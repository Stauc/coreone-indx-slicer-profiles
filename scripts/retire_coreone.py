import os, re, json, time, collections, sys
HOME = os.path.expanduser('~'); M = HOME + '/mnt/'
RP = M + 'Roaming--PrusaSlicer/'; OR = M + 'Roaming--OrcaSlicer/'; OF = OR + 'user/default/filament/'; OM = OR + 'user/default/machine/'
TS = '20261106'
for p in (RP + 'PrusaSlicer.ini', OR + 'OrcaSlicer.conf'):
    if time.time() - os.path.getmtime(p) < 120: sys.exit('ABORT: %s changed in the last 2 min - is the slicer open?' % p)
log = collections.OrderedDict()

# ---------- PrusaSlicer 2.x: archive CORE One (non-INDX) print + filament presets ----------
sel = {sub: sorted(f[:-4] for f in os.listdir(RP + sub) if f.endswith('.ini') and re.search(r'@COREONE(?!INDX)', f)) for sub in ('print', 'filament')}
assert len(sel['print']) == 10 and len(sel['filament']) == 12, {k: len(v) for k, v in sel.items()}
ini_txt = open(RP + 'PrusaSlicer.ini', 'rb').read().decode('utf-8', 'replace')
for sub, names in sel.items():
    for n in names: assert ('= ' + n + '\r') not in ini_txt, 'selected in PrusaSlicer.ini: ' + n
    os.makedirs('%s_archive_%s/%s' % (RP, TS, sub), exist_ok=True)
    for n in names:
        dst = '%s_archive_%s/%s/%s.ini' % (RP, TS, sub, n); assert not os.path.exists(dst)
        os.rename('%s%s/%s.ini' % (RP, sub, n), dst)
log['prusa2x_archived'] = sel

# ---------- Orca: carry the connection settings into INDX machines FIRST ----------
def rj(p): return json.loads(open(p, 'rb').read().decode('utf-8'), object_pairs_hook=collections.OrderedDict)
def wj(p, j): open(p, 'wb').write((json.dumps(collections.OrderedDict(sorted(j.items())), indent=4, ensure_ascii=False).replace('\n', '\r\n') + '\r\n').encode('utf-8'))
CONN = ['host_type', 'print_host', 'print_host_webui', 'printhost_authorization_type', 'printhost_user', 'printhost_password', 'printhost_apikey', 'printhost_port', 'printhost_cafile', 'printhost_ssl_ignore_revoke']
SYS = 'Prusa CORE One INDX 8T HF 0.4 nozzle'
made = []
for suffix, srcname in (('LAN', 'Prusa CORE One HF 0.4 nozzle - Copy'), ('Connect', 'Prusa CORE One 0.4 nozzle + wiper')):
    src = rj(OM + srcname + '.json'); name = SYS + ' - ' + suffix
    assert not os.path.exists(OM + name + '.json')
    j = collections.OrderedDict([('from', 'User'), ('inherits', SYS), ('is_custom_defined', '0'), ('name', name), ('printer_settings_id', name), ('version', src['version'])])
    for k in CONN:
        if k in src: j[k] = src[k]
    wj(OM + name + '.json', j)
    open(OM + name + '.info', 'wb').write(('sync_info = create\nuser_id = \nsetting_id = \nbase_id = \nupdated_time = %d\n' % int(time.time())).replace('\n', '\r\n').encode('utf-8'))
    made.append(name)
log['orca_machines_created'] = made

# ---------- Orca: new INDX filaments also list the two new machine names ----------
n_upd = 0
for f in sorted(os.listdir(OF)):
    if f.endswith('.json') and 'CORE One INDX' in f:
        j = rj(OF + f)
        if j.get('compatible_printers') == [SYS]:
            j['compatible_printers'] = [SYS] + made; wj(OF + f, j); n_upd += 1
log['orca_filaments_compat_updated'] = n_upd

# ---------- Orca: archive CORE One filaments + machines ----------
orca_sel = {'filament': sorted(f[:-5] for f in os.listdir(OF) if f.endswith('.json') and re.search(r'CORE One(?! INDX)', f)),
            'machine': sorted(f[:-5] for f in os.listdir(OM) if f.endswith('.json') and re.search(r'CORE One(?! INDX)', f))}
assert len(orca_sel['filament']) == 4 and len(orca_sel['machine']) == 5, {k: len(v) for k, v in orca_sel.items()}
for sub, names in orca_sel.items():
    d = OF if sub == 'filament' else OM
    os.makedirs('%s_archive_%s/%s' % (OR, TS, sub), exist_ok=True)
    for n in names:
        for ext in ('json', 'info'):
            dst = '%s_archive_%s/%s/%s.%s' % (OR, TS, sub, n, ext)
            if os.path.exists(dst): dst = dst.replace('.' + ext, '_2.' + ext)
            os.rename('%s%s.%s' % (d, n, ext), dst)
log['orca_archived'] = orca_sel
json.dump(log, open(HOME + '/retire_coreone_log.json', 'w'), indent=1)
print(json.dumps(log, indent=1))
