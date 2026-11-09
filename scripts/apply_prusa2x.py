import os, re, shutil, time, json, sys
HOME = os.path.expanduser('~'); RP = HOME + '/mnt/Roaming--PrusaSlicer/'; BP = HOME + '/mnt/PrusaSlicer-beta/'
TS = '20261106'
ini = RP + 'PrusaSlicer.ini'
age = time.time() - os.path.getmtime(ini)
if age < 120: sys.exit('ABORT: PrusaSlicer.ini changed %ds ago, PrusaSlicer may be running' % age)

C = ' @COREONEINDX HF0.4'
fil = {
 'GeeeTech PLA Matte Stone Gray @ MINIIS': 'GeeeTech PLA Matte Stone Gray @MINIIS',
 'GeeeTech PLA Silver (Silk) @ MINIIS': 'GeeeTech PLA Silver (Silk) @MINIIS',
 'Prusament Galaxy Black PLA @MINIIS': 'Prusament PLA Galaxy Black @MINIIS',
 'Prusament PLA (Galaxy Red) @COREONE': 'Prusament PLA Galaxy Red @COREONE',
 'PLA - SunLu White (Gee) - new 15mm3': 'Sunlu PLA White - Gee new 15mm3',
 'PLA - SunLu White (Gee) - new': 'Sunlu PLA White - Gee new',
 'PLA - Verbatim (IS)': 'Verbatim PLA - IS',
 'SUNLU PETG @COREONEINDX HF0.4 - FLATTENED': 'Sunlu PETG @COREONEINDX HF0.4 - FLATTENED',
 'SUNLU PLA @COREONEINDX HF0.4 - FLATTENED': 'Sunlu PLA @COREONEINDX HF0.4 - FLATTENED',
 'SUNLU PLA+ 2.0 @COREONEINDX HF0.4 - FLATTENED': 'Sunlu PLA+ 2.0 @COREONEINDX HF0.4 - FLATTENED',
}
for n in ['ColorMix Black','ColorMix Cyan','ColorMix Gold Glitter','ColorMix Magenta','ColorMix Silver Glitter','ColorMix White','ColorMix Yellow',
          'Galaxy Green','Galaxy Purple','Galaxy Red','Galaxy Silver','Prusa Galaxy Black','Prusa Orange']:
    fil['Prusament PLA ' + n] = 'Prusament PLA ' + n + C
prn = {'Prusa CORE One INDX 8T HF0.4 nozzle + Wiper + GECO': 'Prusa CORE One INDX 8T HF0.4 nozzle + Wiper + GEKO'}
renames = {'filament': fil, 'printer': prn}
archive = {'print': ['0.20mm STRUCTURAL @COREONE 0.4 - Copy', '0.40mm STRUCTURAL @COREONE HF0.8 - Copy'],
           'filament': ['Sunlu PETG @COREONE HF0.8 - Copy', 'bonkers_pla']}

# ---- preflight ----
for sub, mp in renames.items():
    existing = {f[:-4].lower() for f in os.listdir(RP + sub) if f.endswith('.ini')}
    for old, new in mp.items():
        assert os.path.exists('%s%s/%s.ini' % (RP, sub, old)), 'missing ' + old
        assert new.lower() not in existing or new.lower() == old.lower(), 'target exists ' + new
for sub, names in archive.items():
    for n in names: assert os.path.exists('%s%s/%s.ini' % (RP, sub, n)), 'missing ' + n
log = {'renamed': [], 'archived': [], 'created': [], 'beta_archived': []}

# ---- archive (reversible, nothing deleted) ----
for sub, names in archive.items():
    os.makedirs('%s_archive_%s/%s' % (RP, TS, sub), exist_ok=True)
    for n in names:
        dst = '%s_archive_%s/%s/%s.ini' % (RP, TS, sub, n)
        assert not os.path.exists(dst)
        os.rename('%s%s/%s.ini' % (RP, sub, n), dst); log['archived'].append(sub + '/' + n)

# ---- renames, two-step so case-only changes work on case-insensitive disks ----
for sub, mp in renames.items():
    tmp = {}
    for i, (old, new) in enumerate(mp.items()):
        t = '%s%s/.tmp_%d' % (RP, sub, i); os.rename('%s%s/%s.ini' % (RP, sub, old), t); tmp[t] = new
    for t, new in tmp.items():
        os.rename(t, '%s%s/%s.ini' % (RP, sub, new))
    log['renamed'] += [sub + ': ' + o + '  ->  ' + n for o, n in mp.items()]

# ---- update the selected presets in PrusaSlicer.ini (bytes, keep CRLF/UTF-8) ----
b = open(ini, 'rb').read(); n_changed = 0
def fix(m):
    global n_changed
    key, val = m.group(1).decode(), m.group(2).decode('utf-8')
    kind = 'printer' if key == 'printer' else 'filament'
    if val in renames[kind]:
        n_changed += 1; return m.group(1) + b' = ' + renames[kind][val].encode('utf-8')
    return m.group(0)
b2 = re.sub(rb'^(filament(?:_\d+)?|printer) = ([^\r\n]*)', fix, b, flags=re.M)
open(ini, 'wb').write(b2); log['ini_selection_lines_updated'] = n_changed

# ---- any remaining references to old names inside user presets? ----
allmap = {}; [allmap.update(m) for m in renames.values()]; stale = []
for sub in ('print', 'filament', 'printer', 'physical_printer'):
    for f in os.listdir(RP + sub):
        if not f.endswith('.ini'): continue
        txt = open('%s%s/%s' % (RP, sub, f), 'rb').read().decode('utf-8', 'replace')
        for old in allmap:
            if re.search(r'(^|[=;"])\s*"?' + re.escape(old) + r'"?\s*($|[;"\r])', txt, re.M): stale.append((sub + '/' + f, old))
log['stale_references'] = stale

# ---- add the new INDX filaments ----
for f in sorted(os.listdir(HOME + '/stage_out/filament')):
    dst = RP + 'filament/' + f
    assert not os.path.exists(dst), 'exists ' + f
    shutil.copyfile(HOME + '/stage_out/filament/' + f, dst); log['created'].append(f[:-4])

# ---- stale PrusaSlicer-beta presets -> archive ----
for sub in ('print', 'filament', 'printer'):
    os.makedirs('%s_archive_%s/%s' % (BP, TS, sub), exist_ok=True)
    for f in sorted(os.listdir(BP + sub)):
        if f.endswith('.ini'):
            os.rename('%s%s/%s' % (BP, sub, f), '%s_archive_%s/%s/%s' % (BP, TS, sub, f)); log['beta_archived'].append(sub + '/' + f[:-4])
json.dump(log, open(HOME + '/apply_prusa2x_log.json', 'w'), indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in log.items()}, indent=1))
print('stale references to old names:', stale if stale else 'none')
