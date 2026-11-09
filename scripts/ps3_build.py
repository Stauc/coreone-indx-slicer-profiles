#!/usr/bin/env python3
"""PS3 alpha13: ColorMix detail user presets (print + tool_print). --write to apply."""
import sys, os, uuid, base64, secrets
WRITE = '--write' in sys.argv
D = os.path.expanduser('~/mnt/PrusaSlicer3-dev/presets/user/prusa-research-fff/PrusaResearch/')
PRINT_ROOT = '0VkSjedbRgyaEXK2ofKGmg'
TOOL_ROOT = 'tfGmkfdiQq++NX6mf8p4UQ'
# vendor leaf ids (from preset-print-coreone-indx.yaml / preset-tool-coreone-indx.yaml)
P_ID = {'0.10': 'Z0/g4p1mRzSbu/AYadbpqg', '0.15': 'sp9t4qR5QSyyIBb4MUPsuw'}
T_ID = {'0.10': '0.10mm Fine @COREONEINDX 0.4HF', '0.15': 'Hhus/D8wTPKSY9vp0xEuUQ'}
COND_P = '((printer.base_model == "COREONE_INDX") and (tool.nozzle_diameter == 0.4) and tool.nozzle_high_flow)'
def cond_t(lh): return '((printer.base_model == "COREONE_INDX") and (tool.nozzle_diameter == 0.4) and tool.nozzle_high_flow and (print.layer_height == %s))' % lh
def rid(): return base64.b64encode(secrets.token_bytes(16)).decode().rstrip('=')

# (layer height, display, parent key, top, bottom, density)
SETS = [('0.07', '0.07mm Extra Fine', '0.10', 9, 7, '8%'),
        ('0.12', '0.12mm Detail',     '0.15', 6, 5, '10%'),
        ('0.15', '0.15mm Detail',     '0.15', 6, 5, '10%')]
files = {}
for lh, disp, par, top, bot, dens in SETS:
    tname = '%s ColorMix @COREONEINDX 0.4HF' % disp
    pname = '%s ColorMix' % disp
    files['print-%s.yaml' % pname] = f'''kind: print
id: {uuid.uuid4()}
variants:
- condition: {COND_P}
  id: {rid()}
  name: {pname}
  unconditional_inherits:
  - {P_ID[par]}
  values:
    layer_height: {lh}
    brim_type: outer_and_inner
    brim_width: 5
    default_tool_print: {tname}
  features:
    based_id: {P_ID[par]}
    based_root_id: {PRINT_ROOT}
'''
    files['tool_print-%s.yaml' % tname] = f'''kind: tool_print
id: {uuid.uuid4()}
variants:
- condition: {cond_t(lh)}
  id: {rid()}
  name: {tname}
  unconditional_inherits:
  - {T_ID[par]}
  values:
    fill_pattern: gyroid
    fill_density: {dens}
    top_solid_layers: {top}
    bottom_solid_layers: {bot}
  features:
    based_id: {T_ID[par]}
    based_root_id: {TOOL_ROOT}
'''
try:
    import yaml
except ImportError:
    yaml = None
for n, t in files.items():
    if yaml:
        d = yaml.safe_load(t)
        v = d['variants'][0]
        assert d['kind'] in ('print', 'tool_print') and v['name'] and v['values'] and v['unconditional_inherits'] == [v['features']['based_id']], n
    assert not os.path.exists(D + n), D + n
    print(('WRITE ' if WRITE else 'would write ') + n)
    if WRITE: open(D + n, 'w', newline='\n').write(t)
print('yaml-validated' if yaml else 'PyYAML missing: not validated')
