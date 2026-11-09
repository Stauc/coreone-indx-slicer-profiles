#!/usr/bin/env python3
"""Build OrcaSlicer user presets for the mixed-nozzle INDX 8T. Use --write to apply; default is a dry run."""
import sys, os, json, time, shutil, collections, glob
sys.path.insert(0, os.path.expanduser('~/scripts'))
from lib2x import parse_user

WRITE = '--write' in sys.argv
HOME = os.path.expanduser('~')
OR = HOME + '/mnt/Roaming--OrcaSlicer/'
UD = OR + 'user/default/'
PS = HOME + '/mnt/Roaming--PrusaSlicer/print/'
BK = OR + '_backup_orca_mixed_20261106/'
NOW = int(time.time())

SYS_M = 'Prusa CORE One INDX 8T HF 0.4 nozzle'
OLD_M = [SYS_M, SYS_M + ' - LAN', SYS_M + ' - Connect']
NEW_M = ['Prusa CORE One INDX 8T Mixed Nozzles - LAN', 'Prusa CORE One INDX 8T Mixed Nozzles - Connect']
NOZ = ['0.4'] * 6 + ['0.25', '1']
MINL = ['0.07'] * 6 + ['0.05', '0.25']
MAXL = ['0.3'] * 6 + ['0.15', '0.75']
VERSION_P = '2.3.1.0'

def dump(d):
    return (json.dumps(d, indent=4, ensure_ascii=False, sort_keys=True).replace('\n', '\r\n') + '\r\n').encode('utf-8')
def info():
    return ('sync_info = create\r\nuser_id = \r\nsetting_id = \r\nbase_id = \r\nupdated_time = %d\r\n' % NOW).encode()
def load(path):
    raw = open(path, 'rb').read()
    return json.loads(raw.decode('utf-8-sig')), raw

machines = {}
for conn in ('LAN', 'Connect'):
    d, raw = load(UD + 'machine/%s - %s.json' % (SYS_M, conn))
    assert dump(d) == raw, 'machine roundtrip mismatch ' + conn
    n = dict(d)
    name = 'Prusa CORE One INDX 8T Mixed Nozzles - ' + conn
    n['name'] = name; n['printer_settings_id'] = name
    n['nozzle_diameter'] = NOZ; n['min_layer_height'] = MINL; n['max_layer_height'] = MAXL
    machines[name] = n

fil_edits = {}
for f in sorted(glob.glob(UD + 'filament/*.json')):
    d, raw = load(f)
    cp = d.get('compatible_printers')
    if not cp or (SYS_M + ' - LAN') not in cp: continue
    assert dump(d) == raw, 'filament roundtrip mismatch ' + f
    add = [m for m in NEW_M if m not in cp]
    if add:
        d2 = dict(d); d2['compatible_printers'] = list(cp) + add
        fil_edits[f] = d2

MAP = collections.OrderedDict([
 ('layer_height', 'layer_height'), ('first_layer_height', 'initial_layer_print_height'),
 ('perimeters', 'wall_loops'), ('top_solid_layers', 'top_shell_layers'), ('bottom_solid_layers', 'bottom_shell_layers'),
 ('fill_density', 'sparse_infill_density'), ('fill_pattern', 'sparse_infill_pattern'),
 ('external_perimeter_extrusion_width', 'outer_wall_line_width'), ('perimeter_extrusion_width', 'inner_wall_line_width'),
 ('infill_extrusion_width', 'sparse_infill_line_width'), ('solid_infill_extrusion_width', 'internal_solid_infill_line_width'),
 ('top_infill_extrusion_width', 'top_surface_line_width'), ('first_layer_extrusion_width', 'initial_layer_line_width'),
 ('support_material_extrusion_width', 'support_line_width'),
 ('perimeter_speed', 'inner_wall_speed'), ('external_perimeter_speed', 'outer_wall_speed'), ('small_perimeter_speed', 'small_perimeter_speed'),
 ('infill_speed', 'sparse_infill_speed'), ('solid_infill_speed', 'internal_solid_infill_speed'), ('top_solid_infill_speed', 'top_surface_speed'),
 ('first_layer_speed', 'initial_layer_speed'), ('travel_speed', 'travel_speed'), ('bridge_speed', 'bridge_speed'),
 ('gap_fill_speed', 'gap_infill_speed'), ('support_material_speed', 'support_speed'),
 ('default_acceleration', 'default_acceleration'), ('perimeter_acceleration', 'inner_wall_acceleration'),
 ('external_perimeter_acceleration', 'outer_wall_acceleration'), ('infill_acceleration', 'sparse_infill_acceleration'),
 ('top_solid_infill_acceleration', 'top_surface_acceleration'), ('first_layer_acceleration', 'initial_layer_acceleration'),
 ('bridge_acceleration', 'bridge_acceleration'), ('travel_acceleration', 'travel_acceleration'),
 ('support_material_contact_distance', 'support_top_z_distance'), ('elefant_foot_compensation', 'elefant_foot_compensation'),
 ('brim_type', 'brim_type'), ('brim_width', 'brim_width'), ('support_material', 'enable_support'),
])

