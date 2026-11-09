import os, re, sys, collections, shutil
HOME = os.path.expanduser('~')
RP = HOME + '/mnt/Roaming--PrusaSlicer/'
STAGE = HOME + '/stage_out/filament/'
PLATFORM = {'filament_unloading_speed', 'filament_unloading_speed_start'}
IGN = {'filament_settings_id', 'inherits', 'compatible_printers', 'compatible_printers_condition',
       'compatible_prints', 'compatible_prints_condition'}

def rt(p): return open(p, 'rb').read().decode('utf-8', 'replace').replace('\r\n', '\n')

def parse_user(p):
    od = collections.OrderedDict(); header = []
    for line in rt(p).split('\n'):
        if line.startswith('#'): header.append(line); continue
        if ' = ' in line: k, _, v = line.partition(' = ')
        elif line.endswith(' ='): k, v = line[:-2], ''
        else: continue
        od[k.strip()] = v
    return od, header

def parse_vendor(p):
    secs = {}; cur = None
    for line in rt(p).split('\n'):
        s = line.strip()
        if not s or s[0] in ';#': continue
        m = re.match(r'^\[([a-z_]+):(.+)\]$', s)
        if m: cur = (m.group(1), m.group(2)); secs.setdefault(cur, collections.OrderedDict()); continue
        if s.startswith('['): cur = None; continue
        if cur and '=' in s:
            k, _, v = s.partition('='); secs[cur][k.strip()] = v.strip()
    return secs

SECS = parse_vendor(RP + 'vendor/PrusaResearch.ini')

def resolve(kind, name):
    key = (kind, name)
    if key not in SECS: raise KeyError(key)
    cfg = collections.OrderedDict()
    for par in [x.strip() for x in SECS[key].get('inherits', '').split(';') if x.strip()]:
        cfg.update(resolve(kind, par))
    for k, v in SECS[key].items():
        if k != 'inherits': cfg[k] = v
    return cfg

def norm(v):
    v = v.strip(); out = []
    for t in re.split(r'\s*[;,]\s*', v):
        try: out.append(repr(round(float(t), 6)))
        except ValueError: return v
    return tuple(out)
def eq(a, b): return norm(a) == norm(b)
def sh(v, n=70): return v if len(v) <= n else v[:n] + '...'

# ---------- resolver self-test on an existing, known-good user preset ----------
S, _ = parse_user(RP + 'filament/Prusament PLA @COREONEINDX HF0.4 - Color.ini')
Pi = resolve('filament', S['inherits'])
d = [k for k in S if k not in IGN and k in Pi and not eq(S[k], Pi[k])]
holes = [k for k in S if k not in IGN and k not in Pi]
print('SELF-TEST existing "Prusament PLA @COREONEINDX HF0.4 - Color" vs resolved parent:')
print('  keys differing from parent (should be the user\'s tweaks only):', [(k, sh(S[k], 30), sh(Pi[k], 30)) for k in d])
print('  keys not defined by parent (PrusaSlicer defaults):', len(holes), 'of', len(S))
print()

