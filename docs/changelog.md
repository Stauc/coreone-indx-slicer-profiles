# Changelog

Newest first. Dates are the working dates of the session in which each change was made.

## 2026-11-18 - Prusa FFF 1.0.24 / PS2 2.5.16 ported, "+ Wiper" dropped from the names

* **PrusaSlicer 3 bundle 1.0.13**, regenerated from Prusa FFF 1.0.24: Prusa's own 0.25 nozzle presets (0.07 / 0.10 / 0.15 mm) and 0.25 / 0.6 / 0.8 filament values, the new 0.30mm Coarse for 0.4 (HF and standard; replaces the 0.30 "Match"), Prusa's new speeds/accelerations for the INDX 0.4 HF presets, PLA min fan 85 -> 100 % on the INDX. Generic PA is split into PA6/PA66/PA612/PA11/PA12. Prusa 1.0.24 limits some filaments (Prusament ASA, PC Blend, PETG CF, TPU 95A, Generic ABS/ASA/PC/FLEX/PVA/BVOH, Woodfill, rPLA) to the 0.4 nozzle on the INDX; the bundle also keeps them on the 1.0 HF nozzle (T8), where the user presets live. All 53 PS3 user presets still resolve.
* **Tool change (PS2, PS3, Orca):** Prusa's per-nozzle flush on the purge station (0.25 / 0.6 / 0.8) and the start G-code without the unrecovered `+ 0.04` retract (cf. prusa3d/PrusaSlicer-settings-prusa-fff#49). Kept: TPU/FLEX hotter clean + 8 s soak, priming heats the nozzles (#53).
* **Removed the extra `G12 S2` quick clean** from the PS3 tool change (Prusa does not have it; it is the fast wipe that threw filament bits on the plate). In PS2 it was already commented out.
* **Renamed printers** (nothing in them is wiper-specific): PS2 `HF0.4 nozzle + Wiper` -> `HF0.4 nozzle (custom)` (the plain name is a Prusa system preset), `HF0.4 nozzle + Wiper + GECO` -> `HF0.4 nozzle + GECO`, `Mixed Nozzles + Wiper` -> `Mixed Nozzles`, `Mixed Nozzles + Wiper + GECO` -> `Mixed Nozzles + GECO`; PS3 `Prusa CORE One INDX + Wiper` -> `Prusa CORE One INDX 8T (custom)`. The old one-off scripts in `scripts/` still use the old names.
* **PS2 T7 (0.25):** retract 0.8 -> 0.7 mm (Prusa's 0.25 value); 0.07 / 0.10 mm presets take Prusa's speeds and accelerations (0.07: outer 80, perimeters 120, small 80 mm/s); new `0.15mm Detail @COREONEINDX 0.25 - T7`.
* **PS2 GECO printers are PLA-only for our filaments:** the two `+ GECO` printers carry the keyword `GECO_COLD_PLATE` in `printer_notes`, and the 25 non-PLA user filaments (PETG, ASA, PA/PC/PP CF, TPU) add `and printer_notes!~/.*GECO_COLD_PLATE.*/`. Prusa's own system filaments cannot be hidden per printer without editing the vendor file.
* **PS2 GECO start G-code check:** if any used tool has a non-PLA filament, the start G-code adds `M117 GECO: PLA only!` and `M862.3 P "GECO-PLA-ONLY"` (a deliberate printer-model mismatch), so the printer warns, or refuses with the model check set to strict. Not yet tested on the printer.
* **PrusaSlicer 3 bundle 1.0.14:** the *GECO (cold)* sheet gets the same PLA-only check in its start G-code.
* **`install.ps1`** (repository root): copies the profiles into the PrusaSlicer 2.x / PrusaSlicer 3 / OrcaSlicer data folders with a backup; README *Install* rewritten. Not yet run on a clean machine.
* New filaments (2026-11-18): GeeeTech PLA Water Blue and GeeeTech PLA Black Carbon Fiber for HF0.4, PS2 and PS3.

## 2026-11-17 - Priming heats the nozzles

* **Fix: "Prime all printing extruders" primed cold.** Prusa's INDX `toolchange_gcode` heats a nozzle only when `layer_num >= 0`; during priming (`layer_num < 0`) it only picked the tool (`T2 S1 L0 D0`), with no `M104`/`M109`. T2-T5 and T0 were primed cold and T0 stayed at the `M104 S120` of the Z homing, so the print started at 120 C. The `else` branch now sets and waits for `first_layer_temperature` of the nozzle (`M104` + `M109`). Patched in the four PrusaSlicer 2.x INDX printer presets, the PrusaSlicer 3 user printer preset "Prusa CORE One INDX + Wiper" and the PrusaSlicer 3 mixed-nozzle bundle (1.0.12 zip). Confirmed on the printer: every nozzle heats and primes correctly. Reported to Prusa: https://github.com/prusa3d/PrusaSlicer-settings-prusa-fff/issues/53

## 2026-11-16 - Sunlu White, Prusament PETG/ASA for 1.0 HF, normal 1.0 HF prints

* **Sunlu High Speed Matte PETG White** for T6 (standard 0.4; cap 11 mm3/s, PA 0.050 estimated from the GeeeTech Std/HF step) and for T8 (copy of the T8 tune, colour #FFFFFF), in PrusaSlicer 2.x, OrcaSlicer and as PrusaSlicer 3 user presets.
* **Prusament PETG @ 1.0HF - T8** (260 C, bed 90/85, cap 30, PA 0.018) and **Prusament ASA @ 1.0HF - T8** (270 C, bed 110, fan 20-30, cap 30, PA 0.007, shrinkage compensation 0.22 % from Prusa's CORE One ASA group). Prusa has no 1.0 mm profiles; both follow Prusa's 0.8 HF values scaled to INDX. Caps and PA are estimates until a flow and a PA test.
* **Normal print presets for the 1.0 HF nozzle (T8)**: 0.30 / 0.40 / 0.50 mm, 2 perimeters, 15 % gyroid, 1.05 mm lines, speeds limited to 30 mm3/s (95 / 70 / 55 mm/s), 2-loop skirt, in PrusaSlicer 2.x and OrcaSlicer. In the PrusaSlicer 3 bundle (1.0.10) the Vase profiles stay as alternatives at 0.40 / 0.50 / 0.60 and "0.50mm Normal" is the default for T8; 0.30 mm is now a layer height on every nozzle.
* **PrusaSlicer 3 bundle 1.0.11 / 1.0.12**: PS3 validates the line widths of *every* tool at the print layer height, even unused ones. The 0.25 mm nozzle (T7) has 0.25 mm lines, so any layer height above 0.20 gave "extrusion width is too low to be printable at current layer height" (only 0.20 worked). The "Match" placeholders now get lines of at least 1.5 x the layer height, capped at 2.48 x the nozzle diameter (PS3 rejects wider: "too large to be printable with the nozzle diameter"). Reported working by the author in PS3 alpha 14 up to 0.60 mm (the 0.60 mm margin on T7 is only 0.02 mm).

## 2026-11-11 - PrusaSlicer 3 mixed nozzles, T6/T7 filaments, TPU

* The TPU part sliced by **PrusaSlicer 3 printed with a better fit** than the PrusaSlicer 2.x one; the cause is how each slicer splits a thin wall into beads, see [prusaslicer-3-alpha.md](prusaslicer-3-alpha.md). Also noted there: alpha 14 crashes when opening a 2.x project with mixed nozzles, and its built-in flow and temperature towers.
* **Infill default 10 % gyroid** everywhere: nine PrusaSlicer 2.x print presets changed (T7 and T6 White from 15 % grid; Speed 120% and T6 TPU from 15 %; T6 CF from 20 %; 0.07 ColorMix from 8 %), and it is the printer default in the PrusaSlicer 3 bundle (1.0.9). OrcaSlicer already had it.
* **OrcaSlicer Ultrafuse TPU**: the filament start G-code came from the Nextruder TPU profile (`M900 K0`, heatbreak temperature) and never set the reduced extruder current. It now sends `M572 S0` and `M906 P2` like PrusaSlicer 2.x and 3.
* The Ultrafuse TPU T6 profile printed well from PrusaSlicer 2.x. The PrusaSlicer 3 G-code for the same part matches it ([comparison](prusaslicer-3-alpha.md#prusaslicer-3-alpha-14-compared-with-prusaslicer-29-observed-10-11-nov-2026)); the OrcaSlicer one has not been re-sliced since the fix.
* **PrusaSlicer 3 alpha 14: mixed-nozzle INDX printer** as a separate preset source (0.4 HF, 0.4 standard, 0.25 and 1.0 HF tools on one printer), generated from Prusa's FFF profiles 1.0.23. See [prusaslicer-3-mixed-nozzles.md](prusaslicer-3-mixed-nozzles.md). Idea from ltlowe's Multi-Size Core One INDX bundle.
* New filaments in all three slicers: **Ultrafuse TPU 95A for T6** (standard 0.4), **Prusament PETG for T7** (0.25). T7 Prusament PLA moved to Prusa's 2.5.15 values (220 C, PA 0.13).
* **Ultrafuse TPU 95A** (all variants): 225 C / 230 first layer, bed 40, fan 20-100 % automatic from BASF's Prusa profile; retract 3 -> 1.5 mm from Prusa's INDX TPU profile.
* **OrcaSlicer Mixed Nozzles machines**: the start G-code declared every tool as high-flow in the nozzle check (`M862.1 ... F1`); T6 and T7 now report `F0`.
* Sliced and compared one TPU part on T6 in all three slicers: each G-code selects tool 6 throughout. PrusaSlicer 3 lacked the TPU hotter clean + soak for the *first* tool; it is now in the mixed bundle's start G-code.

## 2026-11-10 - Skirt and Speed 120 % profiles

* All INDX print/process presets now print a **2-loop skirt** (nozzle clean-up before the part): `skirts = 2` in PrusaSlicer 2.x (ColorMix presets also `skirt_distance` 0 -> 6), `skirts: 2` in the PS3 alpha print presets, `skirt_loops` 2 in OrcaSlicer.
* New **0.20mm Speed 120%** and **0.25mm Speed 120%** presets for the HF 0.4 tools in all three slicers: the stock Balanced / Draft speeds x 1.2 (same as the 120 % speed override on the printer panel), accelerations unchanged, Gyroid infill. PS3 has a `print` + `tool_print` pair for each.
* The slicer still limits speed by each filament's max volumetric speed, so these presets only run faster where the filament cap allows it. Caps are not raised without a max-flow test.
* **GeeeTech PETG** HF 0.4 cap 18 -> **22** mm3/s (prints well at 120 % on T1; no max-flow test yet).

## 2026-11 - credits

* Added a Credits section to the README (Kiddocteur for the TPU tool-change fix, hyiger for the mixed-nozzle INDX profile that documents per-tool filament filtering).

## 2026-11 - TPU tool changes (untested)

* The INDX printer presets of PrusaSlicer 2.x, PrusaSlicer 3 alpha and OrcaSlicer now use a hotter cleaning temperature (target - 25 C instead of
  target - 60 C) and an 8 s soak for flexible filaments only (FLEX / TPU), following a report by Kiddocteur on the Prusa forum.
  See [tpu-toolchange.md](tpu-toolchange.md) for the source and details.

## 2026-11 - publishing

* Added the AGPL-3.0 licence (the presets derive from PrusaSlicer / OrcaSlicer presets, which are AGPL-3.0) and made the repository public.
* Collected profiles, notes and scripts into this repository. INDX only (the Mini IS presets are not included).
  Machine presets for OrcaSlicer were scrubbed of host, user, password, API key and Prusa Connect id.

## 2026-11 - OrcaSlicer defaults

* All OrcaSlicer process presets for the INDX changed from 15 % Grid to **10 % Gyroid**; added Gyroid variants of Fine / Detail / Draft.

## 2026-11 - Sunlu High Speed Matte PETG flow test

* Ran a max-flow tower at 255 C: clean to 34.9 mm3/s. Profile changed from 255 C / cap 22 to **250/245 C, cap 30**.
* Added throw-away FLOWTEST presets (cap 100, layer slowdown off, filament ids 1).
* Compared with Prusament PETG; see [flow-tests.md](flow-tests.md).

## 2026-11 - PETG family

* **GeeeTech PETG Transparent** - slow, glass-clear profile (235/240 C, cap 8, low fan).
* **GeeeTech PETG** - normal/fast profile for any colour (245/250 C, cap 18).
* **Sunlu High Speed Matte PETG**.
* Each for PrusaSlicer 2.x, PrusaSlicer 3 alpha and OrcaSlicer on T1-T5 (HF 0.4), plus T8 (1.0 HF) variants for PS 2.x and Orca.
* Fixed T8 PLA pressure advance values in Orca (0.009 / 0.013 / 0.011) to match the PS 2.x ones.

## Earlier

* Audit and clean-up of the PS 2.x, PS3 alpha and Orca presets for the mixed-nozzle INDX, including the T6 (standard 0.4), T7 (0.25) and
  T8 (1.0 HF) filament sets, CF filaments, TPU flow variants and TriColor Silk PLA.
* Orca compatibility fixes (compat by machine name, visibility in the filament list).
