import os, re, sys, time, json, yaml
HOME = os.path.expanduser('~'); M = HOME + '/mnt/'
RP = M + 'Roaming--PrusaSlicer/'; OF = M + 'Roaming--OrcaSlicer/user/default/filament/'
AL = M + 'PrusaSlicer3-dev/presets/user/prusa-research-fff/PrusaResearch/'
ini = RP + 'PrusaSlicer.ini'
if time.time() - os.path.getmtime(ini) < 120: sys.exit('ABORT: PrusaSlicer.ini changed in the last 2 min - is PrusaSlicer open?')
log = []
def sub_bytes(path, pairs, only_prefix=None):
    b = open(path, 'rb').read(); out = []
    for line in b.split(b'\n'):
        if only_prefix is None or line.startswith(only_prefix):
            for o, n in pairs: line = line.replace(o, n)
        out.append(line)
    nb = b'\n'.join(out)
    if nb != b: open(path, 'wb').write(nb); return True
    return False

# 1) revert my wrong printer rename (GEKO was only a typo in OTHER places; the plate is GECO)
src = RP + 'printer/Prusa CORE One INDX 8T HF0.4 nozzle + Wiper + GEKO.ini'
dst = RP + 'printer/Prusa CORE One INDX 8T HF0.4 nozzle + Wiper + GECO.ini'
assert os.path.exists(src) and not os.path.exists(dst)
os.rename(src, dst); log.append('printer renamed back to ... + GECO')
sub_bytes(ini, [(b'Wiper + GEKO', b'Wiper + GECO')], only_prefix=b'printer = '); log.append('PrusaSlicer.ini selected printer -> GECO')

# 2) GEKO -> GECO in filament names
for n in ['Prusament PLA @COREONE - GEKO', 'Prusament PLA @COREONE HF0.4 - GEKO', 'Prusament PLA @COREONE HF0.8 - GEKO', 'Prusament PLA @COREONEINDX HF0.4 - GEKO']:
    new = n.replace('GEKO', 'GECO'); assert os.path.exists(RP + 'filament/%s.ini' % n) and not os.path.exists(RP + 'filament/%s.ini' % new)
    os.rename(RP + 'filament/%s.ini' % n, RP + 'filament/%s.ini' % new); log.append('filament: %s -> %s' % (n, new))

# 3) spelling inside compatible_printers lists (these name the CORE One '+ Wiper + GECO' printers)
for sub, f in [('filament', 'Prusament PLA @COREONE HF0.4 - GECO.ini'), ('filament', 'Sunlu PETG @COREONE HF0.8 - Matte HS.ini'), ('print', '0.40mm STRUCTURAL @COREONE HF0.8 - Aligned.ini')]:
    if sub == 'filament' or sub == 'print':
        changed = sub_bytes('%s%s/%s' % (RP, sub, f), [(b'Wiper + GEKO', b'Wiper + GECO')], only_prefix=b'compatible_printers = ')
        log.append('compat list spelling fixed in %s/%s: %s' % (sub, f, changed))

# 4) the new INDX GECO filament must only show for the GECO printer (bed heater off = 0 C is only right on the cold plate)
p = RP + 'filament/Prusament PLA @COREONEINDX HF0.4 - GECO.ini'
b = open(p, 'rb').read()
nb = re.sub(rb'^compatible_printers = .*$', b'compatible_printers = "Prusa CORE One INDX 8T HF0.4 nozzle + Wiper + GECO"', b, flags=re.M)
open(p, 'wb').write(nb); log.append('INDX GECO filament restricted to the GECO printer')

# 5) Orca
for ext in ('json', 'info'):
    os.rename(OF + 'Prusament PLA @Prusa CORE One INDX - GEKO.' + ext, OF + 'Prusament PLA @Prusa CORE One INDX - GECO.' + ext)
raw = open(OF + 'Prusament PLA @Prusa CORE One INDX - GECO.json', 'rb').read().replace(b'GEKO', b'GECO')
open(OF + 'Prusament PLA @Prusa CORE One INDX - GECO.json', 'wb').write(raw); json.loads(raw.decode('utf-8')); log.append('Orca preset renamed to GECO')

# 6) 3.0 alpha
os.rename(AL + 'filament-Prusament PLA @COREONEINDX HF0.4 - GEKO.yaml', AL + 'filament-Prusament PLA @COREONEINDX HF0.4 - GECO.yaml')
t = open(AL + 'filament-Prusament PLA @COREONEINDX HF0.4 - GECO.yaml', encoding='utf-8').read().replace('GEKO', 'GECO')
open(AL + 'filament-Prusament PLA @COREONEINDX HF0.4 - GECO.yaml', 'w', encoding='utf-8', newline='\n').write(t); yaml.safe_load(t); log.append('3.0 alpha preset renamed to GECO')
print('\n'.join(log))