def map_profile(ps_file, tool):
    S, _ = parse_user(PS + ps_file)
    out = collections.OrderedDict()
    for k, ok in MAP.items():
        v = S.get(k)
        if v is None or v == '': continue
        if str(v).endswith('%') and k != 'fill_density': continue
        if k.endswith('_extrusion_width') and str(v) == '0': continue
        out[ok] = str(v)
    if str(S.get('spiral_vase', '0')) == '1':
        out['spiral_mode'] = '1'; out['detect_thin_wall'] = '0'
    if tool:
        for k in ('wall_filament', 'sparse_infill_filament', 'solid_infill_filament', 'support_filament', 'support_interface_filament'):
            out[k] = str(tool)
    return out

procs = collections.OrderedDict()
def add_proc(orca_name, ps_file, parent, tool, compat):
    d = dict(map_profile(ps_file, tool))
    d.update({'from': 'User', 'inherits': parent, 'is_custom_defined': '0', 'name': orca_name, 'print_settings_id': orca_name,
              'version': VERSION_P, 'compatible_printers': compat})
    procs[orca_name] = d

BASE = ' @Prusa CORE One INDX HF 0.4'
for n in ('0.07mm Extra Fine', '0.12mm Detail', '0.15mm Detail'):
    add_proc('%s%s - ColorMix' % (n, BASE), '%s @COREONEINDX HF0.4 - ColorMix.ini' % n, '0.15mm Detail' + BASE, None, OLD_M + NEW_M)
for n in ('0.05mm Ultra Fine', '0.07mm Extra Fine', '0.10mm Fine'):
    add_proc('%s @Prusa CORE One INDX 0.25 - T7' % n, '%s @COREONEINDX 0.25 - T7.ini' % n, '0.10mm Fine' + BASE, 7, NEW_M)
for lh in ('0.40', '0.50', '0.60'):
    add_proc('%smm Vase @Prusa CORE One INDX 1.0 HF - T8' % lh, '%smm Vase @COREONEINDX 1.0HF - T8.ini' % lh, '0.20mm Balanced' + BASE, 8, NEW_M)
for n in ('White', 'CF', 'TPU'):
    add_proc('0.20mm %s @Prusa CORE One INDX Std 0.4 - T6' % n, '0.20mm %s @COREONEINDX Std0.4 - T6.ini' % n, '0.20mm Balanced' + BASE, 6, NEW_M)

print('machines to create :', list(machines))
print('filaments to patch :', len(fil_edits))
for f in fil_edits: print('   ', os.path.basename(f))
print('process presets    :', len(procs))
for n, d in procs.items():
    print('  ', n, '| keys', len(d), '| layer', d.get('layer_height'), '| tool', d.get('wall_filament'), '| owl', d.get('outer_wall_line_width'), '| compat', len(d['compatible_printers']))
for n, d in procs.items():
    lh = float(d['layer_height']); t = d.get('wall_filament')
    noz = float(NOZ[int(t) - 1]) if t else 0.4
    assert lh <= (noz * 0.75 if noz < 1 else 0.75) + 1e-9, (n, lh, noz)
    assert all(k in d for k in ('layer_height', 'name', 'inherits', 'compatible_printers')), n
    assert not any(str(v) == '' for v in d.values()), n
print('sanity OK')
if not WRITE: sys.exit(0)

assert not os.path.exists(BK), 'backup dir exists'
for s in ('machine', 'filament', 'process'): os.makedirs(BK + s)
for f in fil_edits:
    shutil.copy2(f, BK + 'filament/'); shutil.copy2(f[:-5] + '.info', BK + 'filament/')
for n, d in machines.items():
    p = UD + 'machine/' + n; assert not os.path.exists(p + '.json'), p
    open(p + '.json', 'wb').write(dump(d)); open(p + '.info', 'wb').write(info())
for n, d in procs.items():
    p = UD + 'process/' + n; assert not os.path.exists(p + '.json'), p
    open(p + '.json', 'wb').write(dump(d)); open(p + '.info', 'wb').write(info())
for f, d2 in fil_edits.items():
    open(f, 'wb').write(dump(d2))
print('WRITTEN: machines', len(machines), '| process', len(procs), '| filaments patched', len(fil_edits), '| backup', BK)
