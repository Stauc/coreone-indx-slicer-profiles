# PrusaSlicer 3.0 alpha notes

Written against alpha 13 and alpha 14 on Windows. The format is unstable; expect to redo parts of this.

## Where things live

* Data directory: `PrusaSlicer3-dev` (separate from the 2.x data directory).
* User presets: `presets/user/prusa-research-fff/PrusaResearch/`, one **YAML** file per preset, prefixed by type:
  `filament-`, `print-`, `tool_print-`, `printer-`.
* The vendor bundle copy is under `presets/local`; `update_sync` was old in the data directory examined.

## Format differences from 2.x

* YAML, partial presets: only changed keys plus identity/inheritance keys (`unconditional_inherits`, `based_id`, `based_root_id`).
  2.x user filaments are full ~87-key dumps instead.
* Pressure advance is a filament key: `pressure_advance_value`.
* Compatibility uses the new namespaced syntax, for example
  `((printer.base_model == "COREONE_INDX") and (tool.nozzle_diameter == 0.4) and tool.nozzle_high_flow)`
  instead of `printer_model=~/.../ and nozzle_diameter[0]==0.4 ...`.
* Parent presets are referenced by an **opaque id**, not by name. The id of `Prusament PETG @COREONEINDX HF0.4` was
  `Pg/x3f1fSQGhLv63C+xlpw` (root preset `Prusament PETG`) in the builds checked here. Ids may change between alphas; if a preset
  shows as detached, re-derive the id from a preset you saved yourself.

## Coverage

Only the **T1-T5 HF 0.4** profiles are provided for PS3 (filaments, the ColorMix and Speed 120% print/tool_print presets and the `+ Wiper` printer).
There are no T6, T7 or T8 filaments for PS3 yet.

## Alpha 13 -> 14

* No changes in preset **values** for the INDX presets compared here.
* One additional key on the INDX printer preset.
* Brand metadata (uuid / slug) was added to the vendor data.
* The condition syntax moved to the multi-material style shown above.

## Known annoyances

* PS3 reopened on the *CORE One* printer instead of the *CORE One INDX* one after restarts.
* Because YAML presets depend on opaque ids, copying files between machines only works if both machines have the same alpha's vendor data.

## PrusaSlicer 3 alpha 14 compared with PrusaSlicer 2.9 (observed 10-11 Nov 2026)

Notes from building the mixed-nozzle printer ([prusaslicer-3-mixed-nozzles.md](prusaslicer-3-mixed-nozzles.md)) and from slicing the same TPU part for
tool 6 in both slicers. "Why" is the author's reading of the profile files and the slicer log, not something Prusa has stated.

### How presets are organised

| | PrusaSlicer 2.9 | PrusaSlicer 3 alpha 14 | Probable reason |
|---|---|---|---|
| Nozzles on a printer | free per extruder in the printer preset | only the *tools* the vendor profile defines for that printer; the INDX has just 0.4 HF | hardware is described in `vendor.yaml` (printer, tool, sheet, feeder) and presets attach to it; Prusa's 1.0.23 only ships INDX presets for 0.4 HF |
| Print profile | one profile holds everything, including which extruder prints what | split into a *print* preset (layer height, skirt, whole-print settings) and one *tool print* preset per tool (speeds, widths, infill) | each tool can have its own nozzle, so speed and width belong to the tool |
| Different settings per tool | not possible in one print profile | each tool picks its own tool-print preset, but all share one layer height | one layer height per print; a height is only offered if **every** tool of the printer has a tool-print preset for it (the log says "removed as it has at least one tool without tool print presets") |
| Sending a print to one tool | print profile can force the extruder (`perimeter_extruder = 6`) or the object has an extruder | only the object's tool assignment | the print preset no longer knows about tools |
| Build plate | a separate printer preset per plate | the sheet is selected on the printer, and presets can react to `sheet.type` | sheets are hardware objects; Prusa's filaments already switch bed temperature this way |
| Pressure advance | a line in the filament start G-code (`M572 S...`) | a filament setting (`pressure_advance_value`) | settings instead of G-code snippets |
| User presets | plain files, shown for any compatible printer | stored per source and vendor and tied to that vendor's preset ids | a preset inherits by id, so it cannot move to another vendor's printer |

### Things that behave differently

* **Profile files are not editable in place.** Prusa's installed profiles were replaced by 1.0.23 on the next start, and switching the INDX nozzle
  flags on in those files did not unlock the tools anyway. A separate preset source is the way that works.
* **Named alternatives at one layer height** have to be nested under a single layer-height entry. Two entries with the same condition next to each
  other are first-match only, so the second never shows up.
