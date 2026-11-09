# Hardware and nozzle layout

Prusa CORE One INDX 8T, firmware 8.0.0. Eight tool heads with different nozzles. The profiles encode which tool a filament is meant for.

## Tools

| Tool | Nozzle | Notes |
|---|---|---|
| T1-T5 | 0.4 HF (CHT) | default tools |
| T6 | 0.4 standard (no CHT) | CF, TPU, white. White PLA tends to clog, so it lives here |
| T7 | 0.25 | fine detail |
| T8 | 1.0 HF | vase mode, large lines |

A second printer, a Mini IS, is outside the scope of this repository.

## PrusaSlicer 2.x compatibility conditions

`KW` is `printer_notes=~/.*INDX_MIXED_NOZZLES.*/` (set in the *Mixed Nozzles* printer presets).

* HF 0.4 filaments (T1-T5): `printer_model=~/(COREONE_INDX8T|COREONE_INDX4T|COREONEL_INDX8T|COREONEL_INDX4T)/ and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]`
* T6 filaments: `KW and ((nozzle_diameter[0]==0.4 and !nozzle_high_flow[0]) or (nozzle_diameter[5]==0.4 and !nozzle_high_flow[5]))`
* T8 filaments: `KW and ((nozzle_diameter[0]==1 and nozzle_high_flow[0]) or (nozzle_diameter[7]==1 and nozzle_high_flow[7]))`

The OR form works whether PrusaSlicer evaluates the condition against the first extruder only or against each tool's own nozzle
(hyiger reports in his [mixed-nozzle thread](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/a-mixed-nozzle-profile-for-the-indx/) that PrusaSlicer filters each tool's filament list by that tool's nozzle; the 2.9.7 behaviour was not confirmed here).
PrusaSlicer 2.x user filament presets are full dumps of ~87 keys; `inherits` is informational, the condition decides visibility.

## OrcaSlicer

User presets are partial JSON that `inherit` a system preset, and `compatible_printers` lists machine **names**. The nozzle size cannot gate a
filament, so T6/T8 variants are separate presets and the process presets for T6/T7/T8 name the extruder (`wall_filament` etc.) explicitly.

## INDX start G-code facts

* `M862.1 T<n> P<nozzle> A<abrasive> F<highflow>` is sent for every used tool.
* `M574 S<n> V35 T<temp> F<x>`: Orca's machine start G-code computes `F = min(perimeter_flow_rate, filament max volumetric speed) / filament area`,
  where `perimeter_flow_rate` is outer-wall speed x cross-section from the **process-level** layer height and outer-wall width.
  A process with a small perimeter flow therefore produces a small `F`. Prusa's public G-code documentation does not describe `M574`, so it is not
  known whether the firmware enforces `F`; calibration prints were patched to a high `F` to be safe (see [flow-tests.md](flow-tests.md)).
* Tool change: `G12 S90` (enter cleaner), `G12 S30` (eject), `G12 S91` (exit). Purge speeds are derived from the filament's max volumetric speed.
* Filament start G-code sets pressure advance: `M572 S<pa> ; Pressure advance` then `M573 R`.
* GECO printer variant: the start G-code contains `M140 S0` (no bed heat). Use it for PLA only.

## Pressure advance scaling used for the 1.0 nozzle

Prusa publishes CORE One tables per nozzle (PC CF / PA11 CF: 0.4 = 0.05, 0.5 = 0.035, 0.6 = 0.025, 0.8 = 0.016; PP CF: 0.4 = 0.036 ... 0.8 = 0.015).
Prusa has no 1.0 values, so 1.0 mm values here are the 0.4 value x 0.447 (Prusa's PETG 0.4 -> 0.8 ratio) x 0.69 (0.8 -> 1.0 step used for the CF
profiles, 0.016 -> 0.011). Treat them as estimates and run a PA test on T8.
