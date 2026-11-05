# Disc golf "snap" wrist trainer - personal-use 3D model

An original, parametric design for a 3D-printed disc golf wrist-snap trainer: a curved grip, a pivoting steel arm and a fillable weight. No logos or brand names are on any part.
Everything is parametric: edit the numbers at the top of `model.py`, run the two scripts, done.

**New here?** Start with [BUILD_GUIDE.md](BUILD_GUIDE.md) (step by step) and [HARDWARE.md](HARDWARE.md) (shopping list plus alternative bolts, nuts, arms and weight fillers).

## Files

| File | What it is |
|---|---|
| `trainer_assembly.step` | **The one 3D file**: grip, steel arm, weight cup + lid, bolt, washer, nut, assembled, arm hanging straight down parallel to the grip's left end |
| `trainer_assembly.3mf` | Same assembly (each part a separate coloured object) for slicers |
| `grip.stl` | Grip, printed flat on the bed (bed face down, arm pocket facing up). **Hollow underside**: a 4 mm shell with ribs, not a solid block |
| `weight.stl` | Weight cup, open side up |
| `weight_lid.stl` | Weight lid, textured face up |
| `arm_printed.stl` | Printed stand-in arm (5 mm thick) - **weaker than steel** |
| `grip_for_printed_arm.stl`, `weight_for_printed_arm.stl` | Grip and cup with the slot/tunnel sized for the 5 mm printed arm (use these *with* `arm_printed.stl`) |
| `arm_steel_drawing.svg` / `.pdf` | Flat drawing of the steel arm, 1:1 on A4 landscape, with dimensions and hole positions |
| `preview_top.png`, `preview_34.png`, `preview_exploded.png`, `preview_swing_range.png`, `preview_grip_underside.png` | Blender renders (swing range overlays the arm at 0, 30, 60 and 95 degrees; the underside shot shows the hollow grip and its ribs) |
| `BUILD_GUIDE.md`, `HARDWARE.md` | Build instructions; hardware, material and filler options |
| `model.py` | CadQuery model (all dimensions at the top) |
| `make_outputs.py` | Builds the 3MF + drawing and runs the watertight checks |
| `render_blender.py` | Blender headless renders (reads `_parts/*.stl`) |

## Estimated dimensions (all guesses - measure yours and change them)

These are estimates, scaled against an adult hand (palm ~85 mm wide, fingers 18-20 mm thick).

| Parameter (in `model.py`) | Value | Reasoning |
|---|---|---|
| `GRIP_R_OUT` | 110 mm | Outer arc radius. Arc length is about 123 mm: roughly as long as the palm; the target range is 110-130 mm |
| `GRIP_SWEEP` | 64 deg | Both end faces are radial, about 60-64 deg apart |
| `GRIP_WIDTH` | 50 mm | Radial width of the fan (inner radius 60 mm); a chunky 45-55 mm block fills the hand |
| `GRIP_T` | 28 mm | 25-30 mm thick so it fills the hand; this also leaves room to sink the bolt head |
| `SHELL_WALL` / `TOP_THICK` / `RIB_T` / `RIB_STEP` | 4 / 5 / 3 mm / 8 deg | Hollow-underside shell: set `HOLLOW_UNDERSIDE = False` for a solid grip |
| `RIM_FILLET` | 9 mm | Rounded rim on the outer curve; the bed edge only gets a 0.8 mm chamfer, since a rounded bottom would overhang |
| `PIVOT_FROM_END` / `PIVOT_FROM_RIM` | 14 / 25 mm | Pivot sits near the left end, half-way across the fan |
| `ARM_W` x `ARM_T` | 20 x 3 mm | Standard flat bar |
| `PIVOT_TO_WEIGHT` | 100 mm | Pivot to weight centre; the weight sits in the concave cove below the grip |
| arm length (computed) | 91 mm pivot-to-tip, 101 mm blank | Reaches `ARM_INSERT` = 18 mm into the cup |
| `WEIGHT_D` / `WEIGHT_DEPTH` | 54 / 16 mm | About 0.45x the grip length |
| wall / floor / lid | 4 / 3 / 3 mm | Raised outer rim, lid 1.2 mm below the rim |
| bolt | M6 x 20 button-head (ISO 7380), nylock nut, 12 mm washer | Length is picked automatically; head 10.5 mm dia x 3.3 mm |
| `POCKET_SWING` | 95 deg | Free swing of the arm, from hanging straight down out to slightly past horizontal |
| `CLEAR` / `CLEAR_Z` / `HEX_CLEAR` | 0.3 / 0.4 / 0.4 mm | Pivot hole, arm slot, nut pocket |

