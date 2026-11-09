import os, re, json, time, collections, sys
HOME = os.path.expanduser('~')
exec(open(HOME + '/scripts/indx_build.py').read().split('# ---------- resolver self-test')[0])
OROOT = HOME + '/mnt/Roaming--OrcaSlicer/'
OF = OROOT + 'user/default/filament/'
TS = '20261106'
age = time.time() - os.path.getmtime(OROOT + 'OrcaSlicer.conf')
print('OrcaSlicer.conf last changed %.1f h ago' % (age / 3600))

# round-trip check: our JSON writer must reproduce Orca's own formatting byte for byte
for f in sorted(os.listdir(OF)):
    if f.endswith('.json'):
        raw = open(OF + f, 'rb').read().decode('utf-8')
        j = json.loads(raw, object_pairs_hook=collections.OrderedDict)
        assert json.dumps(j, indent=4, ensure_ascii=False).replace('\n', '\r\n') + '\r\n' == raw, 'format mismatch ' + f
print('JSON round-trip OK for all existing filament files')

def info_text(base_id, kind): return ('sync_info = %s\nuser_id = \nsetting_id = \nbase_id = %s\nupdated_time = %d\n' % (kind, base_id, int(time.time()))).replace('\n', '\r\n')
def write_json(path, j): open(path, 'wb').write((json.dumps(j, indent=4, ensure_ascii=False).replace('\n', '\r\n') + '\r\n').encode('utf-8'))

# ---- 1) archive TEST preset, rename safe ones ----
ARC = OROOT + '_archive_%s/filament/' % TS; os.makedirs(ARC, exist_ok=True)
for ext in ('json', 'info'):
    if os.path.exists(OF + 'Generic PETG @System - TEST.' + ext):
        os.rename(OF + 'Generic PETG @System - TEST.' + ext, ARC + 'Generic PETG @System - TEST.' + ext)
assert os.path.exists(ARC + 'Generic PETG @System - TEST.json')
renames = {
 'GeeeTech PLA Matte Stone Gray @MiniIS': 'GeeeTech PLA Matte Stone Gray @MINIIS',
 'GeeeTech PLA Silver (Silk) @MiniIS': 'GeeeTech PLA Silver (Silk) @MINIIS',
 'Prusament Galaxy Black PLA @MINIIS': 'Prusament PLA Galaxy Black @MINIIS',
 'SUNLU PETG @System - HS': 'Sunlu PETG @CORE One HF 0.8 - HS',
}
for old, new in renames.items():
    j = json.loads(open(OF + old + '.json', 'rb').read().decode('utf-8'), object_pairs_hook=collections.OrderedDict)
    info = open(OF + old + '.info', 'rb').read()
    os.makedirs(ARC + 'renamed_originals', exist_ok=True)
    for ext in ('json', 'info'): os.rename(OF + old + '.' + ext, ARC + 'renamed_originals/' + old + '.' + ext)
    assert not os.path.exists(OF + new + '.json'), 'target exists ' + new
    j['name'] = new
    if 'filament_settings_id' in j: j['filament_settings_id'] = [new]
    write_json(OF + new + '.json', j)
    open(OF + new + '.info', 'wb').write(info)
print('renamed in Orca:', len(renames))

# ---- 2) new INDX 8T filaments ----
MACH = 'Prusa CORE One INDX 8T HF 0.4 nozzle'
MAP = [('extrusion_multiplier', ['filament_flow_ratio']), ('temperature', ['nozzle_temperature']),
       ('first_layer_temperature', ['nozzle_temperature_initial_layer']),
       ('bed_temperature', ['hot_plate_temp', 'textured_plate_temp']),
       ('first_layer_bed_temperature', ['hot_plate_temp_initial_layer', 'textured_plate_temp_initial_layer']),
       ('filament_max_volumetric_speed', ['filament_max_volumetric_speed']), ('filament_density', ['filament_density']),
       ('filament_cost', ['filament_cost']), ('filament_colour', ['default_filament_colour']), ('filament_vendor', ['filament_vendor']),
       ('min_fan_speed', ['fan_min_speed']), ('max_fan_speed', ['fan_max_speed']), ('disable_fan_first_layers', ['close_fan_the_first_x_layers']),
       ('fan_below_layer_time', ['fan_cooling_layer_time']), ('slowdown_below_layer_time', ['slow_down_layer_time']),
       ('min_print_speed', ['slow_down_min_speed']), ('bridge_fan_speed', ['overhang_fan_speed']),
       ('filament_retract_length', ['filament_retraction_length']), ('filament_retract_speed', ['filament_retraction_speed']),
       ('filament_deretract_speed', ['filament_deretraction_speed']), ('filament_type', ['filament_type'])]
