# PrusaSlicer 3 alpha: mixed nozzles on the CORE One INDX

Prusa's own PrusaSlicer 3 profiles allow one nozzle type for all tools of the INDX (since 1.0.24: 0.4 HF, 0.25, 0.6 HF or 0.8 HF). This folder adds a **separate preset source** with its own
printer, "CORE One INDX Mixed 8T", where every tool can be 0.4 HF, 0.4 standard, 0.25 or 1.0 HF.

The idea of a separate printer family with its own tools comes from ltlowe's
[Multi-Size Core One INDX bundle](https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/i-have-created-a-multi-size-custom-vendor-profil/#post-808190)
(Prusa forum, 2 Nov 2026). No files from that bundle are used; everything here is generated from Prusa's installed profiles by
[`scripts/build_ps3_mixed_vendor.py`](../scripts/build_ps3_mixed_vendor.py).

> Status: archive 1.0.15, built on PrusaSlicer 3.0.0-alpha14 from Prusa FFF profiles 1.0.25. Slicing and upload to Prusa Connect work (checked with 1.0.12). Only a TPU part on
> T6 has been printed. PrusaSlicer 3 is an alpha and its preset format changes between builds.

## Files

| File | What it is |
|---|---|
| `slicers/prusaslicer-3-alpha/mixed-nozzles/stauc-indx-mixed_offline_1.0.15.zip` | the preset source (offline archive) |
| `slicers/prusaslicer-3-alpha/mixed-nozzles/user-presets/` | the author's filaments for it, one per nozzle type |
| `scripts/build_ps3_mixed_vendor.py` | builds the archive from an installed `PrusaResearch` preset folder |
| `scripts/port_ps3_mixed_user_presets.py` | converts PrusaSlicer 2.x INDX filament `.ini` files into user presets for it |

## Install

1. *Configuration > Preset Sources and Updates > Add Zip*, pick the archive, enable the source.
2. Add the printer "CORE One INDX Mixed 8T" and set the nozzle of each tool.
3. Optional: copy the files from `user-presets/` to `<PS3 data dir>/presets/user/stauc-indx-mixed/StaucINDXMixed/` (create the folders) and restart.

## What is in the archive

* **Tools**: 0.4 HF, 0.4, 0.25, 1.0 HF. **Sheets**: Satin, PEI Smooth, PEI Textured, PA Nylon, PP and "GECO (cold)".
* **Layer heights**: 0.05 / 0.07 / 0.10 / 0.12 / 0.15 / 0.20 / 0.25 / 0.30 / 0.40 / 0.50 / 0.60 mm on every nozzle. PrusaSlicer 3 only offers a layer height
  that exists for *all* tools of the printer, so nozzles without a real profile at a height get a placeholder named "Match" (a copy of their nearest
  real profile). PrusaSlicer 3 checks the line widths of every tool at the print layer height, so the placeholders get lines of at least 1.5 x the layer height, capped at 2.48 x the nozzle diameter (otherwise "extrusion width is too low / too large to be printable"). The 0.25 mm nozzle has no real profile above 0.20 mm. Nothing stops you assigning an object to a tool whose nozzle cannot print that layer height.
* **Print presets, selectable per tool** at one layer height:
  0.4 HF - Prusa's four plus *Speed 120%* (0.20, 0.25) and *ColorMix* (0.07, 0.12, 0.15); 0.4 standard - copies of the HF ones plus *White*, *CF*,
  *TPU* (0.20); 0.25 - Prusa's three (0.07, 0.10, 0.15) plus *Ultra Fine* (0.05); 0.4 HF and 0.4 also Prusa's *0.30mm Coarse*; 1.0 HF - *Normal* (0.30, 0.40, 0.50: 2 perimeters, 15 % gyroid, 1.05 mm lines, 30 mm3/s) and *Vase* (0.40, 0.50, 0.60); "0.50mm Normal" is the default for T8.
* **Default infill**: 10 % gyroid for the whole printer.
* **Printer preset**: Prusa's tool-change G-code (1.0.24, per-nozzle flush) plus the TPU/FLEX hotter clean + soak ([tpu-toolchange.md](tpu-toolchange.md)), also
  applied in the start G-code for the first tool, and heating of every nozzle during "Prime all printing extruders" (Prusa's profile primes cold). With a cold sheet selected the start G-code keeps the bed heater off, and if a used tool has a non-PLA filament it adds `M862.3 P "GECO-PLA-ONLY"` (a deliberate printer-model mismatch) so the printer warns, or refuses with the model check set to strict. 2-loop skirt.
* **Filaments**: all Prusa filaments, renamed `... @INDXMIX`, with Prusa's values for 0.25 (and 0.6 / 0.8, unused here). None has values for 1.0 HF and
  only a few for the 0.4 standard nozzle, which is what the user presets are for. Filaments Prusa limits to 0.4 on the INDX stay available on 1.0 HF.
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

* It is a snapshot of Prusa's 1.0.25 profiles and does not follow Prusa's updates; rebuild it with the script.
* All preset ids differ from Prusa's, so user presets made for the official INDX printer do not show up here.
* Editing Prusa's installed profiles in place does not work: the files stay but the tools remain locked, and a profile update overwrites them.
* Whether the cold-sheet start G-code really keeps the bed off has not been checked on a print.
