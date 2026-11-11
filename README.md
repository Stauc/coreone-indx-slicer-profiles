# Prusa CORE One INDX - slicer profiles and notes

Filament, process and printer presets for the **Prusa CORE One INDX 8T** with a mixed set of nozzles, for
**PrusaSlicer 2.9.x**, **PrusaSlicer 3.0 alpha** and **OrcaSlicer 2.5**, plus the test notes behind the numbers and the Python scripts
used to generate and verify them.

> Status: personal working set, tuned on one printer with the spools listed in [docs/filaments.md](docs/filaments.md).
> Values marked "estimate" in the docs have not been printed yet. Treat everything as a starting point and run your own first-layer,
> flow and pressure-advance checks. Not affiliated with or endorsed by Prusa Research, Sunlu, Geeetech or Ultrafuse.

## Hardware this is written for

| Tool | Nozzle | Used for |
|---|---|---|
| T1-T5 | 0.4 mm high-flow (CHT) | everyday PLA / PETG / ASA / TPU |
| T6 | 0.4 mm standard (no CHT) | CF filaments, TPU, white PLA/PETG |
| T7 | 0.25 mm | fine detail |
| T8 | 1.0 mm high-flow | big/vase-mode prints |

Printer variants: *Mixed Nozzles + Wiper*, *+ GECO* (cold-plate variant, PLA only), *HF 0.4 nozzle + Wiper* (all tools 0.4 HF).
Details and the compatibility conditions are in [docs/hardware-and-nozzle-layout.md](docs/hardware-and-nozzle-layout.md).

## Layout

```
slicers/
  prusaslicer-2.x/        filament/  print/  printer/        (.ini)
  prusaslicer-3-alpha/    presets/user/prusa-research-fff/PrusaResearch/   (.yaml)
                          mixed-nozzles/   separate preset source with a mixed-nozzle INDX printer (.zip) + its user presets
  orcaslicer/             filament/  process/  machine/      (.json)  + flowtest/ (throw-away calibration presets)
docs/                     hardware, filament table, flow-test results, PS3 notes, changelog
scripts/                  Python used to build/audit the profiles (paths assume the author's data folders)
```

## Naming

| Suffix | Meaning |
|---|---|
| `@COREONEINDX HF0.4` (Orca: `@Prusa CORE One INDX`) | T1-T5, 0.4 high-flow nozzle |
| `... Std0.4 - T6` | T6, 0.4 standard nozzle |
| `... 0.25 - T7` | T7, 0.25 nozzle |
| `... 1.0HF - T8` | T8, 1.0 high-flow nozzle |
| `- GECO` | for the cold-plate printer variant, PLA only |
| `- FLATTENED`, `- ICE Rob`, `- GeeeTech` | the author's own tunes (see filament table) |

## Install

Close the slicer first, copy the files, start it again. Existing files with the same name are overwritten, so back up first.

* **PrusaSlicer 2.x** - copy `filament`, `print`, `printer` `.ini` files into the same-named folders of your PrusaSlicer data directory
  (`%APPDATA%\PrusaSlicer` on Windows). Needs the official *Prusa CORE One INDX* printer profile installed (`inherits` points to it).
* **PrusaSlicer 3.0 alpha** - copy the `.yaml` files into `<PS3 data dir>/presets/user/prusa-research-fff/PrusaResearch/`.
  Parent preset ids were taken from alpha 13/14 and may change in later builds ([docs/prusaslicer-3-alpha.md](docs/prusaslicer-3-alpha.md)).
* **OrcaSlicer** - copy `filament`, `process`, `machine` `.json` files into `%APPDATA%\OrcaSlicer\user\default\<folder>\`.
  The `machine` presets have their host, user, password, API key and Prusa Connect id **blanked**: either fill them in again or skip those files.
  Orca ties filaments to machines by *name*, so the compatible-printer lists name the author's four machines
  (`HF 0.4 nozzle` / `Mixed Nozzles`, each `- LAN` / `- Connect`); edit them if your machine names differ.

## Documents

* [docs/hardware-and-nozzle-layout.md](docs/hardware-and-nozzle-layout.md) - tools, conditions, INDX start G-code facts
* [docs/filaments.md](docs/filaments.md) - every filament profile with its main values and where they come from
* [docs/flow-tests.md](docs/flow-tests.md) - max-flow tests, pitfalls, results
* [docs/prusaslicer-3-alpha.md](docs/prusaslicer-3-alpha.md) - PS3 preset format notes and alpha 13 -> 14 comparison, differences from PrusaSlicer 2.9
* [docs/prusaslicer-3-mixed-nozzles.md](docs/prusaslicer-3-mixed-nozzles.md) - mixed nozzles on one INDX printer in PrusaSlicer 3 alpha 14
* [docs/tpu-toolchange.md](docs/tpu-toolchange.md) - hotter clean + soak for TPU/FLEX tool changes in all three slicers (from a Prusa forum report, untested here)
* [docs/changelog.md](docs/changelog.md) - what was done, in order

## Credits

* **Kiddocteur** - the hotter cleaning temperature and soak for TPU tool changes, from his
  [Prusa forum report](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/solved-tpu-tangling-at-the-extruder-after-indx-tool-changes-the-nozzle-was-too-cold-during-cleaning/);
  details in [docs/tpu-toolchange.md](docs/tpu-toolchange.md).
* **[hyiger](https://forum.prusa3d.com/forum/profile/hyiger/)** - [A Mixed Nozzle Profile for the INDX](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/a-mixed-nozzle-profile-for-the-indx/) (Prusa forum, 25 Oct 2026) and his repository
  [hyiger/prusaslicer-indx-profiles](https://github.com/hyiger/prusaslicer-indx-profiles) (AGPL-3.0): a published mixed-nozzle setup for the INDX
  (0.25 mm in tool 1, HF0.4 in tools 2-8) in which PrusaSlicer filters each tool's filaments by that tool's nozzle. That observation is used in
  [docs/hardware-and-nozzle-layout.md](docs/hardware-and-nozzle-layout.md) and the idea of one printer preset with different nozzles per tool is the same here, but the tool layout,
  conditions and profiles in this repository were built separately and no files or settings were copied from his repository.
  If a 0.25 + HF0.4 layout suits you better, use his.

* **ltlowe** - [Multi-Size Core One INDX profile bundle](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/i-have-created-a-multi-size-custom-vendor-profil/#post-808190) (Prusa forum, 2 Nov 2026): the idea of a separate PrusaSlicer 3 printer family with its own tools, and the offline-archive layout that
  [docs/prusaslicer-3-mixed-nozzles.md](docs/prusaslicer-3-mixed-nozzles.md) follows. No files from his bundle are included.
* **BASF Forward AM** - data sheet and Prusa print profiles for Ultrafuse TPU 95A, used for the temperatures, bed and cooling of the Ultrafuse profiles.

## Licence

Released under the **GNU Affero General Public License v3.0** - see [LICENSE](LICENSE). The presets are derived from the official
presets shipped with PrusaSlicer and OrcaSlicer, which are themselves AGPL-3.0 projects, so the same licence is used here to stay on the safe side.
Product and company names belong to their owners and are used only to identify the filaments and printer these profiles are meant for.