* **Some 2.9 filament keys are rejected** (`filament_load_time`, `filament_unload_time`: "Invalid key ... for class FilamentSettings" in the log), and a
  preset with one bad key is dropped completely.
* **Prusa Connect** matches the job by the printer model in the profile (`legacy_printer_model`). With a made-up model name Connect showed "no
  compatible printers"; with `COREONE_INDX8T` the upload works.
* **The settings summary at the end of the G-code is not per tool.** For a part printed only with tool 6 it listed tool 8's values (1 perimeter,
  1.1 mm width, 0 % infill). The moves in the file used tool 6's preset. Do not judge a PrusaSlicer 3 file by that summary.
* **"Complete individual objects" is off unless set in the project**, the same as 2.9, but it is easy to miss. With it off, two small TPU parts were
  printed together and the fan stayed near its minimum; with it on, the fan pattern matched 2.9.
* **The first tool never runs the tool-change G-code**, so a tool-change fix (the TPU hotter clean and soak) also has to be in the start G-code. This is
  the same in 2.9; it only showed up here because the PS3 start G-code had not been patched.
* **The slicer writes a log** to `<data dir>/shared_runtime/log.txt`. It names rejected keys and removed presets, which the user interface does not.

### Same part, same settings: the G-code

Ultrafuse TPU 95A on tool 6 (0.4 standard), 0.20 mm, two small parts printed one after the other.

| | 2.9 (printed well) | 3 alpha 14 |
|---|---|---|
| Tool, nozzle check, temperatures, retract 1.5 mm, reduced extruder current, TPU clean + soak | reference | identical |
| Filament used | 739 mm | 740 mm |
| Outer wall | 6552 mm | 6557 mm, about 6 % more plastic per mm |
| Bridge infill | about 160 mm as its own feature | none; those areas are printed as ordinary infill |
| Idle temperature before bed levelling | 100 C | 70 C |
| Retractions | 267 | 261 |

The wall and bridge differences are probably the newer slicing engine (wall width distribution and bridge detection) rather than a profile value:
the same widths and speeds are set in both. The idle temperature comes from Prusa's stock start G-code, which differs between the 2.5.15 and 1.0.23
profile sets.

### How the two prints came out

Both files were printed. The PrusaSlicer 3 part fitted its mating hole easily; the 2.9 part was a hard fit. The files explain it: on a small tube
(about 4.3 mm outside diameter, wall a little over 1.1 mm) the two slicers split the wall differently with identical settings (3 perimeters, 0.45 mm).

| On that tube | 2.9 | 3 alpha 14 |
|---|---|---|
| Wall built from | three beads, 0.45 / about 0.29 / 0.45 mm | two beads of 0.57 mm |
| Nominal outside diameter | 4.29 mm | 4.28 mm |
| Plastic per layer | 2.24 mm3 | 2.24 mm3 |

Same target size and the same amount of plastic, but three squeezed passes of a soft material seem to push the outer surface out, where two
full-width passes stay put. The "6 % more plastic per mm" in the outer wall above is this section (wider outer beads, no middle bead), not extra
flow. Everywhere else the two toolpaths agree to about a thousandth of a millimetre. Setting 2 perimeters in 2.9 for such a part should give the
same split; that was not sliced to confirm.

### Opening a PrusaSlicer 2.9 project crashes alpha 14

Opening a 2.9 `.3mf` saved with mixed nozzles (0.4 HF, 0.4, 0.25, 1.0 HF) closes the slicer. The log shows
`Assertion failed at HwConfig.cpp:282 ... suggest_name(...)` with `tool => nullptr`: the project's printer model `COREONE_INDX8T` is matched to a
printer definition that has no tool for one of the nozzles. Import the STL files instead and set tool, filament and preset in PrusaSlicer 3.
It is not known whether this also happens without the mixed-nozzle preset source installed, since that source reports the same model name.

### Calibration tools

Alpha 14 ships a built-in Lua plugin "Calibration patterns" (`resources/lua/com.prusa3d.slicer.calibration`) with a **Flow Tower** (minimum and
maximum volumetric flow, number of steps) and a **Temperature Tower**, both in the Calibration menu. Third-party plugin collections exist as well
(for example leotrax3d's unofficial plugins with a fan tower, speed tower and tolerance test); none of them has been tried here.

### Not checked

* Whether the cold-sheet start G-code keeps the bed off on a real print.
* Anything printed with tools 7 and 8 from PrusaSlicer 3.
* Whether the 10 % gyroid default reaches the print (the test part has no sparse infill).
