"""Draws preview_grip_section.png: cut through the grip's middle, radial direction vs height."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
import model as M

m = trimesh.load("grip.stl")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
for ax, (title, ang, at) in zip(axes, [("Through the open cavity (middle of the grip)", M.A_MID, None),
                                         ("Through the arm pad (pivot end)", M.PIVOT_ANGLE, None)]):
    a = math.radians(ang)
    sec = m.section(plane_origin=[0, 0, 0], plane_normal=[-math.sin(a), math.cos(a), 0])
    for ent in sec.entities:
        pts = sec.vertices[ent.points]
        r = pts[:, 0] * math.cos(a) + pts[:, 1] * math.sin(a)      # radial distance from the arc centre
        ax.fill(r, pts[:, 2], color="#555", alpha=0.85) if len(pts) > 3 else None
        ax.plot(r, pts[:, 2], "k", lw=1)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("radius from arc centre (mm)  -  inner curve left, outer rim right")
    ax.set_ylabel("height (mm)")
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.axhline(0, color="r", lw=0.8); ax.text(M.R_IN - 3, 1, "print bed", color="r", fontsize=8)
fig.suptitle("Grip cross-sections: flat top plate, deep rounded lip on the outer curve (right)")
fig.tight_layout()
fig.savefig("preview_grip_section.png", dpi=110)
