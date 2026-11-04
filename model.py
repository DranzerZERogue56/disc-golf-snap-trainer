"""Disc golf "snap" wrist trainer - parametric CadQuery model.

Run:  python model.py            (writes STEP / STL / 3MF / SVG / PDF into ./)

Everything you may want to change is in the PARAMETERS block. All lengths in mm.
Top-view coordinates: X right, Y up, Z up. The arc centre of the grip is the origin.
Parts: GRIP, ARM, WEIGHT (cup + lid).
"""
import math
import os

import cadquery as cq
from shapely import affinity
from shapely.geometry import Point, box
from shapely.ops import unary_union

# ============================ PARAMETERS =====================================
# --- grip (printed) ---
GRIP_R_OUT = 110.0      # outer (rim) arc radius
GRIP_WIDTH = 50.0       # radial width of the fan (outer radius - inner radius)
GRIP_SWEEP = 64.0       # sweep angle of the fan, degrees  (arc length ~ 123 mm)
GRIP_T = 28.0           # thickness = height of the grip (chunky, fills the hand)
RIM_FILLET = 9.0        # rounding of the outer top edge (the "disc rim")
INNER_FILLET = 3.0      # rounding of the concave inner top edge
BOTTOM_CHAMFER = 0.8    # chamfer on the bed-side edge (avoids elephant foot)
PIVOT_FROM_END = 14.0   # pivot hole centre distance from the grip's end face
PIVOT_FROM_RIM = 25.0   # pivot hole centre distance inward from the outer rim
POCKET_SWING = 95.0     # free arm swing (deg) from the hanging pose, outward past the grip end
SCREW_D = 3.4           # small screw hole near the far end (M3 clearance)
SCREW_FROM_END = 14.0   # that hole's distance from the far end face

# --- arm ---
ARM_MODE = os.environ.get("ARM_MODE", "steel")  # "steel" or "printed" - which arm the slots are sized for
ARM_W = 20.0            # arm width (flat bar width)
ARM_T = 3.0             # steel bar thickness
ARM_PRINT_T = 5.0       # thickness of the printed stand-in arm (thicker = stiffer, still weaker)
PIVOT_TO_WEIGHT = 100.0 # pivot hole centre to weight centre
ARM_INSERT = 18.0       # how far the arm tip reaches in past the weight's outer wall
ARM_TIP_HOLE_D = 4.3    # hole near the arm tip (epoxy / shot locks into it)
ARM_TIP_HOLE_FROM_END = 8.0

# --- weight (printed cup + lid) ---
WEIGHT_D = 54.0         # outer diameter
WEIGHT_DEPTH = 16.0     # total height of the cup
WEIGHT_WALL = 4.0       # side wall
WEIGHT_FLOOR = 3.0      # closed bottom
LID_T = 3.0             # lid thickness
LID_LEDGE = 1.2         # ledge the lid rests on (lid is this much wider than the cavity)
LID_RIM_STEP = 1.2      # lid top sits this far below the cup rim -> "raised outer rim"
LID_RECESS_D = 0.6      # depth of the recessed textured face
LID_RECESS_R = 20.0     # radius of the recessed face
TEX_PITCH = 1.8         # crosshatch texture pitch
TEX_GROOVE_W = 0.6
TEX_GROOVE_D = 0.4

# --- hardware (M6) ---
BOLT_D = 6.0
BOLT_HEAD_D = 10.5      # button-head bolt (ISO 7380): dome head
BOLT_HEAD_H = 3.3
HEAD_SINK = 0.5         # head top sits this far below the grip face
NUT_AF = 10.0           # across flats of the nut
NUT_H = 8.0             # nylock nut height (DIN 985)
WASHER_OD = 12.0
WASHER_T = 1.6
STD_BOLT_LENGTHS = [16, 20, 25, 30, 35, 40]

# --- clearances ---
CLEAR = 0.3             # pivot hole + arm slot clearance (per side / diametral for holes)
CLEAR_Z = 0.4           # extra height above the arm in slots
HEX_CLEAR = 0.4         # added to the nut across-flats for the captive pocket
# =============================================================================

