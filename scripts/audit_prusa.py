import os, re, sys, collections, itertools
root = sys.argv[1]
SECRET = re.compile(r'(key|password|secret|token|authorization|user)', re.I)

def parse_ini(path):
    d = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('#') or line.startswith(';') or '=' not in line or line.startswith('['):
                continue
            k, v = line.split('=', 1)
            d[k.strip()] = v.strip()
    return d

def vendor_names(path):
    names = collections.defaultdict(set)
    if not os.path.exists(path): return names
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.match(r'\[(print|filament|printer|sla_print|sla_material|physical_printer):(.+?)\]\s*$', line)
            if m: names[m.group(1)].add(m.group(2))
    return names

def load_dir(base, sub):
    out = {}
    p = os.path.join(base, sub)
    if not os.path.isdir(p): return out
    for fn in sorted(os.listdir(p)):
        if fn.endswith('.ini'):
            out[fn[:-4]] = parse_ini(os.path.join(p, fn))
    return out

IGN = {'filament_settings_id','print_settings_id','printer_settings_id','sla_print_settings_id','sla_material_settings_id'}

def report(label, base):
    print('='*100); print(label, base)
    vn = vendor_names(os.path.join(base, 'vendor', 'PrusaResearch.ini'))
    for sub in ('printer','print','filament'):
        presets = load_dir(base, sub)
        print('\n--- %s (%d)' % (sub, len(presets)))
        bad = []
        for name, d in presets.items():
            inh = d.get('inherits','')
            ok = ''
            if inh:
                parents = [x.strip() for x in inh.split(';') if x.strip()]
                miss = [x for x in parents if x not in vn[sub] and x not in presets]
                ok = 'OK' if not miss else 'BROKEN:' + ','.join(miss)
                if miss: bad.append((name, miss))
            else:
                ok = 'detached'
            cond = d.get('compatible_printers_condition','')
            cp = d.get('compatible_printers','')
            extra = ''
            if sub == 'filament':
                extra = 'type=%s vendor=%s T=%s/%s bed=%s/%s dens=%s cost=%s' % (d.get('filament_type'), d.get('filament_vendor'), d.get('first_layer_temperature'), d.get('temperature'), d.get('first_layer_bed_temperature'), d.get('bed_temperature'), d.get('filament_density'), d.get('filament_cost'))
            elif sub == 'print':
                extra = 'layer=%s' % d.get('layer_height')
            else:
                extra = 'model=%s variant=%s nozzles=%s' % (d.get('printer_model'), d.get('printer_variant'), d.get('nozzle_diameter'))
            print('* %s\n    inh=[%s] %s\n    cond=[%s] cp=[%s]\n    %s' % (name, inh, ok, cond[:160], cp[:80], extra))
        print('  >> broken inherits:', bad if bad else 'none')
        # near duplicates
        names = list(presets)
        pairs = []
        for a, b in itertools.combinations(names, 2):
            da, db = presets[a], presets[b]
            keys = (set(da) | set(db)) - IGN
            diff = sorted(k for k in keys if da.get(k) != db.get(k))
            if len(diff) <= 4: pairs.append((a, b, diff))
        print('  >> near-duplicate pairs (<=4 differing keys): %d' % len(pairs))
        for a, b, diff in pairs:
            print('     "%s"  ~  "%s"  diff=%s' % (a, b, diff))

report('PrusaSlicer 2.x', os.path.join(root, 'Roaming--PrusaSlicer'))
