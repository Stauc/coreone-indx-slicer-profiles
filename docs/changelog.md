# Changelog

Newest first. Dates are the working dates of the session in which each change was made.

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
