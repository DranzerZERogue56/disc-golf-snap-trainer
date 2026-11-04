# Build guide

About one evening of work, plus print time (the grip is the longest print).

## 1. Check the sizes against your hand (recommended)

All sizes are estimates. Before printing, hold a ruler to your hand:
- Grip arc length should be about as long as your palm (default 123 mm).
- Can you wrap your fingers around a 28 mm thick grip comfortably? (default `GRIP_T = 28`)

If not, edit the PARAMETERS block at the top of `model.py` and rebuild (see "Changing the sizes" in the README).
To test cheaply, print only the grip first at 15 % infill.

## 2. Print the parts

Settings: PETG or PLA+, 0.2 mm layers, 4 walls.

| Part | File | Orientation | Infill |
|---|---|---|---|
| Grip | `grip.stl` | as exported: bed face down, step facing up | 30-40 % |
| Weight cup | `weight.stl` | as exported: open side up | 100 %, or about 20 % if filled with shot |
| Weight lid | `weight_lid.stl` | as exported: textured face up | 100 % |
| Printed arm only | `arm_printed.stl` + `grip_for_printed_arm.stl` + `weight_for_printed_arm.stl` | as exported | 100 % |

Notes:
- No supports are needed. The nut pocket (about 12 mm wide) and the arm tunnel in the cup wall (about 20 mm wide) are bridges: print them slowly with full cooling.
- Before gluing anything, test-fit the nut in its pocket and the arm in the tunnel.

## 3. Make the steel arm

1. Print `arm_steel_drawing.pdf` at 100 % ("actual size"). It is 1:1.
2. Cut a 20 x 3 mm steel flat bar to 101 mm.
3. Round the pivot end to R10 (a file is fine) and lightly round the other two corners (R2).
4. Drill the pivot hole 6.3 mm at 10 mm from the rounded end, and the tip hole 4.3 mm at 8 mm from the other end. Use a small pilot hole first.
5. Deburr both faces and all edges. Paint or oil the steel if it is not stainless.

## 4. Assemble the pivot

1. Drop the nylock nut into the hex pocket on the underside of the grip (the face that was on the bed). It should be a snug, captive fit.
2. Lay the arm in the recessed step with the pivot holes lined up.
3. Put the washer on the bolt, then push the bolt down through the arm and the grip into the nut.
4. Tighten with the 4 mm hex key until snug, then back off about a quarter turn so the arm swings freely. The nylon insert holds it.
5. Check that the head sits just below the grip's top face, and that the arm swings from hanging straight down out through about 95 degrees without rubbing.

## 5. Build the weight

1. Slide the arm tip into the tunnel in the cup wall until it rests on the cup floor (the arm reaches about 18 mm past the outer wall).
2. Dry-fit the lid first: it should drop onto its ledge without touching the arm.
3. Mix epoxy and add the filler (steel shot, washers or coins; see `HARDWARE.md`). Get some epoxy into the 4.3 mm hole at the arm tip: this locks the arm in.
4. Fill to about 1 mm below the lid ledge and let the epoxy cure fully (check the pack, often 24 h).
5. Glue the lid onto its ledge, textured face up. The lid face then sits 1.2 mm below the cup rim.

## 6. Try it

Hold the grip like a disc rim with the arm hanging down. Start with small, slow wrist snaps; the weight should swing freely.
If it binds, back the nut off a little more. If the arm bends, use thicker steel (`ARM_T = 4.0`, then rebuild).

## Safety

The weight swings fast and the steel arm has hard edges. Deburr everything, keep the area around you clear, and stop
if anything cracks (check the printed parts around the pivot first).
