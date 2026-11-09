# TPU (FLEX) tool changes on the INDX

The four PrusaSlicer 2.x INDX printer presets in this repository contain a FLEX-only change to the cleaning temperature and a short
soak. It is based on a report by another INDX owner and is **not yet verified on this printer**.

## Source

Kiddocteur, "[Solved] TPU tangling at the extruder after INDX tool changes: the nozzle was too cold during cleaning",
Prusa forum, INDX general discussion, posted 07/11/2026 (the page does not say whether that is day/month or month/day; last edited about two days before 9 Nov 2026):
<https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/solved-tpu-tangling-at-the-extruder-after-indx-tool-changes-the-nozzle-was-too-cold-during-cleaning/>

Reported setup: Core One INDX, firmware 8.0.0, PrusaSlicer 2.9.6, Arianeplast TPU (Flexfill 92A based profile, FLEX, 225 C) printed together with PLA,
wipe tower off. At the time of writing it was a single report without independent confirmation, and the author changed several things at once and
says he does not know how much each one contributes. Credit for the diagnosis and the numbers goes to him.

## The problem

TPU printed fine on layer 1 but tangled at the extruder every time the printer came back to the TPU tool; almost nothing came out during the purge.
The stock tool-change G-code cools the nozzle to `max(160, target - 60)` for the cleaner and then does the "Final lock tool" push
(`G1 E1.6 F1200`) while the nozzle is still that cold. Soft TPU does not push into a half-melted plug, it buckles.

The stock presets contain exactly this logic (in `start_gcode` and `toolchange_gcode`). For the TPU profiles in this repository
(Ultrafuse TPU-95A, 220 C, first layer 230 C) the stock cleaning temperature is therefore 160 C on normal layers and 170 C on the first layer.

## What was changed here

Only for filaments with `filament_type = FLEX`:

1. The cleaning temperature becomes `target - 25` instead of `target - 60` (195 C normal layers, 205 C first layer for these TPU profiles).
2. An 8 s dwell (`G4 S8`) is added after the nozzle has reached the target temperature and before the deretract push, in the purge-station branch of
   the tool change and in the initial-tool sequence of the start G-code.

Both edits are marked with a comment that names the source. Other filaments are not affected. The edit is scripted in
[`scripts/apply_flex_toolchange.py`](../scripts/apply_flex_toolchange.py) (idempotent, keeps the CRLF line endings).

## What was not changed

The same post also lists other FLEX-only tweaks that were applied together and not tested separately: multitool ramming off, purge speed floor
0.5 mm/s, deretract 0.8 mm/s, lock push at 1 mm/s, park retraction 2 mm. None of these are applied here (the TPU profiles still have multitool
ramming on). The wipe-tower branch of the tool change (the thread used the purge station) and the PrusaSlicer 3 alpha printer preset, which contains the same stock
logic, were not changed. OrcaSlicer machine presets inherit the system G-code and have no copy of it.

## How to check it

Slice a small TPU + PLA print with several tool changes and look at the G-code: for the TPU tool the clean should read `M109 C195`
(`M109 C205` on layer 1) and a `G4 S8` line should follow `M104 S220`. On the printer, watch for tangling at the extruder after the first return
to the TPU tool and for how clean the nozzle is afterwards, since a hotter clean may ooze more. To go back, restore the printer `.ini` files from the previous commit.