TYPE = {'FLEX': 'TPU'}
def unq(v): return v.strip().strip('"')
def good(v): return v not in ('', 'nil') and not v.endswith('%')

NEW = [  # (orca name, prusa preset, orca parent, mode, indx prusa parent for delta)
 ('Prusament PETG @Prusa CORE One INDX - GeeeTech', 'Prusament PETG @COREONEINDX HF0.4 - GeeeTech', 'Prusament PETG @Prusa CORE One INDX', 'delta', 'Prusament PETG @COREONEINDX HF0.4', 'GFSA04'),
 ('Prusament PETG @Prusa CORE One INDX - ICE Rob', 'Prusament PETG @COREONEINDX HF0.4 - ICE Rob', 'Prusament PETG @Prusa CORE One INDX', 'delta', 'Prusament PETG @COREONEINDX HF0.4', 'GFSA04'),
 ('Prusament PLA @Prusa CORE One INDX - GEKO', 'Prusament PLA @COREONEINDX HF0.4 - GEKO', 'Prusament PLA @Prusa CORE One INDX', 'delta', 'Prusament PLA @COREONEINDX HF0.4', 'GFSA04'),
 ('Sunlu PLA @Prusa CORE One INDX - 220-210', 'Sunlu PLA @COREONEINDX HF0.4 - 220-210 - FLATTENED', 'Generic PLA @Prusa CORE One INDX', 'full', None, ''),
 ('Fiberlogy ASA @Prusa CORE One INDX - Matte Olive Green', 'Fiberlogy ASA @COREONEINDX HF0.4 - Matte Olive Green', 'Generic ABS @Prusa CORE One INDX', 'full', None, ''),
 ('Ultrafuse TPU-95A @Prusa CORE One INDX - 1.06 flow', 'Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.06 flow', 'Generic TPU @Prusa CORE One', 'full', None, ''),
 ('Ultrafuse TPU-95A @Prusa CORE One INDX - 1.08 flow', 'Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.08 flow', 'Generic TPU @Prusa CORE One', 'full', None, ''),
]
for oname, pname, parent, mode, ipar, base_id in NEW:
    S, _ = parse_user(RP + 'filament/%s.ini' % pname)
    Pi = resolve('filament', ipar) if ipar else {}
    take = {k for k in S if mode == 'full' or (k in Pi and not eq(S[k], Pi[k]))}
    j = collections.OrderedDict()
    j.update({'compatible_printers': [MACH], 'filament_settings_id': [oname], 'from': 'User', 'inherits': parent,
              'is_custom_defined': '0', 'name': oname, 'version': '2.3.1.0'})
    for pk, oks in MAP:
        if pk not in take or pk not in S: continue
        v = unq(S[pk])
        if not good(v) and pk not in ('filament_vendor',): continue
        if pk == 'filament_type': v = TYPE.get(v, v)
        if pk == 'filament_type' and mode == 'delta': continue
        for ok in oks: j[ok] = [v]
    if 'start_filament_gcode' in take or mode == 'full':
        m = re.search(r'M572 S([0-9.]+)', S.get('start_filament_gcode', ''))
        if m and float(m.group(1)) > 0: j['enable_pressure_advance'] = ['1']; j['pressure_advance'] = [m.group(1)]
    j = collections.OrderedDict(sorted(j.items()))
    p = OF + oname
    assert not os.path.exists(p + '.json'), 'exists ' + oname
    write_json(p + '.json', j); open(p + '.info', 'wb').write(info_text(base_id, 'create').encode('utf-8'))
    print('\n+ %s\n    parent: %s | mode: %s | overrides: %s' % (oname, parent, mode, {k: v[0] for k, v in j.items() if isinstance(v, list) and k not in ('compatible_printers', 'filament_settings_id')}))

# ---- verify ----
bad = 0
for f in os.listdir(OF):
    if f.endswith('.json'):
        try: json.load(open(OF + f, encoding='utf-8'))
        except Exception as e: bad += 1; print('BAD JSON', f, e)
print('\nOrca user filaments now:', len([f for f in os.listdir(OF) if f.endswith('.json')]), 'json /', len([f for f in os.listdir(OF) if f.endswith('.info')]), 'info; parse errors:', bad)