Cavity of the weight is about 14.6 cm3, roughly 60-70 g of steel shot, more with a metal filler and epoxy.

## How it goes together

1. The grip has a recessed step (about 8.4 mm deep) where the arm sits, a 6.3 mm pivot hole and a hex nut pocket open on the bed face. The nylock nut is **captive** in that pocket and sits above the bed face. The step is deep enough that the bolt head ends up 0.5 mm **below** the grip face, so nothing digs into the palm.
2. Bolt order from the top: head, washer, arm, then the grip floor, then the nut underneath. **Tighten only until snug, then back off about a quarter turn** so the arm swings freely; the nylock holds it.
3. Slide the arm into the tunnel in the cup wall. It lies on the cup floor. Fill the cup with steel shot, coins or washers, adding epoxy or CA glue so nothing rattles. Epoxy also locks into the 4.3 mm hole near the arm tip. Press the lid onto its ledge and glue it.
4. The small 3.4 mm hole near the far end of the grip is for an M3 screw (stop, lanyard or whatever you like).
5. **Swing range.** The arm hangs straight down (the rest pose; the grip body is the stop on that side) and swings freely outward through 95 degrees, past horizontal, into open air beside the grip end. The pocket is cut to that sweep, so the left end of the grip is open. `preview_swing_range.png` shows the arm at 0, 30, 60 and 95 degrees. `model.py` sweeps the arm and weight through 0-95 degrees and reports the overlap with the grip, bolt, washer and nut at each step: all 0.000 mm^3. Swinging the other way, or beyond about 97 degrees, hits the pocket wall, as expected.

## Print settings

- PETG or PLA+, 0.2 mm layers, 4 walls (>= 1.6 mm).
- **Grip:** the underside is hollow (4 mm outer wall, 3 mm radial and ring ribs standing on the bed, 5 mm top skin, solid bosses round the nut pocket and screw hole), so it is light and rim-shaped, about 71 cm3 of plastic instead of 122. 15-20 % infill is plenty; walls and ribs carry the load. No supports: the roof only bridges the 13-20 mm cells between ribs. The hex pocket bridges about 12 mm; if it sags, use a sacrificial layer or a slightly slower first bridge.
- **Weight cup:** 100 % infill, or ~20 % if you fill it with shot. The arm tunnel bridges about 20 mm: slow that bridge and use full cooling. Do not use supports inside the tunnel.
- **Lid:** 100 % infill, textured face up.
- **Printed arm:** a stand-in only. 5 mm of PETG or PLA bends and snaps far sooner than 3 mm steel. Use 100 % infill, orient flat as exported, and expect it to break if you really snap hard.

## Hardware list

- M6 x 20 button-head socket bolt (ISO 7380, 4 mm hex key); a flanged button head also works
- M6 nylock nut (DIN 985, height 8 mm)
- 1 x M6 washer (12 mm OD)
- Steel flat bar 20 x 3 mm, ~101 mm blank (see `arm_steel_drawing.pdf`)
- Steel shot, coins or washers for the weight, plus epoxy or CA glue
- Optional: M3 screw for the small hole in the grip

## Changing the sizes

1. Edit the PARAMETERS block at the top of `model.py` (everything is in mm).
2. Rebuild:
   ```
   pip install --user cadquery trimesh matplotlib shapely
   python make_outputs.py                       # rebuilds STEP, STLs, 3MF, drawing, checks
   ARM_MODE=printed python model.py             # (optional) regenerates the *_for_printed_arm files
   "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python render_blender.py
   ```
   On Windows PowerShell, set the variable first: `$env:ARM_MODE = "printed"`.
3. `model.py` prints an interference check for each pair of parts; all should read 0.000 mm^3.

## Checks that were run

- All STLs: `trimesh.is_watertight` = True, consistent winding; the 3MF reloads with every part watertight.
- No overlap between any two parts in the assembly, and none at 0, 15, 30 ... 90 and 95 degrees of arm swing (all 0.000 mm^3).
- Not done: a full Cura slice. The CLI engine needed more machine definition files than I could supply, so open the STLs in Cura yourself to confirm.

## License

MIT: anyone may use, copy, modify, print, sell or share this design. See [LICENSE](LICENSE). The design is provided as is, with no warranty: you build and use it at your own risk.
