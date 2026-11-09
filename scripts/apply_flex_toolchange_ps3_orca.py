#!/usr/bin/env python3
"""FLEX/TPU-only hotter cleaning + soak for the INDX tool change - PrusaSlicer 3 alpha and OrcaSlicer variants.

Same idea as scripts/apply_flex_toolchange.py (PrusaSlicer 2.x): clean at target - 25 C instead of target - 60 C and wait 8 s
before the deretract push. Credit: a report by Kiddocteur on the Prusa forum, see docs/tpu-toolchange.md.

  apply_flex_toolchange_ps3_orca.py ps3  <printer yaml> [backup dir]
  apply_flex_toolchange_ps3_orca.py orca <system Prusa.opc> <machine dir> [backup dir]

PS3: only toolchange_gcode is patched (the start G-code is inherited from the vendor bundle and not overridden).
Orca: the user machine presets inherit their G-code from the system preset, so the stock start and change-filament G-code are
copied out of the system bundle, patched, and stored as overrides (machine_start_gcode, change_filament_gcode).
"""
import glob, json, os, re, shutil, sys

SRC = ('source: Prusa forum INDX thread TPU tangling at the extruder after INDX tool changes by Kiddocteur')


def edits(kind, tpu):
    """(old, new) snippet pairs. kind: ps3-change | orca-change | orca-start. tpu = filament type string."""
    q = '"%s"' % tpu
    soak = 'G4 S8 ; %s soak - let the TPU melt before pushing - %s' % (tpu, SRC)
    if kind == 'ps3-change':
        a = ('  {if layer_z <= (first_layer_height + 0.0001)}\n'
             '    {target_temp = first_layer_temperature[next_extruder]}\n'
             '  {endif}\n')
        b = ('    M109 C{target_temp}\n    M104 S{target_temp}\n\n    {if tool_init[next_extruder] == 1}\n')
        return [
            (a, a + '\n  {if filament_type[next_extruder]==%s}\n    {eject_temp = target_temp - 25}\n  {endif}\n' % q),
            (b, '    M109 C{target_temp}\n    M104 S{target_temp}\n\n'
                '    {if filament_type[next_extruder]==%s}\n      %s\n    {endif}\n\n'
                '    {if tool_init[next_extruder] == 1}\n' % (q, soak)),
        ]
    if kind == 'orca-change':
        a = ('  {if layer_z <= (initial_layer_print_height + 0.0001)}\n'
             '    {target_temp = nozzle_temperature_initial_layer[next_extruder]}\n'
             '  {endif}\n')
        b = '    M109 C{target_temp}\n    M104 S{target_temp}\n\n    G1 E{deretract_length} F{tc_deretract_speed}\n'
        return [
            (a, a + '\n  {if filament_type[next_extruder]==%s}\n    {eject_temp = target_temp - 25}\n  {endif}\n' % q),
            (b, '    M109 C{target_temp}\n    M104 S{target_temp}\n\n'
                '    {if filament_type[next_extruder]==%s}\n      %s\n    {endif}\n\n'
                '    G1 E{deretract_length} F{tc_deretract_speed}\n' % (q, soak)),
        ]
    if kind == 'orca-start':
        a = '{if filament_type[initial_tool]==%s}\n  {tc_deretract_speed = 60*10}\n{endif}\n' % q
        b = 'M109 C{target_temp}\n\nM104 S{target_temp}\n\nG1 E{deretract_length} F{tc_deretract_speed}'
        return [
            (a, '{if filament_type[initial_tool]==%s}\n  {tc_deretract_speed = 60*10}\n  {eject_temp = target_temp - 25}\n{endif}\n' % q),
            (b, 'M109 C{target_temp}\n\nM104 S{target_temp}\n\n'
                '{if filament_type[initial_tool]==%s}\n  %s\n{endif}\n\n'
                'G1 E{deretract_length} F{tc_deretract_speed}' % (q, soak)),
        ]
    raise ValueError(kind)


