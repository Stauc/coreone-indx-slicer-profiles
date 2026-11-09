#!/usr/bin/env python3
"""Add a FLEX-only hotter cleaning temperature and an 8 s soak to the INDX printer presets (PrusaSlicer 2.x).

Idea and numbers (eject temperature = target - 25 C, G4 S8 soak after the nozzle reaches temperature)
come from a report by Kiddocteur on the Prusa forum:
https://forum.prusa3d.com/forum/prusa-indx-general-discussion-announcements-and-releases/solved-tpu-tangling-at-the-extruder-after-indx-tool-changes-the-nozzle-was-too-cold-during-cleaning/
Only filaments with filament_type = FLEX are affected. Usage: apply_flex_toolchange.py <printer dir> [backup dir]
"""
import glob, os, shutil, sys

SRC = ('source: Prusa forum INDX thread TPU tangling at the extruder after INDX tool changes '
       'by Kiddocteur')


def raw(s):
    """G-code values are stored on one line with literal backslash-n for newlines."""
    return s.replace('\n', '\\n')


EDITS = {
    'toolchange_gcode': [
        # hotter clean for FLEX, placed after the first-layer target_temp override
        (
            '  {if layer_z <= (first_layer_height + 0.0001)}\n'
            '    {target_temp = first_layer_temperature[next_extruder]}\n'
            '  {endif}\n',
            '  {if layer_z <= (first_layer_height + 0.0001)}\n'
            '    {target_temp = first_layer_temperature[next_extruder]}\n'
            '  {endif}\n'
            '\n'
            '  {if filament_type[next_extruder]=="FLEX"}\n'
            '    {eject_temp = target_temp - 25}\n'
            '  {endif}\n',
        ),
        # soak in the purge-station branch, after the nozzle reached target and before the deretract push
        (
            '    M109 C{target_temp}\n'
            '    M104 S{target_temp}\n'
            '\n'
            '    {if tool_init[next_extruder] == 1}\n',
            '    M109 C{target_temp}\n'
            '    M104 S{target_temp}\n'
            '\n'
            '    {if filament_type[next_extruder]=="FLEX"}\n'
            '      G4 S8 ; FLEX soak - let the TPU melt before pushing - ' + SRC + '\n'
            '    {endif}\n'
            '\n'
            '    {if tool_init[next_extruder] == 1}\n',
        ),
    ],
    'start_gcode': [
        (
            '{if filament_type[initial_tool]=="FLEX"}\n'
            '  {tc_deretract_speed = 60*10}\n'
            '{endif}\n',
            '{if filament_type[initial_tool]=="FLEX"}\n'
            '  {tc_deretract_speed = 60*10}\n'
            '  {eject_temp = target_temp - 25}\n'
            '{endif}\n',
        ),
        (
            'M109 C{target_temp}\n'
            '\n'
            'M104 S{target_temp}\n'
            '\n'
            'G1 E{deretract_length} F{tc_deretract_speed}',
            'M109 C{target_temp}\n'
            '\n'
            'M104 S{target_temp}\n'
            '\n'
            '{if filament_type[initial_tool]=="FLEX"}\n'
            '  G4 S8 ; FLEX soak - let the TPU melt before pushing - ' + SRC + '\n'
            '{endif}\n'
            '\n'
            'G1 E{deretract_length} F{tc_deretract_speed}',
        ),
    ],
}


def patch_file(path):
    data = open(path, encoding='utf-8', newline='').read()
    lines = data.split('\r\n')
    done = {}
    for i, line in enumerate(lines):
        key = line.split(' = ', 1)[0]
        if key in EDITS:
            val = line
            for old, new in EDITS[key]:
                o, n = raw(old), raw(new)
                if n in val:
                    done[(key, old[:30])] = 'already'
                    continue
                if val.count(o) != 1:
                    raise SystemExit('%s: %s snippet found %d times (expected 1): %r'
                                     % (os.path.basename(path), key, val.count(o), old[:40]))
                val = val.replace(o, n)
                done[(key, old[:30])] = 'patched'
            lines[i] = val
    open(path, 'w', encoding='utf-8', newline='').write('\r\n'.join(lines))
    return done


if __name__ == '__main__':
    pdir = sys.argv[1]
    bdir = sys.argv[2] if len(sys.argv) > 2 else None
    for p in sorted(glob.glob(os.path.join(pdir, '*INDX*.ini'))):
        if bdir:
            os.makedirs(bdir, exist_ok=True)
            b = os.path.join(bdir, os.path.basename(p))
            if not os.path.exists(b):
                shutil.copy2(p, b)
        res = patch_file(p)
        print(os.path.basename(p), '->', sorted(set(res.values())), len(res), 'edits')
