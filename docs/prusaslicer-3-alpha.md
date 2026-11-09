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

Only the **T1-T5 HF 0.4** profiles are provided for PS3 (filaments, the ColorMix print/tool_print presets and the `+ Wiper` printer).
There are no T6, T7 or T8 filaments for PS3 yet.

## Alpha 13 -> 14

* No changes in preset **values** for the INDX presets compared here.
* One additional key on the INDX printer preset.
* Brand metadata (uuid / slug) was added to the vendor data.
* The condition syntax moved to the multi-material style shown above.

## Known annoyances

* PS3 reopened on the *CORE One* printer instead of the *CORE One INDX* one after restarts.
* Because YAML presets depend on opaque ids, copying files between machines only works if both machines have the same alpha's vendor data.
