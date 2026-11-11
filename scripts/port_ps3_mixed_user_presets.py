#!/usr/bin/env python3
"""Port the PrusaSlicer 2.x INDX filament presets to the mixed-nozzle PS3 vendor as user presets (the Wiper tool change is built into the vendor itself)."""
import io,os,re,sys,glob,json,uuid,base64,hashlib,yaml
PS2,STOCK,PS3USER,OUT=sys.argv[1:5]
NB='INDX_MIXED'; SUF='@INDXMIX'
def nid(s): return 'SXM_'+hashlib.sha1(s.encode()).hexdigest()[:20].upper()
def vid(): return base64.b64encode(os.urandom(16)).decode().rstrip('=')
def ini(p):
    d={}
    for l in io.open(p,encoding='utf-8').read().replace('\r','').split('\n'):
        if l.startswith('#') or '=' not in l: continue
        k,v=l.split('=',1); d[k.strip()]=v.strip()
    return d
names={}; types={}; known=set()
for f in glob.glob(STOCK+'/preset-filament-*.yaml'):
    t=io.open(f,encoding='utf-8').read(); known|=set(re.findall(r'(?m)^\s*([a-z_0-9]+):',t))
    for doc in yaml.safe_load_all(t):
        if not doc: continue
        top=doc.get('id')
        def w(v):
            for x in v.get('variants') or []:
                if 'name' in x: names[x['name']]=(x.get('id'),top)
                w(x)
        w(doc)
FALL={'PLA':'Prusament PLA @COREONEINDX HF0.4','PETG':'Prusament PETG @COREONEINDX HF0.4'}
def pick(u):
    p=u.get('inherits','')
    if p in names: return p
    ft=u.get('filament_type','PLA')
    c=[n for n in names if n.endswith('@COREONEINDX HF0.4') and not n.startswith('*') and ft in n.upper().split('@')[0].split()]
    for pref in ['Prusament','Generic']:
        for n in sorted(c):
            if n.startswith(pref): return n
    star={'ASA':'*ASA*','FLEX':'*FLEX*','PC':'*PC*','PA':'*PC*','PP':'*PC*','ABS':'*ABS*'}.get(ft)
    if star and star+' @COREONEINDX HF0.4' in names: return star+' @COREONEINDX HF0.4'
    return FALL.get(ft,FALL['PLA'])
SKIP={'filament_load_time','filament_unload_time','inherits','compatible_printers','compatible_printers_condition','compatible_prints','compatible_prints_condition','filament_settings_id','start_filament_gcode','name','id','condition','kind','variants','values','features'}
REN={'filament_retract_length':'retract_length','filament_retract_length_toolchange':'retract_length_toolchange'}
def val(v):
    if len(v)>1 and v[0]=='"' and v[-1]=='"': v=v[1:-1].replace('\\n','\n').replace('\\"','"').replace('\\\\','\\')
    return v if re.match(r'^-?\d+(\.\d+)?$',v) else json.dumps(v,ensure_ascii=False)
os.makedirs(OUT,exist_ok=True); rep=[]
for f in sorted(glob.glob(PS2+'/filament/*COREONEINDX*.ini')):
    base=os.path.basename(f)[:-4]; u=ini(f)
    if '1.0HF' in base: cond='(tool.nozzle_diameter == 1) and tool.nozzle_high_flow'
    elif 'Std0.4' in base: cond='(tool.nozzle_diameter == 0.4) and not tool.nozzle_high_flow'
    elif re.search(r'0\.25\b',base.split('@')[1]): cond='(tool.nozzle_diameter == 0.25)'
    else: cond='(tool.nozzle_diameter == 0.4) and tool.nozzle_high_flow'
    if 'GECO' in base: cond+=' and (sheet.type == "cold")'
    par=pick(u); pid,top=names[par]
    vals=[]
    for k in sorted(u):
        kk=REN.get(k,k); v=u[k]
        if k in SKIP or kk not in known or v=='nil' or v=='': continue
        vals.append('    %s: %s'%(kk,val(v)))
    m=re.search(r'M572 S([0-9.]+)',u.get('start_filament_gcode',''))
    if m and float(m.group(1))>0: vals.append('    pressure_advance_value: %s'%m.group(1))
    name=base.replace('@COREONEINDX',SUF)
    t='kind: filament\nid: %s\nvariants:\n- condition: ((printer.base_model == "%s") and %s)\n  id: %s\n  name: %s\n  unconditional_inherits:\n  - %s\n  values:\n%s\n  features:\n    based_id: %s\n    based_root_id: %s\n'%(uuid.uuid4(),NB,cond,vid(),json.dumps(name,ensure_ascii=False),nid(pid),'\n'.join(vals),nid(pid),nid(top))
    yaml.safe_load(t); io.open(os.path.join(OUT,'filament-%s.yaml'%name),'w',encoding='utf-8',newline='').write(t)
    rep.append((name,par.split(' @')[0],cond.split('== ')[1][:4],len(vals)))
for r in rep: print('%-62s <- %-34s %s %d'%r)
print(len(rep),'filaments')
