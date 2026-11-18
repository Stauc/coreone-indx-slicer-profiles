# Prusa CORE One INDX - slicer profiles and notes

Filament, process and printer presets for the **Prusa CORE One INDX 8T** with a mixed set of nozzles, for
**PrusaSlicer 2.9.x**, **PrusaSlicer 3.0 alpha** and **OrcaSlicer 2.5**, plus the test notes behind the numbers and the Python scripts
used to generate and verify them.

> Status: personal working set, tuned on one printer with the spools listed in [docs/filaments.md](docs/filaments.md).
> Values marked "estimate" in the docs have not been printed yet. Treat everything as a starting point and run your own first-layer,
> flow and pressure-advance checks. Not affiliated with or endorsed by Prusa Research, Sunlu, Geeetech or Ultrafuse.
> Day to day the author now slices with the PrusaSlicer 3 alpha (mixed-nozzle preset source) and uses OrcaSlicer for tuning; the PrusaSlicer 2.x presets are the tested base the other two are derived from.

## Hardware this is written for

| Tool | Nozzle | Used for |
|---|---|---|
| T1-T5 | 0.4 mm high-flow (CHT) | everyday PLA / PETG / ASA / TPU |
| T6 | 0.4 mm standard (no CHT) | CF filaments, TPU, white PLA/PETG |
| T7 | 0.25 mm | fine detail |
| T8 | 1.0 mm high-flow | big prints, normal and vase mode |

Printer variants: *Mixed Nozzles*, *+ GECO* (cold-plate variant, PLA only), *HF0.4 nozzle (custom)* (all tools 0.4 HF). The "+ Wiper" suffix was dropped on 2026-11-18: the presets have nothing wiper-specific.
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

Windows, with the slicer closed. Download the repository (*Code > Download ZIP*), unpack it, open PowerShell in that folder and run one of:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -PS3          # PrusaSlicer 3 alpha
powershell -ExecutionPolicy Bypass -File .\install.ps1 -PS2          # PrusaSlicer 2.x
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Orca         # OrcaSlicer filaments + processes (add -OrcaMachines for the printers)
powershell -ExecutionPolicy Bypass -File .\install.ps1 -All
```

The script copies the files into the slicer data folders and backs up any file it overwrites (`_backup_install_<date>` in the same folder).

* **PrusaSlicer 3 alpha** (the author's main slicer). After the script, in PrusaSlicer 3: *Configuration > Preset Sources and Updates > Add Zip*,
  pick `slicers/prusaslicer-3-alpha/mixed-nozzles/stauc-indx-mixed_offline_<version>.zip`, enable the source, add the printer **CORE One INDX Mixed 8T**
  and set the nozzle of each tool (0.4 HF / 0.4 / 0.25 / 1.0 HF). For a cold plate pick the sheet *GECO (cold)*. Details: [docs/prusaslicer-3-mixed-nozzles.md](docs/prusaslicer-3-mixed-nozzles.md).
  The script also copies the user presets for these tools and the printer `Prusa CORE One INDX 8T (custom)` for Prusa's own INDX printer.
  The data folder is looked up as `%APPDATA%\PrusaSlicer3-dev`, `PrusaSlicer3` or `PrusaSlicer-3`; otherwise pass `-PS3DataDir "<folder>"`.
* **PrusaSlicer 2.x** - needs Prusa's *CORE One INDX* printer installed once through the Configuration Wizard (the profiles inherit from it).
  Then pick one of the printers `Prusa CORE One INDX 8T Mixed Nozzles`, `... Mixed Nozzles + GECO`, `... HF0.4 nozzle (custom)`, `... HF0.4 nozzle + GECO`.
* **OrcaSlicer** - copied into `%APPDATA%\OrcaSlicer\user\default\` (`-OrcaUser <name>` for another user folder). The machine presets have their host,
  API key and Prusa Connect id **blanked**: fill them in again. Orca ties filaments to machines by *name*, so the compatible-printer lists name the author's four
  machines (`HF 0.4 nozzle` / `Mixed Nozzles`, each `- LAN` / `- Connect`); edit them if your machine names differ.

Manual install: copy the files of `slicers/<slicer>/...` into the same-named folders of the slicer data directory.

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
