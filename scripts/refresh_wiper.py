#!/usr/bin/env python3
"""Refresh the four '+ Wiper' printer profiles to the installed vendor G-code; keep the extra wipe as commented-out lines. --write to apply."""
import sys, os, re, glob, shutil
sys.path.insert(0, os.path.expanduser('~/scripts'))
from lib2x import parse_user, resolve, RP
WRITE = '--write' in sys.argv
BK = RP + '_backup_wiper_refresh_20261106/printer/'
M115 = re.compile(r'M115 U[0-9.]+\+[0-9]+')
ANCHOR = 'M83 ; extruder relative mode\\n  G12 S91 ; Exit cleaning station'
OLD_BLOCK = 'M83 ; extruder relative mode\\n\\n  ;Additional Cleaning\\n  M400\\n  G12 S2 ; Quick clean\\n\\n  G12 S91 ; Exit cleaning station'
NEW_BLOCK = ('M83 ; extruder relative mode\\n\\n'
             '  ;Additional Cleaning - DISABLED for testing, remove the leading semicolon on the next two lines to re-enable\\n'
             '  ;M400\\n  ;G12 S2 ; Quick clean\\n\\n  G12 S91 ; Exit cleaning station')

def write_ini(path, od, header):
    lines = [header] + [f'{k} = {od[k]}' for k in sorted(od)]
    open(path, 'wb').write(('\r\n'.join(lines) + '\r\n').encode('utf-8'))

files = sorted(glob.glob(RP + 'printer/*Wiper*.ini'))
assert len(files) == 4, files
plan = []
for f in files:
    S, h = parse_user(f)
    # writer must reproduce the file byte for byte before I trust it
    write_ini('/tmp/rt_w.ini', S, h[0])
    assert open('/tmp/rt_w.ini', 'rb').read() == open(f, 'rb').read(), 'round-trip failed ' + f
    V = resolve('printer', S['inherits'])
    geco = 'GECO' in os.path.basename(f)
    old_tc, old_start, old_layer = S['toolchange_gcode'], S['start_gcode'], S['layer_gcode']
    # --- toolchange: vendor + (commented) extra wipe; prove the old file was exactly vendor + active block
    assert V['toolchange_gcode'].count(ANCHOR) == 1
    active = V['toolchange_gcode'].replace(ANCHOR, OLD_BLOCK) + '\\n'
    assert active == old_tc, 'old toolchange is not vendor+block: ' + f
    new_tc = V['toolchange_gcode'].replace(ANCHOR, NEW_BLOCK)
    # --- start: vendor, or (GECO) old GECO text with only the firmware line refreshed
    vm = M115.search(V['start_gcode']).group()
    if geco:
        assert len(M115.findall(old_start)) == 1
        new_start = M115.sub(vm, old_start)
    else:
        assert M115.sub(vm, old_start) == V['start_gcode'], 'old start differs from vendor by more than the M115 line: ' + f
        new_start = V['start_gcode']
    new_layer = V['layer_gcode']
    N = dict(S); N.update(toolchange_gcode=new_tc, start_gcode=new_start, layer_gcode=new_layer)
    plan.append((f, h[0], S, N, geco))
    print(os.path.basename(f), '| GECO' if geco else '| plain', '| start:', M115.search(old_start).group(), '->', vm, '| layer_gcode differs:', old_layer != new_layer,
          '| toolchange: wipe lines now commented')
print('all pre-checks passed')
if not WRITE: sys.exit(0)
os.makedirs(BK, exist_ok=False)
for f, hdr, S, N, geco in plan:
    shutil.copy2(f, BK + os.path.basename(f))
    write_ini(f, N, hdr)
print('written; originals in', BK)