BUILDS = [
 ('Prusament PETG @COREONEINDX HF0.4 - GeeeTech', 'Prusament PETG @COREONE HF0.4 - GeeeTech', 'Prusament PETG @COREONEINDX HF0.4', 'Prusament PETG @COREONE HF0.4', None),
 ('Prusament PETG @COREONEINDX HF0.4 - ICE Rob', 'Prusament PETG @COREONE HF0.4 - ICE Rob', 'Prusament PETG @COREONEINDX HF0.4', 'Prusament PETG @COREONE HF0.4', None),
 ('Prusament PLA @COREONEINDX HF0.4 - GEKO', 'Prusament PLA @COREONE HF0.4 - GEKO', 'Prusament PLA @COREONEINDX HF0.4', 'Prusament PLA @COREONE HF0.4', None),
 ('Fiberlogy ASA @COREONEINDX HF0.4 - Matte Olive Green', 'Fiberlogy ASA @COREONE - Matte Olive Green', 'Prusament ASA @COREONEINDX HF0.4', 'Prusament ASA @COREONE', None),
 ('Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.06 flow', 'Ultrafuse TPU-95A @COREONE - 1.06 flow', 'Prusament TPU 95A @COREONEINDX HF0.4', 'Prusament TPU 95A @COREONE', None),
 ('Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.08 flow', 'Ultrafuse TPU-95A @COREONE - 1.08 flow', 'Prusament TPU 95A @COREONEINDX HF0.4', 'Prusament TPU 95A @COREONE', None),
 ('Sunlu PLA @COREONEINDX HF0.4 - 220-210 - FLATTENED', 'Sunlu PLA @COREONE HF0.4 - 220-210', None, 'Sunlu PLA @COREONE HF0.4', 'SUNLU PLA @COREONEINDX HF0.4 - FLATTENED'),
]

COLOR, COLOR_HDR = parse_user(RP + 'filament/Prusament PLA @COREONEINDX HF0.4 - Color.ini')
shutil.rmtree(HOME + '/stage_out', ignore_errors=True); os.makedirs(STAGE)
for new_name, src, indx_parent, base, template in BUILDS:
    S, header = parse_user(RP + 'filament/%s.ini' % src)
    Pc = resolve('filament', base)
    tweaks = [k for k in S if k not in IGN and k not in PLATFORM and k in Pc and not eq(S[k], Pc[k])]
    new = collections.OrderedDict()
    if template is None:
        Pi = resolve('filament', indx_parent)
        for k in S:
            if k in IGN: continue
            if k in tweaks: new[k] = S[k]
            elif k in Pi: new[k] = Pi[k]
            else: new[k] = S[k]
        new['filament_settings_id'] = S.get('filament_settings_id', '""')
        new['inherits'] = indx_parent
        new['compatible_printers'] = ''
        new['compatible_printers_condition'] = Pi.get('compatible_printers_condition', '')
        new['compatible_prints'] = Pi.get('compatible_prints', '')
        new['compatible_prints_condition'] = Pi.get('compatible_prints_condition', '')
        swapped = [k for k in S if k not in IGN and k not in tweaks and k in Pi and not eq(S[k], Pi[k])]
    else:
        T, header = parse_user(RP + 'filament/%s.ini' % template)
        new = collections.OrderedDict(T)
        for k in tweaks: new[k] = S[k]
        swapped = []
    # keep S key order (all user dumps share the same key set)
    added = [k for k in COLOR if k not in new]
    for k in added: new[k] = (Pi.get(k, COLOR[k]) if template is None else COLOR[k])
    ordered = collections.OrderedDict((k, new[k]) for k in sorted(new))
    if added: print('    (added %d keys missing from the older source dump: %s)' % (len(added), added))
    print('=== %s\n    source: %s | INDX parent: %s | CORE One base: %s%s' % (new_name, src, indx_parent, base, (' | template: ' + template) if template else ''))
    print('    your tweaks carried over (%d): %s' % (len(tweaks), [(k, sh(S[k], 28)) for k in tweaks if k not in ('start_filament_gcode',)] + ([('start_filament_gcode', sh(S['start_filament_gcode'], 60))] if 'start_filament_gcode' in tweaks else [])))
    if swapped: print('    INDX-parent values replacing CORE One ones (%d): %s' % (len(swapped), [(k, sh(S[k], 22), sh(Pi[k], 22)) for k in swapped][:14]))
    print('    compat condition: %s' % sh(ordered.get('compatible_printers_condition', ''), 120))
    lines = COLOR_HDR[:1] + ['%s = %s' % (k, v) for k, v in ordered.items()]
    open(STAGE + new_name + '.ini', 'wb').write(('\r\n'.join(lines) + '\r\n').encode('utf-8'))
print('\nstaged files:'); print('\n'.join(sorted(os.listdir(STAGE))))
