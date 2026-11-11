# PrusaSlicer 3 alpha: mixed nozzles on the CORE One INDX

Prusa's own PrusaSlicer 3 profiles (1.0.23) only allow the 0.4 HF nozzle on the INDX. This folder adds a **separate preset source** with its own
printer, "CORE One INDX Mixed 8T", where every tool can be 0.4 HF, 0.4 standard, 0.25 or 1.0 HF.

The idea of a separate printer family with its own tools comes from ltlowe's
[Multi-Size Core One INDX bundle](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/i-have-created-a-multi-size-custom-vendor-profil/#post-808190)
(Prusa forum, 2 Nov 2026). No files from that bundle are used; everything here is generated from Prusa's installed profiles by
[`scripts/build_ps3_mixed_vendor.py`](../scripts/build_ps3_mixed_vendor.py).

> Status: built and used on PrusaSlicer 3.0.0-alpha14 with Prusa FFF profiles 1.0.23. Slicing and upload to Prusa Connect work. Only a TPU part on
> T6 has been printed. PrusaSlicer 3 is an alpha and its preset format changes between builds.

## Files

| File | What it is |
|---|---|
| `slicers/prusaslicer-3-alpha/mixed-nozzles/stauc-indx-mixed_offline_1.0.8.zip` | the preset source (offline archive) |
| `slicers/prusaslicer-3-alpha/mixed-nozzles/user-presets/` | the author's filaments for it, one per nozzle type |
| `scripts/build_ps3_mixed_vendor.py` | builds the archive from an installed `PrusaResearch` preset folder |
| `scripts/port_ps3_mixed_user_presets.py` | converts PrusaSlicer 2.x INDX filament `.ini` files into user presets for it |

## Install

1. *Configuration > Preset Sources and Updates > Add Zip*, pick the archive, enable the source.
2. Add the printer "CORE One INDX Mixed 8T" and set the nozzle of each tool.
3. Optional: copy the files from `user-presets/` to `<PS3 data dir>/presets/user/stauc-indx-mixed/StaucINDXMixed/` (create the folders) and restart.

## What is in the archive

* **Tools**: 0.4 HF, 0.4, 0.25, 1.0 HF. **Sheets**: Satin, PEI Smooth, PEI Textured, PA Nylon, PP and "GECO (cold)".
* **Layer heights**: 0.05 / 0.07 / 0.10 / 0.12 / 0.15 / 0.20 / 0.25 / 0.40 / 0.50 / 0.60 mm on every nozzle. PrusaSlicer 3 only offers a layer height
  that exists for *all* tools of the printer, so nozzles without a real profile at a height get a placeholder named "Match" (a copy of their nearest
  real profile). Nothing stops you assigning an object to a tool whose nozzle cannot print that layer height.
* **Print presets, selectable per tool** at one layer height:
  0.4 HF - Prusa's four plus *Speed 120%* (0.20, 0.25) and *ColorMix* (0.07, 0.12, 0.15); 0.4 standard - copies of the HF ones plus *White*, *CF*,
  *TPU* (0.20); 0.25 - Prusa's three plus *Ultra Fine* (0.05); 1.0 HF - *Vase* (0.40, 0.50, 0.60).
* **Printer preset**: the author's Wiper tool-change G-code with the TPU/FLEX hotter clean + soak ([tpu-toolchange.md](tpu-toolchange.md)), also
  applied in the start G-code for the first tool. With a cold sheet selected the start G-code keeps the bed heater off. 2-loop skirt.
* **Filaments**: all Prusa filaments, renamed `... @INDXMIX`. Only a few of them have values for the 0.4 standard nozzle and none for 0.25 or 1.0 HF,
  which is what the user presets are for.
* The printer reports the model `COREONE_INDX8T`, so Prusa Connect treats the G-code as a normal INDX 8T job.

## How the archive is laid out

```
manifest.json            source id, name
vendor_indices.zip       <Vendor>.idx with "min_slic3r_version" and the version list
<Vendor>/<version>/      vendor.yaml, preset-*.yaml, assets/, manifest.json (file name + sha256 of every file)
```

Without `vendor_indices.zip` alpha 14 answers "not a usable preset source". Alternatives at one layer height must be unconditioned children of the
layer-height node; siblings with the same condition are first-match only.

## Limits

* It is a snapshot of Prusa's 1.0.23 profiles and does not follow Prusa's updates; rebuild it with the script.
* All preset ids differ from Prusa's, so user presets made for the official INDX printer do not show up here.
* Editing Prusa's installed profiles in place does not work: the files stay but the tools remain locked, and a profile update overwrites them.
* Whether the cold-sheet start G-code really keeps the bed off has not been checked on a print.
