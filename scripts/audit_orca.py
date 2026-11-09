import os, sys, json, glob
base = os.path.join(sys.argv[1], 'Roaming--OrcaSlicer', 'user', 'default')
for sub in ('machine', 'filament', 'process'):
    d = os.path.join(base, sub)
    jsons = sorted(f[:-5] for f in os.listdir(d) if f.endswith('.json')) if os.path.isdir(d) else []
    infos = set(f[:-5] for f in os.listdir(d) if f.endswith('.info')) if os.path.isdir(d) else set()
    print('--- %s: %d json, %d info' % (sub, len(jsons), len(infos)))
    print('   json without .info:', [j for j in jsons if j not in infos])
    print('   info without .json:', sorted(infos - set(jsons)))
    for n in jsons:
        try:
            j = json.load(open(os.path.join(d, n + '.json'), encoding='utf-8'))
        except Exception as e:
            print('* %s  PARSE ERROR %s' % (n, e)); continue
        if sub == 'filament':
            print('* %s | inh=[%s] type=%s vendor=%s nozzleT=%s bed=%s compat=%s' % (n, j.get('inherits'), j.get('filament_type'), j.get('filament_vendor'), j.get('nozzle_temperature'), j.get('hot_plate_temp') or j.get('textured_plate_temp'), j.get('compatible_printers')))
        elif sub == 'machine':
            print('* %s | inh=[%s] model=%s variant=%s nozzle=%s' % (n, j.get('inherits'), j.get('printer_model'), j.get('printer_variant'), j.get('nozzle_diameter')))
        else:
            print('* %s | inh=[%s] layer=%s' % (n, j.get('inherits'), j.get('layer_height')))
