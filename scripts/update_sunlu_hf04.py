import os, re, json, shutil, time, sys
sys.path.insert(0, os.path.expanduser('~/scripts'))
H = os.path.expanduser('~/mnt/')
PS2 = H + 'Roaming--PrusaSlicer/filament/Sunlu High Speed Matte PETG @COREONEINDX HF0.4.ini'
PS3 = H + 'PrusaSlicer3-dev/presets/user/prusa-research-fff/PrusaResearch/filament-Sunlu High Speed Matte PETG @COREONEINDX HF0.4.yaml'
OJ = H + 'Roaming--OrcaSlicer/user/default/filament/Sunlu High Speed Matte PETG @Prusa CORE One INDX.json'
OI = OJ[:-5] + '.info'
OLD = re.compile(r'Cap 22 mm3/s at 255 C:.*?Raise the cap with a max-flow test\.')
NEW = ('Max-flow test on T1 (0.4 HF, 255 C, ramp up to 34.9 mm3/s): clean to the top, so cap 30 (about 85 percent of the tested top; the real limit is higher). '
       '250/245 C because the spool lists 240-255 C for 100-300 mm/s and the print looked better at the fast end, so 255 C is hot for slow parts. PA 0.048 from the Sunlu PETG tune.')
bk = H + 'Roaming--OrcaSlicer/_backup_20261109_sunlu_hf04/'; os.makedirs(bk, exist_ok=True)
for p in (PS2, PS3, OJ): shutil.copy(p, bk + os.path.basename(p))
# PS 2.x ini (CRLF)
t = open(PS2, 'rb').read().decode('utf-8')
for k, v in (('temperature', '250'), ('first_layer_temperature', '245'), ('filament_max_volumetric_speed', '30')):
    t, n = re.subn(r'(?m)^%s = [^\r\n]*' % k, '%s = %s' % (k, v), t); assert n == 1, k
t, n = OLD.subn(NEW, t); assert n == 1
open(PS2, 'wb').write(t.encode('utf-8'))
# PS3 yaml (LF)
y = open(PS3, 'rb').read().decode('utf-8')
for k, v in (('temperature', '250'), ('first_layer_temperature', '245'), ('filament_max_volumetric_speed', '30')):
    y, n = re.subn(r'(?m)^(    %s): [^\r\n]*' % k, r'\1: %s' % v, y); assert n == 1, k
y, n = OLD.subn(NEW.replace("'", "''"), y); assert n == 1
open(PS3, 'wb').write(y.encode('utf-8'))
# Orca json (CRLF) + info
j = json.load(open(OJ, encoding='utf-8'))
j['nozzle_temperature'] = ['250']; j['nozzle_temperature_initial_layer'] = ['245']; j['filament_max_volumetric_speed'] = ['30']
j['filament_notes'] = [OLD.sub(NEW, j['filament_notes'][0])]; assert 'Max-flow test on T1' in j['filament_notes'][0]
open(OJ, 'wb').write((json.dumps(j, indent=4, sort_keys=True).replace('\n', '\r\n') + '\r\n').encode('utf-8'))
i = open(OI, 'rb').read().decode(); i = re.sub(r'updated_time = \d+', 'updated_time = %d' % int(time.time()), i); open(OI, 'wb').write(i.encode())
print('updated; backups in', bk)
