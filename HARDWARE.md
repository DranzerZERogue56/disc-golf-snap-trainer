# Hardware and material options (everything that is not 3D printed)

The default build is in the README. This lists the alternatives. If a part differs from the default,
check the "Change in `model.py`" column: some options change a dimension and need a rebuild.

## Bolt (pivot)

| Option | Fits as-is? | Change in `model.py` |
|---|---|---|
| **M6 x 20 button head, ISO 7380 (default)**, 4 mm hex key | Yes | none |
| M6 x 20 flanged button head | Yes, and the flange can replace the washer | optionally `WASHER_T = 0` |
| M6 hex head (DIN 933), 10 mm across flats | Head is taller, so the step gets deeper | `BOLT_HEAD_D = 11.5`, `BOLT_HEAD_H = 4.0` |
| M6 socket cap (DIN 912) | Taller again | `BOLT_HEAD_D = 10.0`, `BOLT_HEAD_H = 6.0` |
| Shoulder bolt (M6 thread, 8 mm shoulder) | Best pivot: the arm turns on the smooth shoulder and cannot be pinched | not modelled; enlarge the arm hole to the shoulder diameter + 0.3 |

The script picks the longest standard length that does not poke out of the bed face (20 mm by default).
Stainless is fine; zinc-plated steel is the cheapest.

## Nut

| Option | Notes |
|---|---|
| **M6 nylock, DIN 985, 8 mm tall, 10 mm across flats (default)** | Sits in the hex pocket, held captive. The bolt should poke 0.5 mm through |
| M6 full-height nylock (DIN 982, 10 mm tall) | Set `NUT_H = 10.0`; the pocket is made deeper automatically |
| Plain M6 nut + removable (blue) thread locker | Works; tighten snug, then back off |
| Two plain M6 nuts (jam nuts) | Works if you cannot get nylocks; stack height about 10 mm, so set `NUT_H = 10.0` |

## Washer

M6 flat washer, 12 mm OD x 1.6 mm (the thin ISO 7089 / "form A" size). The model uses these numbers.
A washer up to about 16 mm OD also fits the slot. A PTFE or nylon washer between the arm and the grip floor gives a smoother swing.

## Arm

| Option | Notes |
|---|---|
| **Mild steel flat bar 20 x 3 mm (default)** | Cheapest. Paint or oil it against rust |
| Stainless steel flat bar 20 x 3 mm | No rust, a little harder to drill (cutting oil, slow speed) |
| Aluminium flat bar 20 x 3 mm | Easy to cut, but bends more under a hard snap; prefer 4 mm (set `ARM_T = 4.0`) |
| Steel 4 mm thick | Stiffer, heavier; set `ARM_T = 4.0` and rebuild so the slot and tunnel match |
| **Printed arm** (`arm_printed.stl`, 5 mm PETG) | Stand-in only, weaker. Use with the `*_for_printed_arm.stl` files |

Cut to a 101 mm blank, round the pivot end to R10, drill the 6.3 and 4.3 mm holes, deburr. See `arm_steel_drawing.pdf` (1:1 on A4).
A metal supplier or workshop can cut and drill it from the drawing.

## Weight filler (the cup holds about 14.6 cm3)

| Filler | Approx. mass for a full cup | Notes |
|---|---|---|
| Steel shot / BBs | 60-70 g | Cheap, easy to pour, the best choice |
| Steel washers or nuts | 60-75 g | Stack them in, fill gaps with epoxy |
| Coins | 60-80 g | Works, a bit fiddly |
| Lead shot | 90-100 g | Heavier but toxic: not recommended for something you hold |
| Tungsten shot | 150 g or more | Expensive; check your wrist is up to it |
| Sand + epoxy | about 40 g | Cheapest and lightest |

Always glue the filler (epoxy or CA) so it cannot rattle or leak. The empty cup and lid are about 23 g of PETG.

## Glue and fasteners

- **Two-part epoxy**: fills the cup, locks the arm tip and holds the lid. Best choice.
- **CA (super) glue**: fine for the lid only.
- **Thread locker**: only needed with plain nuts.
- **M3 screw** (about 28 mm or shorter): optional, for the 3.4 mm hole near the grip's far end.

## Tools

4 mm hex key, 10 mm spanner, hacksaw or angle grinder for the bar, file, drill with 4.3 and 6.3 mm bits, calipers or a ruler.
