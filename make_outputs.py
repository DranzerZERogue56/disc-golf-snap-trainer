"""Builds trainer_assembly.3mf and the steel-arm drawing (svg + pdf), and checks the STLs.
Run after model.py:  python make_outputs.py"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MPoly, FancyArrowPatch
import trimesh

import model as M

HERE = M.OUT

# ---- 3MF: all parts, assembly pose, coloured ----
scene = trimesh.Scene()
for name, (_, rgb) in M.main().items():
    mesh = trimesh.load(os.path.join(HERE, "_parts", name + ".stl"))
    mesh.visual.face_colors = [int(c * 255) for c in rgb] + [255]
    scene.add_geometry(mesh, node_name=name, geom_name=name)
scene.export(os.path.join(HERE, "trainer_assembly.3mf"))

# ---- steel arm drawing, 1:1 on A4 landscape ----
L, W = M.ARM_LEN, M.ARM_W
tipx = L - M.ARM_TIP_HOLE_FROM_END
fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 297); ax.set_ylim(0, 210); ax.set_aspect("equal"); ax.axis("off")
ox, oy = 60, 105                      # pivot hole centre on the sheet
r = W / 2
th = [math.radians(a) for a in range(90, 271, 3)]
pts = [(ox + L - 2, oy + r), (ox + L, oy + r - 2), (ox + L, oy - r + 2), (ox + L - 2, oy - r)]
pts += [(ox + r * math.cos(t), oy + r * math.sin(t)) for t in reversed(th)] if False else []
outline = [(ox + L - 2, oy - r), (ox, oy - r)] + [(ox + r * math.cos(math.radians(a)), oy + r * math.sin(math.radians(a))) for a in range(270, 89, -5)] + [(ox, oy + r), (ox + L - 2, oy + r), (ox + L, oy + r - 2), (ox + L, oy - r + 2)]
ax.add_patch(MPoly(outline, closed=True, fill=False, ec="k", lw=1.5))
d1, d2 = M.BOLT_D + M.CLEAR, M.ARM_TIP_HOLE_D
ax.add_patch(Circle((ox, oy), d1 / 2, fill=False, ec="k", lw=1.2))
ax.add_patch(Circle((tipx + ox, oy), d2 / 2, fill=False, ec="k", lw=1.2))
for cx in (ox, tipx + ox):            # centre marks
    ax.plot([cx - 5, cx + 5], [oy, oy], "k-.", lw=0.5); ax.plot([cx, cx], [oy - 5, oy + 5], "k-.", lw=0.5)


def dim_h(x0, x1, y, txt, off=0):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<->", mutation_scale=8, lw=0.8))
    ax.text((x0 + x1) / 2, y + 1.8 + off, txt, ha="center", fontsize=8)
    for x in (x0, x1):
        ax.plot([x, x], [oy + r + 1 if y > oy else oy - r - 1, y + (1 if y > oy else -1)], "k-", lw=0.4)


def dim_v(x, y0, y1, txt):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="<->", mutation_scale=8, lw=0.8))
    ax.text(x + 2, (y0 + y1) / 2, txt, fontsize=8, va="center")


dim_h(ox - r, ox + L, oy + r + 12, f"{L + r:.0f} overall length of blank")
dim_h(ox, ox + L, oy + r + 32, f"{L:.0f} pivot centre to tip")
dim_h(ox, ox + tipx, oy + r + 22, f"{tipx:.0f} pivot centre to tip-hole centre")
dim_v(ox + L + 8, oy - r, oy + r, f"{W:.0f} wide")
ax.text(ox + 6, oy - r - 8, f"Ø{d1:.1f} pivot hole (M6 + 0.3 clearance)", fontsize=8)
ax.text(ox + tipx - 55, oy - r - 16, f"Ø{d2:.1f} tip hole ({M.ARM_TIP_HOLE_FROM_END:.0f} from end)", fontsize=8)
ax.text(ox - 10, oy - r - 16, f"R{r:.0f} full round at pivot end", fontsize=8)
ax.text(ox + L - 30, oy - r - 24, "tip corners R2", fontsize=8)
ax.text(15, 190, "SNAP TRAINER - STEEL ARM (cut from flat bar)", fontsize=13, weight="bold")
ax.text(15, 180, f"Material: flat steel bar {M.ARM_W:.0f} x {M.ARM_T:.0f} mm (mild steel / stainless). Length of blank: {L + r:.0f} mm.", fontsize=9)
ax.text(15, 173, "Drawn 1:1 on A4 landscape - print at 100% / 'actual size' to use as a template. Dimensions in mm.", fontsize=9)
ax.text(15, 166, "Deburr all edges. Hole tolerance as drawn; do not enlarge the pivot hole (0.3 mm clearance is deliberate).", fontsize=9)
ax.text(15, 40, "Side view: bar thickness %.0f mm. Both holes drilled straight through the %.0f mm face." % (M.ARM_T, M.ARM_T), fontsize=9)
ax.add_patch(plt.Rectangle((ox, 20), L, M.ARM_T, fill=False, ec="k", lw=1.2))
dim_v(ox + L + 8, 20, 20 + M.ARM_T, "%.0f" % M.ARM_T)
fig.savefig(os.path.join(HERE, "arm_steel_drawing.svg"))
fig.savefig(os.path.join(HERE, "arm_steel_drawing.pdf"))

# ---- STL checks ----
print("--- STL checks ---")
ok = True
for f in ["grip", "weight", "weight_lid", "arm_printed", "grip_for_printed_arm", "weight_for_printed_arm"]:
    m = trimesh.load(os.path.join(HERE, f + ".stl"))
    ext = m.bounds[1] - m.bounds[0]
    print(f"{f:24s} watertight={m.is_watertight} winding={m.is_winding_consistent} vol={m.volume/1000:.1f}cm3 "
          f"bbox={ext[0]:.1f}x{ext[1]:.1f}x{ext[2]:.1f} zmin={m.bounds[0][2]:.2f} faces={len(m.faces)}")
    ok &= m.is_watertight
print("3MF reload:", [(k, g.is_watertight) for k, g in trimesh.load(os.path.join(HERE, "trainer_assembly.3mf")).geometry.items()])
print("ALL WATERTIGHT:", ok)
