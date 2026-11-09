import os, re, uuid, base64, glob, collections, yaml, sys
HOME = os.path.expanduser('~')
exec(open(HOME + '/scripts/indx_build.py').read().split('# ---------- resolver self-test')[0])
AL = HOME + '/mnt/PrusaSlicer3-dev/presets/'
VEND = AL + 'local/prusa-research-fff/PrusaResearch/'
OUT = AL + 'user/prusa-research-fff/PrusaResearch/'

# ---- value-type vocabulary from the alpha's own vendor filaments ----
tcount = collections.defaultdict(collections.Counter)
def collect(node):
    for k, v in (node.get('values') or {}).items(): tcount[k][type(v)] += 1
    for c in node.get('variants') or []: collect(c)
for f in glob.glob(VEND + 'preset-filament-*.yaml'):
    for d in yaml.safe_load_all(open(f, encoding='utf-8')):
        if d: collect(d)

types = {}
def finalize_types():
    for k, c in tcount.items(): types[k] = c.most_common(1)[0][0]
finalize_types()

def find_leaf(doc, path_subs):
    """walk variants; each step must match a condition containing path_subs[i]"""
    node, i = doc, 0
    def rec(n, i):
        for c in n.get('variants') or []:
            cond = str(c.get('condition', ''))
            if i < len(path_subs) and path_subs[i] in cond:
                if i == len(path_subs) - 1: return c
                r = rec(c, i + 1)
                if r: return r
        return None
    return rec(doc, 0)

PARENT = {  # 2.x INDX parent -> (alpha vendor file)
 'Prusament PETG @COREONEINDX HF0.4': 'preset-filament-PETG-Prusament-PETG.yaml',
 'Prusament PLA @COREONEINDX HF0.4': 'preset-filament-PLA-Prusament-PLA.yaml',
 'Prusament ASA @COREONEINDX HF0.4': 'preset-filament-ASA-Prusament-ASA.yaml',
 'Prusament TPU 95A @COREONEINDX HF0.4': 'preset-filament-FLEX-Prusament-TPU-95A.yaml'}
WHITE = ['extrusion_multiplier','temperature','first_layer_temperature','bed_temperature','first_layer_bed_temperature','filament_max_volumetric_speed',
 'filament_cost','filament_density','filament_colour','filament_vendor','filament_spool_weight','filament_notes','filament_type','min_fan_speed','max_fan_speed',
 'bridge_fan_speed','disable_fan_first_layers','fan_below_layer_time','slowdown_below_layer_time','min_print_speed','fan_always_on','enable_dynamic_fan_speeds',
 'cooling','full_fan_speed_layer','filament_retract_length','filament_retract_speed','filament_deretract_speed','filament_retract_before_travel',
 'filament_retract_layer_change','filament_retract_before_wipe','filament_travel_ramping_lift']
RENAME3 = {'filament_retract_length': 'retract_length', 'filament_retract_speed': 'retract_speed', 'filament_deretract_speed': 'deretract_speed',
 'filament_retract_before_travel': 'retract_before_travel', 'filament_retract_layer_change': 'retract_layer_change',
 'filament_retract_before_wipe': 'retract_before_wipe', 'filament_travel_ramping_lift': 'travel_ramping_lift'}
PRESETS = [
 ('Prusament PETG @COREONEINDX HF0.4 - GeeeTech', 'Prusament PETG @COREONEINDX HF0.4'),
 ('Prusament PETG @COREONEINDX HF0.4 - ICE Rob', 'Prusament PETG @COREONEINDX HF0.4'),
 ('Prusament PLA @COREONEINDX HF0.4 - GEKO', 'Prusament PLA @COREONEINDX HF0.4'),
 ('Sunlu PLA @COREONEINDX HF0.4 - 220-210 - FLATTENED', 'Prusament PLA @COREONEINDX HF0.4'),
 ('Fiberlogy ASA @COREONEINDX HF0.4 - Matte Olive Green', 'Prusament ASA @COREONEINDX HF0.4'),
 ('Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.06 flow', 'Prusament TPU 95A @COREONEINDX HF0.4'),
 ('Ultrafuse TPU-95A @COREONEINDX HF0.4 - 1.08 flow', 'Prusament TPU 95A @COREONEINDX HF0.4'),
]
def coerce(key, v):
    v = v.strip().strip('"')
    t = types.get(key, str)
    try:
        if t is bool: return bool(int(float(v)))
        if t is int: return int(float(v)) if float(v) == int(float(v)) else float(v)
        if t is float: return float(v)
    except ValueError: pass
    return v.replace('\\n', '\n').replace('\\"', '"') if k == 'filament_notes' else v

os.makedirs(OUT, exist_ok=True)
made = []
for name, ipar in PRESETS:
    S, _ = parse_user(RP + 'filament/%s.ini' % name)
    Pi = resolve('filament', ipar)
    vf = PARENT[ipar]
    doc = next(d for d in yaml.safe_load_all(open(VEND + vf, encoding='utf-8')) if d and d.get('kind') == 'filament' and d.get('id') and 'variants' in d)
    leaf = find_leaf(doc, ['COREONE_INDX', 'nozzle_diameter == 0.4', 'nozzle_high_flow'])
    if not leaf: print('SKIP (no INDX HF0.4 leaf found):', name); continue
    vals = collections.OrderedDict()
    for k in WHITE:
        if k not in S or S[k].strip() in ('', 'nil', '""'): continue
        if k in Pi and eq(S[k], Pi[k]): continue
        k3 = RENAME3.get(k, k)
        if k3 not in types: continue
        vals[k3] = coerce(k3, S[k])
    top = collections.OrderedDict([('kind', 'filament'), ('id', str(uuid.uuid4())), ('variants', [collections.OrderedDict([
        ('condition', '((printer.base_model == "COREONE_INDX") and (tool.nozzle_diameter == 0.4) and tool.nozzle_high_flow)'),
        ('id', base64.b64encode(uuid.uuid4().bytes).decode().rstrip('=')),
        ('name', name),
        ('unconditional_inherits', [leaf['id']]),
        ('values', vals),
        ('features', collections.OrderedDict([('based_id', leaf['id']), ('based_root_id', doc['id'])]))])])])
    yaml.add_representer(collections.OrderedDict, lambda d, data: d.represent_mapping('tag:yaml.org,2002:map', data.items()))
    path = OUT + 'filament-%s.yaml' % name
    open(path, 'w', encoding='utf-8', newline='\n').write(yaml.dump(top, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000))
    chk = yaml.safe_load(open(path, encoding='utf-8'))
    made.append(name)
    print('+ %s\n    inherits leaf %s of "%s" | values: %s' % (name, leaf['id'], doc['id'], dict(vals)))
print('\ncreated', len(made), 'of', len(PRESETS), '| files in alpha user dir:', sorted(os.listdir(OUT)))
