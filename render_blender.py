"""Blender headless renderer: blender --background --python render_blender.py
Renders preview_top.png, preview_34.png, preview_exploded.png from _parts/*.stl."""
import json
import math
import os

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
COLORS = {"grip": (0.06, 0.06, 0.07), "arm": (0.62, 0.62, 0.65), "weight_cup": (0.06, 0.06, 0.07),
          "weight_lid": (0.12, 0.12, 0.13), "bolt": (0.5, 0.5, 0.55), "washer": (0.7, 0.7, 0.72),
          "nut": (0.08, 0.12, 0.45)}
METAL = {"arm", "bolt", "washer"}
EXPLODE = {"grip": (0, 0, 0), "arm": (0, 0, 28), "bolt": (0, 0, 58), "washer": (0, 0, 44),
           "nut": (0, 0, -30), "weight_cup": (0, 0, -10), "weight_lid": (0, 0, 40)}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.device = "CPU"
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def load(offsets):
    objs = {}
    for name, col in COLORS.items():
        bpy.ops.wm.stl_import(filepath=os.path.join(HERE, "_parts", name + ".stl"))
        o = bpy.context.selected_objects[0]
        o.name = name
        o.location = Vector(offsets.get(name, (0, 0, 0)))
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*col, 1)
        b.inputs["Metallic"].default_value = 0.15 if name in METAL else 0.0
        b.inputs["Roughness"].default_value = 0.85 if name in METAL else 0.45
        o.data.materials.append(m)
        bpy.ops.object.shade_smooth()
        objs[name] = o
    return objs


def add_light(loc, energy, size=150):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.data.energy = energy
    l.data.size = size
    l.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, ortho=None, lens=50):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        c.data.type = "ORTHO"
        c.data.ortho_scale = ortho
    else:
        c.data.lens = lens
    bpy.context.scene.camera = c


def render(name):
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = 1000
    sc.render.filepath = os.path.join(HERE, name)
    bpy.ops.render.render(write_still=True)


def shot(name, offsets, cam, lights=((60, -80, 300), (-200, 150, 250))):
    reset()
    load(offsets)
    add_light(lights[0], 90000, 200)
    add_light(lights[1], 50000, 200)
    cam()
    render(name)


INFO = json.load(open(os.path.join(HERE, "_parts", "info.json")))
PX, PY = INFO["pivot"]


def swing_copies(angles):
    """Ghost copies of arm + weight rotated about the pivot (angles = degrees from the hanging pose)."""
    tints = [(0.9, 0.2, 0.2), (0.95, 0.6, 0.1), (0.2, 0.7, 0.3), (0.2, 0.4, 0.9)]
    for k, d in enumerate(angles):
        for name in ("arm", "weight_cup", "weight_lid"):
            bpy.ops.wm.stl_import(filepath=os.path.join(HERE, "_parts", name + ".stl"))
            o = bpy.context.selected_objects[0]
            o.name = f"{name}_{d}"
            T = Matrix.Translation((PX, PY, 0))
            o.matrix_world = T @ Matrix.Rotation(-math.radians(d), 4, "Z") @ T.inverted()
            m = bpy.data.materials.new(o.name)
            m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Base Color"].default_value = (*tints[k % 4], 1)
            b.inputs["Alpha"].default_value = 0.55
            b.inputs["Roughness"].default_value = 0.5
            o.data.materials.append(m)


# assembled top view (outer arc up, pivot at left)
shot("preview_top.png", {}, lambda: camera((50, 35, 600), (50, 35, 0), ortho=200))
# 3/4 view
shot("preview_34.png", {}, lambda: camera((150, -140, 190), (40, 35, 12), lens=50))
# exploded
shot("preview_exploded.png", EXPLODE, lambda: camera((210, -230, 200), (40, 35, 14), lens=50))

# swing range: arm hanging pose solid, ghosts at 30/60/95 deg
def swing_shot():
    reset()
    load({})
    swing_copies([30, 60, 95])
    add_light((60, -80, 300), 90000, 200)
    add_light((-200, 150, 250), 50000, 200)
    camera((20, 20, 650), (20, 20, 0), ortho=290)
    render("preview_swing_range.png")


swing_shot()


# underside of the grip (bed face): shell, ribs, nut pocket
def underside_shot():
    reset()
    load({"arm": (0, 0, 500), "bolt": (0, 0, 500), "washer": (0, 0, 500), "nut": (0, 0, 500),
          "weight_cup": (0, 0, 500), "weight_lid": (0, 0, 500)})
    add_light((60, 80, -300), 90000, 200)
    add_light((-200, -150, -250), 50000, 200)
    camera((50, 45, -600), (50, 45, 0), ortho=160)
    c = bpy.context.scene.camera
    c.rotation_euler = (math.pi, 0, 0)     # look up the +Z axis, Y up in the image
    render("preview_grip_underside.png")


underside_shot()