OUT = os.path.dirname(os.path.abspath(__file__))
R_IN = GRIP_R_OUT - GRIP_WIDTH
ARM_THICK = ARM_T if ARM_MODE == "steel" else ARM_PRINT_T


def pol(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def ac(af):  # across corners of a hexagon
    return af / math.cos(math.radians(30))


def arcs_at(wp, z, radius, tol=0.2):
    return [e for e in wp.val().Edges()
            if e.geomType() == "CIRCLE" and abs(e.radius() - radius) < tol
            and abs(e.startPoint().z - z) < 1e-3 and abs(e.endPoint().z - z) < 1e-3]


# ---- layout (all in plan view) ----
A_LEFT = 90.0                          # left end face is vertical in the top view
A_RIGHT = A_LEFT - GRIP_SWEEP
A_MID = (A_LEFT + A_RIGHT) / 2
R_PIV = GRIP_R_OUT - PIVOT_FROM_RIM
# pivot: PIVOT_FROM_END away from the left end face, measured along the arc
PIVOT_ANGLE = A_LEFT - math.degrees(math.asin(PIVOT_FROM_END / R_PIV))
PIVOT = pol(R_PIV, PIVOT_ANGLE)
ARM_ANGLE = A_LEFT + 180                # rest pose: arm hangs straight down, parallel to the left end face
ARM_DIR = pol(1, ARM_ANGLE)
WEIGHT_C = (PIVOT[0] + ARM_DIR[0] * PIVOT_TO_WEIGHT, PIVOT[1] + ARM_DIR[1] * PIVOT_TO_WEIGHT)
WEIGHT_R = WEIGHT_D / 2
ARM_LEN = PIVOT_TO_WEIGHT - WEIGHT_R + ARM_INSERT   # pivot centre -> tip
ARM_END_R = ARM_W / 2

SLOT_DEPTH = ARM_THICK + WASHER_T + BOLT_HEAD_H + HEAD_SINK   # head ends up below the grip face
Z_FLOOR = GRIP_T - SLOT_DEPTH           # arm lies on this level
HEAD_BOTTOM_Z = Z_FLOOR + ARM_THICK + WASHER_T
BOLT_LEN = max(l for l in STD_BOLT_LENGTHS if HEAD_BOTTOM_Z - l >= 0)
BOLT_TIP_Z = HEAD_BOTTOM_Z - BOLT_LEN
NUT_BOTTOM_Z = BOLT_TIP_Z + 0.5          # bolt pokes 0.5 mm through the nut
NUT_POCKET_H = NUT_BOTTOM_Z + NUT_H      # nut rests against the pocket ceiling


def build_grip():
    a0, a1 = A_RIGHT, A_LEFT
    g = (cq.Workplane("XY").moveTo(*pol(GRIP_R_OUT, a0))
         .threePointArc(pol(GRIP_R_OUT, A_MID), pol(GRIP_R_OUT, a1))
         .lineTo(*pol(R_IN, a1))
         .threePointArc(pol(R_IN, A_MID), pol(R_IN, a0)).close().extrude(GRIP_T))
    g = g.faces("<Z").edges().chamfer(BOTTOM_CHAMFER)
    g = g.newObject(arcs_at(g, GRIP_T, GRIP_R_OUT)).fillet(RIM_FILLET)
    g = g.newObject(arcs_at(g, GRIP_T, R_IN)).fillet(INNER_FILLET)

    # arm pocket: slot for the arm, plus the swing range, round end around the pivot
    hw = ARM_W / 2 + CLEAR
    shapes = [Point(PIVOT).buffer(hw, 32)]
    n = max(1, int(POCKET_SWING))
    for i in range(n + 1):
        ang = ARM_ANGLE - POCKET_SWING * i / n
        r = box(0, -hw, 200, hw)
        r = affinity.rotate(r, ang, origin=(0, 0))
        shapes.append(affinity.translate(r, *PIVOT))
    poly = unary_union(shapes)
    pts = [(x, y) for x, y in poly.exterior.coords][:-1]
    pocket = cq.Workplane("XY").workplane(offset=Z_FLOOR).polyline(pts).close().extrude(SLOT_DEPTH + 1)
    g = g.cut(pocket)

    # pivot hole + captive hex nut pocket (open on the bed face, bolt head sits on top)
    g = g.cut(cq.Workplane("XY").center(*PIVOT).circle((BOLT_D + CLEAR) / 2).extrude(GRIP_T + 1))
    hexp = (cq.Workplane("XY").center(*PIVOT).polygon(6, ac(NUT_AF + HEX_CLEAR))
            .extrude(NUT_POCKET_H))
    g = g.cut(hexp)

    # small screw hole near the far (right) end
    ang = A_RIGHT + math.degrees(math.asin(SCREW_FROM_END / (GRIP_R_OUT - GRIP_WIDTH / 2)))
    sp = pol(GRIP_R_OUT - GRIP_WIDTH / 2, ang)
    g = g.cut(cq.Workplane("XY").center(*sp).circle(SCREW_D / 2).extrude(GRIP_T + 1))
    return g


def arm_profile(thick):
    """Arm in local coords: pivot at the origin, tip along +X, lying on Z=0."""
    L = ARM_LEN
    a = (cq.Workplane("XY").moveTo(0, -ARM_END_R).lineTo(L - 2, -ARM_END_R)
         .threePointArc((L - 2 + 2 * math.sin(math.pi / 4), -ARM_END_R + 2 - 2 * math.cos(math.pi / 4)), (L, -ARM_END_R + 2))
         .lineTo(L, ARM_END_R - 2)
         .threePointArc((L - 2 + 2 * math.sin(math.pi / 4), ARM_END_R - 2 + 2 * math.cos(math.pi / 4)), (L - 2, ARM_END_R))
         .lineTo(0, ARM_END_R)
         .threePointArc((-ARM_END_R, 0), (0, -ARM_END_R)).close().extrude(thick))
    a = a.cut(cq.Workplane("XY").circle((BOLT_D + CLEAR) / 2).extrude(thick))
    a = a.cut(cq.Workplane("XY").center(L - ARM_TIP_HOLE_FROM_END, 0).circle(ARM_TIP_HOLE_D / 2).extrude(thick))
    return a


def build_weight():
    """Cup in local coords: centre at origin, arm enters from the -X side, Z=0 on the bed."""
    R = WEIGHT_R
    cup = cq.Workplane("XY").circle(R).extrude(WEIGHT_DEPTH)
    cup = cup.faces("<Z").edges().chamfer(BOTTOM_CHAMFER)
    cup = cup.faces(">Z").edges().fillet(0.8)
    cav_r = R - WEIGHT_WALL
    cup = cup.cut(cq.Workplane("XY").workplane(offset=WEIGHT_FLOOR).circle(cav_r).extrude(WEIGHT_DEPTH))
    ledge_z = WEIGHT_DEPTH - LID_RIM_STEP - LID_T
    cup = cup.cut(cq.Workplane("XY").workplane(offset=ledge_z).circle(cav_r + LID_LEDGE + 0.15)
                  .extrude(WEIGHT_DEPTH))
    # tunnel for the arm through the wall (arm rests on the cavity floor)
    hw = ARM_W / 2 + CLEAR
    x0, x1 = -(R + 1), -(cav_r - 4.0)   # from outside, through the wall, into the cavity
    tun = (cq.Workplane("XY").workplane(offset=WEIGHT_FLOOR).center((x0 + x1) / 2, 0)
           .rect(x1 - x0, 2 * hw).extrude(ARM_THICK + CLEAR_Z))
    cup = cup.cut(tun)
    return cup


def build_lid():
    r = WEIGHT_R - WEIGHT_WALL + LID_LEDGE
    lid = cq.Workplane("XY").circle(r).extrude(LID_T)
    lid = lid.faces("<Z").edges().chamfer(0.4)
    top = LID_T
    lid = lid.cut(cq.Workplane("XY").workplane(offset=top - LID_RECESS_D).circle(LID_RECESS_R).extrude(5))
    # crosshatch grooves in the recessed face
    span = LID_RECESS_R
    n = int(span / TEX_PITCH)
    zb = top - LID_RECESS_D - TEX_GROOVE_D
    circ = cq.Workplane("XY").workplane(offset=zb).circle(LID_RECESS_R - 1.0).extrude(TEX_GROOVE_D + 1)
    for horiz in (True, False):
        pts = [((0, i * TEX_PITCH) if horiz else (i * TEX_PITCH, 0)) for i in range(-n, n + 1)]
        wh = (2 * span, TEX_GROOVE_W) if horiz else (TEX_GROOVE_W, 2 * span)
        bars = (cq.Workplane("XY").workplane(offset=zb).pushPoints(pts).rect(*wh)
                .extrude(TEX_GROOVE_D + 1))
        lid = lid.cut(bars.intersect(circ))
    return lid


def hex_prism(af, h, hole_d=None):
    s = cq.Workplane("XY").polygon(6, ac(af)).extrude(h)
    if hole_d:
        s = s.cut(cq.Workplane("XY").circle(hole_d / 2).extrude(h))
    return s


def build_hardware():
    z_head = HEAD_BOTTOM_Z
    head = cq.Workplane("XY").circle(BOLT_HEAD_D / 2).extrude(BOLT_HEAD_H).edges(">Z").fillet(1.4)
    head = head.cut(cq.Workplane("XY").workplane(offset=BOLT_HEAD_H - 2).polygon(6, ac(4.0)).extrude(3))
    bolt = (head.translate((0, 0, z_head))
            .union(cq.Workplane("XY").circle(BOLT_D / 2).extrude(BOLT_LEN).translate((0, 0, BOLT_TIP_Z))))
    washer = (cq.Workplane("XY").circle(WASHER_OD / 2).circle((BOLT_D + 0.4) / 2).extrude(WASHER_T)
              .translate((0, 0, Z_FLOOR + ARM_THICK)))
    nut = hex_prism(NUT_AF, NUT_H, BOLT_D).translate((0, 0, NUT_BOTTOM_Z))
    mv = lambda s: s.translate((PIVOT[0], PIVOT[1], 0))
    return mv(bolt), mv(washer), mv(nut)


def place_arm(arm):
    return arm.rotate((0, 0, 0), (0, 0, 1), ARM_ANGLE).translate((PIVOT[0], PIVOT[1], Z_FLOOR))


def place_weight(w):
    return w.rotate((0, 0, 0), (0, 0, 1), ARM_ANGLE).translate((WEIGHT_C[0], WEIGHT_C[1], Z_FLOOR - WEIGHT_FLOOR))


def lid_place(l):
    return l.rotate((0, 0, 0), (0, 0, 1), ARM_ANGLE).translate(
        (WEIGHT_C[0], WEIGHT_C[1], Z_FLOOR - WEIGHT_FLOOR + WEIGHT_DEPTH - LID_RIM_STEP - LID_T))


def stl(shape, name, tol=0.02):
    cq.exporters.export(shape, os.path.join(OUT, name), tolerance=tol, angularTolerance=0.1)


def main():
    grip, cup, lid = build_grip(), build_weight(), build_lid()
    arm_steel = arm_profile(ARM_T)
    arm_print = arm_profile(ARM_PRINT_T)
    bolt, washer, nut = build_hardware()

    parts = {  # name -> (shape in assembly position, rgb)
        "grip": (grip, (0.10, 0.10, 0.11)),
        "arm": (place_arm(arm_steel if ARM_MODE == "steel" else arm_print), (0.72, 0.72, 0.75)),
        "weight_cup": (place_weight(cup), (0.10, 0.10, 0.11)),
        "weight_lid": (lid_place(lid), (0.22, 0.22, 0.24)),
        "bolt": (bolt, (0.55, 0.55, 0.58)),
        "washer": (washer, (0.65, 0.65, 0.68)),
        "nut": (nut, (0.15, 0.2, 0.55)),
    }

    # --- print files (flat on the bed) ---
    sfx = "" if ARM_MODE == "steel" else "_for_printed_arm"
    stl(grip, f"grip{sfx}.stl")
    stl(cup, f"weight{sfx}.stl")
    stl(lid, "weight_lid.stl")
    stl(arm_print, "arm_printed.stl")

    # --- assembly STEP ---
    if ARM_MODE != "steel":      # only the slot-sized print files differ for the printed arm
        return parts
    assy = cq.Assembly(name="snap_trainer")
    for name, (shape, rgb) in parts.items():
        assy.add(shape, name=name, color=cq.Color(*rgb, 1.0))
    assy.save(os.path.join(OUT, "trainer_assembly.step"))

    # --- per-part meshes for renders / 3MF (assembly pose) ---
    mesh_dir = os.path.join(OUT, "_parts")
    os.makedirs(mesh_dir, exist_ok=True)
    for name, (shape, rgb) in parts.items():
        cq.exporters.export(shape, os.path.join(mesh_dir, f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)

    # --- interference check between parts that must not overlap ---
    def vol(a, b):
        try:
            return a.intersect(b).val().Volume()
        except Exception:
            return 0.0
    pairs = [("grip", "arm"), ("grip", "bolt"), ("grip", "nut"), ("arm", "weight_cup"),
             ("arm", "bolt"), ("grip", "weight_cup"), ("weight_cup", "weight_lid"), ("grip", "washer")]
    for a, b in pairs:
        print(f"interference {a}/{b}: {vol(parts[a][0], parts[b][0]):.3f} mm^3")

    # --- swing sweep: arm + weight rotated about the pivot, checked against everything fixed ---
    def bb_overlap(a, b):
        p, q = a.val().BoundingBox(), b.val().BoundingBox()
        return not (p.xmax < q.xmin or q.xmax < p.xmin or p.ymax < q.ymin or q.ymax < p.ymin
                    or p.zmax < q.zmin or q.zmax < p.zmin)
    swing_ok = True
    steps = sorted(set([0, 15, 30, 45, 60, 75, 90, POCKET_SWING]))
    for d in steps:
        worst = 0.0
        for mv in ("arm", "weight_cup", "weight_lid"):
            moved = parts[mv][0].rotate((PIVOT[0], PIVOT[1], 0), (PIVOT[0], PIVOT[1], 1), -d)
            for fx in ("grip", "bolt", "washer", "nut"):
                if bb_overlap(moved, parts[fx][0]):
                    worst = max(worst, vol(moved, parts[fx][0]))
        swing_ok &= worst < 0.01
        print(f"swing {d:5.1f} deg (arm heading {ARM_ANGLE - d:6.1f}): max overlap {worst:.3f} mm^3")
    print("SWING CLEAR:", swing_ok)
    import json
    json.dump(dict(pivot=PIVOT, arm_angle=ARM_ANGLE, swing=POCKET_SWING), open(os.path.join(mesh_dir, "info.json"), "w"))

    info = dict(R_IN=R_IN, PIVOT=PIVOT, WEIGHT_C=WEIGHT_C, ARM_LEN=ARM_LEN, ARM_ANGLE=ARM_ANGLE,
                Z_FLOOR=Z_FLOOR, BOLT_LEN=BOLT_LEN, BOLT_TIP_Z=BOLT_TIP_Z, cavity_cc=None)
    cav_r = WEIGHT_R - WEIGHT_WALL
    info["cavity_cc"] = math.pi * cav_r ** 2 * (WEIGHT_DEPTH - LID_RIM_STEP - LID_T - WEIGHT_FLOOR) / 1000
    for k, v in info.items():
        print(k, v)
    return parts


if __name__ == "__main__":
    main()
