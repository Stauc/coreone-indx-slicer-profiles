import os, json, glob, shutil, time
D = os.path.expanduser('~/mnt/Roaming--OrcaSlicer/user/default/process/')
bk = os.path.expanduser('~/mnt/Roaming--OrcaSlicer/_backup_20261109_before_gyroid10/'); os.makedirs(bk, exist_ok=True)
def dump(path, j, like):
    raw = open(like, 'rb').read() if os.path.exists(like) else b''
    tab = raw.startswith(b'{\n\t') or raw.startswith(b'{\r\n\t')
    s = json.dumps(j, indent='\t' if tab else 4, sort_keys=True)
    nl = '\r\n' if b'\r\n' in raw else ('\n' if tab else '\r\n')
    open(path, 'wb').write((s.replace('\n', nl) + nl).encode('utf-8'))
changed = []; skipped = []
for f in sorted(glob.glob(D + '*.json')):
    j = json.load(open(f, encoding='utf-8')); n = os.path.basename(f)[:-5]
    if j.get('spiral_mode') in ('1', 1):
        skipped.append(n); continue
    old = (j.get('sparse_infill_density'), j.get('sparse_infill_pattern'))
    shutil.copy(f, bk + os.path.basename(f))
    j['sparse_infill_density'] = '10%'; j['sparse_infill_pattern'] = 'gyroid'
    dump(f, j, f); changed.append((n, old))
# user copies of the system INDX presets that have no user version yet
now = int(time.time()); made = []
for base in ['0.10mm Fine @Prusa CORE One INDX HF 0.4', '0.15mm Detail @Prusa CORE One INDX HF 0.4', '0.25mm Draft @Prusa CORE One INDX HF 0.4']:
    name = base + ' - Gyroid'
    if os.path.exists(D + name + '.json'): continue
    j = {'from': 'User', 'inherits': base, 'name': name, 'print_settings_id': name, 'sparse_infill_density': '10%', 'sparse_infill_pattern': 'gyroid', 'version': '2.4.0.18'}
    dump(D + name + '.json', j, D + '0.20mm Balanced @Prusa CORE One INDX HF 0.4 - Gyroid.json')
    open(D + name + '.info', 'wb').write(f'sync_info = \nuser_id = \nsetting_id = \nbase_id = \nupdated_time = 0\n'.encode())
    made.append(name)
print('CHANGED'); [print('  ', n, o, '-> 10% gyroid') for n, o in changed]
print('SKIPPED (spiral vase, 0% infill):'); [print('  ', n) for n in skipped]
print('NEW user copies of system presets:'); [print('  ', n) for n in made]
print('backups in', bk)