def apply_edits(text, pairs, label):
    crlf = '\r\n' in text
    for old, new in pairs:
        if crlf:
            old, new = old.replace('\n', '\r\n'), new.replace('\n', '\r\n')
        if new in text:
            continue
        if text.count(old) != 1:
            raise SystemExit('%s: snippet found %d times (expected 1): %r' % (label, text.count(old), old[:50]))
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------- PrusaSlicer 3 alpha
def patch_ps3(path, backup=None):
    import yaml
    raw = open(path, encoding='utf-8', newline='').read()
    before = yaml.safe_load(raw)['variants'][0]['values']['toolchange_gcode']
    want = apply_edits(before, edits('ps3-change', 'FLEX'), 'PS3 value')

    def yq(s):
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    pairs = [(yq(o), yq(n)) for o, n in edits('ps3-change', 'FLEX')]
    if backup:
        os.makedirs(backup, exist_ok=True)
        b = os.path.join(backup, os.path.basename(path))
        if not os.path.exists(b):
            shutil.copy2(path, b)
    new_raw = raw
    for o, n in pairs:
        if n in new_raw:
            continue
        if new_raw.count(o) != 1:
            raise SystemExit('PS3 raw: snippet found %d times (expected 1)' % new_raw.count(o))
        new_raw = new_raw.replace(o, n)
    after = yaml.safe_load(new_raw)['variants'][0]['values']['toolchange_gcode']
    assert after == want, 'PS3: parsed result differs from expected'
    open(path, 'w', encoding='utf-8', newline='').write(new_raw)
    print('PS3 patched:', os.path.basename(path), '(+%d chars)' % (len(after) - len(before)))


# ---------------------------------------------------------------- OrcaSlicer
def orca_stock(opc):
    """Return (start, change) stock INDX G-code strings from the system bundle (records are length-prefixed)."""
    b = open(opc, 'rb').read()
    ok = set([9, 10, 13] + list(range(32, 127)))
    found = {}
    for m in re.finditer(rb'eject_temp', b):
        s = m.start()
        while s > 0 and (b[s - 1] in ok or b[s - 1] >= 0x80):
            s -= 1
        e = m.start()
        while e < len(b) and (b[e] in ok or b[e] >= 0x80):
            e += 1
        for s2 in range(max(8, s - 3), m.start()):
            if int.from_bytes(b[s2 - 8:s2], 'little') in (e - s2, e - s2 - 1):
                n = int.from_bytes(b[s2 - 8:s2], 'little')
                found[(s2, s2 + n)] = b[s2:s2 + n].decode('utf-8')
                break
    start = [t for t in found.values() if 'Clean and prime' in t]
    change = [t for t in found.values() if 'Change Tool' in t]
    if len(start) != 1 or len(change) != 1:
        raise SystemExit('could not isolate stock start/change G-code in %s (%d/%d)' % (opc, len(start), len(change)))
    return start[0], change[0]


def orca_patched(opc):
    start, change = orca_stock(opc)
    return (apply_edits(start, edits('orca-start', 'TPU'), 'Orca start'),
            apply_edits(change, edits('orca-change', 'TPU'), 'Orca change'))


def dump_like(raw, obj):
    nl = '\r\n' if '\r\n' in raw else '\n'
    m = re.search(r'\n([ \t]+)"', raw)
    indent = m.group(1) if m else '    '
    srt = list(obj.keys()) == sorted(obj.keys())
    out = json.dumps(obj, indent=indent, sort_keys=srt, ensure_ascii=False).replace('\n', nl)
    if raw.endswith(nl):
        out += nl
    return out


def patch_orca(machine_dir, opc, backup=None):
    start, change = orca_patched(opc)
    for p in sorted(glob.glob(os.path.join(machine_dir, '*INDX*.json'))):
        raw = open(p, encoding='utf-8', newline='').read()
        obj = json.loads(raw)
        if dump_like(raw, obj) != raw:
            raise SystemExit('%s: round-trip formatting differs, refusing to rewrite' % os.path.basename(p))
        if obj.get('machine_start_gcode') == start and obj.get('change_filament_gcode') == change:
            print('Orca already patched:', os.path.basename(p))
            continue
        if backup:
            os.makedirs(backup, exist_ok=True)
            b = os.path.join(backup, os.path.basename(p))
            if not os.path.exists(b):
                shutil.copy2(p, b)
        obj['machine_start_gcode'] = start
        obj['change_filament_gcode'] = change
        open(p, 'w', encoding='utf-8', newline='').write(dump_like(raw, obj))
        print('Orca patched:', os.path.basename(p))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'ps3' and len(a) >= 2:
        patch_ps3(a[1], a[2] if len(a) > 2 else None)
    elif a and a[0] == 'orca' and len(a) >= 3:
        patch_orca(a[2], a[1], a[3] if len(a) > 3 else None)
    else:
        sys.exit(__doc__)
