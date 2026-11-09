# Max volumetric flow tests

How the `filament_max_volumetric_speed` caps in this repository were found (or estimated), what goes wrong, and the results so far.

## Method (OrcaSlicer "Max flowrate" tower)

1. Calibration menu -> Flow rate -> **Max flowrate**. It prints a spiral-vase tower whose volumetric flow rises with height
   (about `start + step x z` mm3/s, roughly 14 + z with the default start/step, so a 40 mm tower reaches about 54 mm3/s).
2. Slice with the filament under test and the nozzle that will be used. Read the flow at the height where the wall first goes wrong
   (rough, gaps, under-extrusion, extruder clicking) and keep a **safety margin of 10-15 %** below the last clean height.
3. Test at the temperature you intend to print with. Flow capacity rises roughly with temperature, so a cap measured at 255 C is not valid at 230 C.

The test object's layer height and line width come from the nozzle (0.32 mm layer / 0.7 mm width on a 0.4 nozzle), not from the process
preset you pick.

## What can silently ruin a run

| Problem | Symptom | Fix |
|---|---|---|
| Filament preset cap lower than the test range | Flow flattens at the cap, no ramp | Test with a copy of the filament preset with cap 100 (see `slicers/orcaslicer/flowtest/filament`) |
| Layer-time slowdown / fan slowdown | Speed drops on small layers, ramp flattens | Turn `slow_down_for_layer_cooling` off in the test copy |
| Process sets a wall filament (`wall_filament`) | Test prints with another tool than intended | Use a process whose filament ids are 1 (`flowtest/process`) |
| `M574 ... F<x>` in the INDX start G-code | See below | Check the first lines of the G-code before printing |
| Filament blocked at the spool | Extruder clicks / grinds during the first lines | Check the spool path; a clog or tangle looks exactly like "flow too high" |

### The INDX `M574` line

The INDX start G-code contains `M574 S<n> V35 T<temp> F<x>` for the active tool. Observed values were consistent with
`F = min(perimeter_flow_rate, filament_max_volumetric_speed) / 2.405`, where 2.405 mm2 is the 1.75 mm filament cross-section and
`perimeter_flow_rate = outer_wall_speed x (h x (w - h) + pi x (h/2)^2)`, using the **process-level** layer height and outer wall width.
Examples: F11.6411 = 28 / 2.405; F24.2277 with cap 100 on a 0.6 / 1.1 / 100 mm/s vase process; F6.76977 on a 0.2 mm Balanced process at 200 mm/s
with 0.45 mm width.

M574 is not publicly documented and it is **not known whether firmware 8.0.0 enforces F as a hard limit**. For flow tests the repository's
approach was to patch the generated G-code (`M574 S0 V35 T255 F16`, i.e. 16 x 2.405 = 38 mm3/s) rather than assume either way. If a tower
flattens at a suspiciously low height, check this line first.

## Results

### Sunlu High Speed Matte PETG, T1 (0.4 HF), 0.2 mm Balanced process, F patched to 16

* Tower at **255 C** printed clean up to about **34.9 mm3/s** (top of the tower; no under-extrusion, no clicking after the spool blockage was cleared).
* Appearance improved towards the top (faster = better), i.e. the temperature is high for the slow lower part.
* Spool label bands (Chinese supplier, barcode 01550619A): 230-240 C @ 50-100 mm/s, 240-255 C @ 100-300 mm/s, 255-270 C @ 300-600 mm/s, bed 70-80 C.
* Result: profile set to **250 C / 245 C first layer, cap 30 mm3/s** (about 15 % margin below the 34.9 clean point, one step lower in temperature).
  Not yet verified on a real print at the time of writing.

A first attempt used a 0.6 mm vase process on the 0.4 nozzle and was abandoned: a layer/width the nozzle cannot supply, and the process also forced a different tool.

### T8 (1.0 HF), TriColor Silk PLA

* At 215 C the tower was clean up to at least **40.8 mm3/s**; the profile uses **cap 35**. Other T8 caps (PETG: 25 / 10 / 30) are estimates, **not tested**.

### Estimates (not printed)

Caps for filaments that were not flow-tested were estimated from similar Prusa presets, spool labels and published data, and kept
conservative. They are labelled as estimates in each preset's notes.

## Pressure advance for the 1.0 mm nozzle

Pressure advance values for T8 were scaled from the 0.4 HF value: x 0.447 (the ratio Prusa applies to PETG going from 0.4 to 0.8) and then
x 0.69 for 0.8 -> 1.0 (taken from the CF precedent, 0.016 -> 0.011). They are starting points; run a PA test before trusting them.
