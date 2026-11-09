import os, re, collections
HOME = os.path.expanduser('~')
RP = HOME + '/mnt/Roaming--PrusaSlicer/'
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
    secs = collections.OrderedDict(); cur = None
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
