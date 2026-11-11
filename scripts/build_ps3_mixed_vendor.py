#!/usr/bin/env python3
"""Build a separate PrusaSlicer 3 vendor bundle (offline zip) with mixed nozzles for the CORE One INDX,
generated from the installed Prusa profiles. Idea: ltlowe's "Multi-Size Core One INDX" bundle (Prusa forum)."""
import io,os,re,sys,json,hashlib,shutil,zipfile,yaml
SRC,OUT,ZIP=sys.argv[1],sys.argv[2],sys.argv[3]
WIPER=sys.argv[4] if len(sys.argv)>4 else None
NB='INDX_MIXED'; VID='StaucINDXMixed'; REPO='stauc-indx-mixed'; VER='1.0.8'; SUF='@INDXMIX'
def rd(f): return io.open(os.path.join(SRC,f),encoding='utf-8',newline='').read().replace('\r\n','\n')
def nid(s): return 'SXM_'+hashlib.sha1(s.encode()).hexdigest()[:20].upper()
def unq(s):
    s=s.strip()
    return s[1:-1] if len(s)>1 and s[0]==s[-1] and s[0] in '\'"' else s
files=['preset-print-common.yaml','preset-print-coreone-indx.yaml','preset-tool-coreone-indx.yaml','preset-printer-coreone-indx.yaml']
files+=sorted(f for f in os.listdir(SRC) if f.startswith('preset-filament-') and f.endswith('.yaml'))
txt={f:rd(f) for f in files}
# --- tool_print: enable 0.25, add standard 0.4 (values copied from 0.4HF)
def mixed_tool(t):
    ls=t.split('\n'); s=next(i for i,l in enumerate(ls) if l.strip()=='# # 0.25 nozzle'); out=ls[:s]
    for l in ls[s:]:
        if l.strip()=='# only_one_perimeter_first_layer': continue
        out.append(re.sub(r'^(\s*)# ?',r'\1',l,count=1))
    a=next(i for i,l in enumerate(ls) if l.startswith('      - condition: print.layer_height == 0.10'))
    b=next(i for i,l in enumerate(ls) if l.strip().startswith('# # 0.5 high-flow nozzle') or l.strip().startswith('# - condition: tool.nozzle_diameter == 0.5'))
    new=['# 0.4 standard nozzle, values copied from 0.4HF','  - condition: tool.nozzle_diameter == 0.4 and not tool.nozzle_high_flow','    id: std04-root','    values:','      max_print_speed: 300','    variants:']
    for l in [l for l in ls[a:b] if l.strip() and not l.strip().startswith('#')]:
        l=l[2:]
        m=re.match(r'^(\s*)name: (.*) @COREONEINDX 0.4HF$',l)
        if m: l='%sname: %s @COREONEINDX 0.4'%(m.group(1),m.group(2))
        m=re.match(r'^(\s*)id: (.*)$',l)
        if m: l='%sid: std04-%s'%(m.group(1),unq(m.group(2)))
        new.append(l)
    while out and out[-1]=='': out.pop()
    return '\n'.join(out+new)+'\n'
txt['preset-tool-coreone-indx.yaml']=mixed_tool(txt['preset-tool-coreone-indx.yaml'])

# --- v1.0.1: 1.0 HF nozzle + every layer height on every nozzle ("Match" entries), because PS3 only offers
#     layer heights that exist for all tools of the printer
H=['0.05','0.07','0.10','0.12','0.15','0.20','0.25','0.40','0.50','0.60']
def ind(l): return len(l)-len(l.lstrip(' '))
def code(l): return l.strip() and not l.strip().startswith('#')
def block_end(ls,i):
    k=ind(ls[i]); j=i+1
    while j<len(ls) and not (code(ls[j]) and ind(ls[j])<=k): j+=1
    return j
def find(ls,pat,start=0):
    return next(i for i in range(start,len(ls)) if re.match(pat,ls[i]))
def print_file(t):
    ls=t.split('\n')
    def fill(i,tag):
        k=ind(ls[i]); e=block_end(ls,i); have=set()
        for l in ls[i:e]:
            m=re.match(r'^\s*- name: (\S+)mm\s*$',l)
            if m: have.add('%.2f'%float(m.group(1)))
        new=[]
        for h in H:
            if h not in have: new+=[' '*(k+2)+'- name: %smm'%h,' '*(k+4)+'id: lh-%s-%s'%(tag,h),' '*(k+4)+'values:',' '*(k+6)+'layer_height: %s'%h]
        ls[e:e]=new
    nh=find(ls,r'^  - condition: not tool\.nozzle_high_flow')
    fill(find(ls,r'^    - condition: tool\.nozzle_diameter == 0\.4\s*$',nh),'std04')
    fill(find(ls,r'^    - condition: tool\.nozzle_diameter == 0\.25\s*$',nh),'n025')
    nh=find(ls,r'^  - condition: not tool\.nozzle_high_flow')
    ls[nh:nh]=['    - condition: tool.nozzle_diameter == 1','      id: lh-hf10-root','      variants:']
    fill(nh,'hf10')
    fill(find(ls,r'^    - condition: tool\.nozzle_diameter == 0\.4\s*$'),'hf04')
    # default tool print for the 1.0 nozzle
    d=find(ls,r'^- condition: tool\.nozzle_diameter == 0\.8')
    e=block_end(ls,d); ls[e:e]=['- condition: tool.nozzle_diameter == 1','  id: dtp-hf10','  values:','    default_tool_print: 0.50mm Vase']
    r=find(ls,r'^- condition: printer\.base_model == "COREONE_INDX"',find(ls,r'^match_mode: all_matches')); v=find(ls,r'^  values:',r); ls[v+1:v+1]=['    skirts: 2']
    return '\n'.join(ls)
V10=[('extrusion_width','1.1'),('first_layer_extrusion_width','1.2'),('perimeter_extrusion_width','1.1'),('external_perimeter_extrusion_width','1.1'),('infill_extrusion_width','1.1'),('solid_infill_extrusion_width','1.1'),('top_infill_extrusion_width','1'),('support_material_extrusion_width','1'),
 ('perimeters','1'),('top_solid_layers','0'),('top_solid_min_thickness','0'),('bottom_solid_min_thickness','1'),('fill_density','0%'),('elefant_foot_compensation','0.3'),('gap_fill_enabled','0'),('gap_fill_speed','40'),
 ('first_layer_speed','35'),('perimeter_speed','100'),('external_perimeter_speed','100'),('small_perimeter_speed','100'),('infill_speed','100'),('solid_infill_speed','100'),('top_solid_infill_speed','100'),
 ('external_perimeter_acceleration','3000'),('perimeter_acceleration','3000'),('infill_acceleration','3000'),('max_print_speed','300')]
def tool_file(t):
    ls=t.split('\n'); known=set(re.findall(r'(?m)^\s*#?\s*([a-z_0-9]+):',t))
    def items_of(i):
        k=ind(ls[i]); e=block_end(ls,i); items={}; cur=None; pat=re.compile(r'^\s{%d}- condition: print\.layer_height == (\S+)'%(k+2))
        for l in ls[i+1:e]:
            m=pat.match(l)
            if m:
                cur='%.2f'%float(m.group(1)); cur=cur if cur not in items else None
                if cur: items[cur]={}
                continue
            if cur and code(l) and ind(l)>=k+6 and not l.strip().startswith(('name:','id:','values:')):
                a,b=l.strip().split(':',1); items[cur][a]=b.strip()
        return items
    def custom(i,tag,suffix,name,h,base,ov):
        # named alternatives at one layer height must be unconditioned children of the layer-height node (as in Prusa's XL presets)
        k=ind(ls[i]); e=block_end(ls,i); v=dict(items_of(i)[base])
        for a,b in ov.items():
            assert a in known,a
            v[a]=b
        new=[' '*(k+4)+'- name: %s @COREONEINDX %s'%(name,suffix),' '*(k+6)+'id: tc-%s-%s'%(tag,name),' '*(k+6)+'values:']+[' '*(k+8)+'%s: %s'%x for x in v.items()]
        pat=re.compile(r'^\s{%d}- condition: print\.layer_height == (\S+)'%(k+2)); j=None
        for q in range(i+1,e):
            m=pat.match(ls[q])
            if m and '%.2f'%float(m.group(1))==h: j=q; break
        if j is None:
            ls[e:e]=[' '*(k+2)+'- condition: print.layer_height == %s'%h,' '*(k+4)+'id: tg-%s-%s'%(tag,h),' '*(k+4)+'variants:']+new; return
        je=block_end(ls,j)
        if not any(l.strip()=='variants:' and ind(l)==k+4 for l in ls[j+1:je]):
            body=[l for l in ls[j+1:je]]; first=next(q for q,l in enumerate(body) if code(l))
            assert body[first].strip().startswith('name:'),body[first]
            body=[('  '+l if l.strip() else l) for l in body]; body[first]=' '*(k+4)+'- '+body[first].strip()
            ls[j+1:je]=[' '*(k+4)+'id: tg-%s-%s'%(tag,h),' '*(k+4)+'variants:']+body; je=block_end(ls,j)
        ls[je:je]=new
    def matches(i,tag,suffix,skip=()):
        k=ind(ls[i]); e=block_end(ls,i); items={}; cur=None; pat=re.compile(r'^\s{%d}- condition: print\.layer_height == (\S+)'%(k+2))
        for l in ls[i+1:e]:
            m=pat.match(l)
            if m: cur='%.2f'%float(m.group(1)); items[cur]=[]; continue
            if cur and code(l) and ind(l)>=k+6 and not l.strip().startswith(('name:','id:','values:')): items[cur].append(l.strip())
        new=[]
        for h in H:
            if h in items or h in skip: continue
            near=min(items,key=lambda x:abs(float(x)-float(h)))
            new+=[' '*(k+2)+'- condition: print.layer_height == %s'%h,' '*(k+4)+'name: %smm Match @COREONEINDX %s'%(h,suffix),' '*(k+4)+'id: tm-%s-%s'%(tag,h),' '*(k+4)+'values:']+[' '*(k+6)+x for x in items[near]]
        ls[e:e]=new
    i4=find(ls,r'^  - condition: tool\.nozzle_diameter == 0\.4 and not tool\.nozzle_high_flow')
    matches(i4,'std04','0.4')
    custom(i4,'std04','0.4','0.20mm White','0.20','0.20',{'max_volumetric_speed':'12'})
    custom(i4,'std04','0.4','0.20mm CF','0.20','0.20',{'bottom_solid_layers':'4','bridge_speed':'35','default_acceleration':'2500','external_perimeter_acceleration':'2500','external_perimeter_speed':'120','fill_density':'20%','fill_pattern':'gyroid','first_layer_speed':'30','gap_fill_speed':'60','infill_acceleration':'4000','infill_speed':'150','max_volumetric_speed':'8','perimeter_acceleration':'3000','perimeter_speed':'150','perimeters':'3','small_perimeter_speed':'100','solid_infill_acceleration':'3000','solid_infill_speed':'120','support_material_speed':'60','top_solid_infill_speed':'80','top_solid_layers':'6'})
    custom(i4,'std04','0.4','0.20mm TPU','0.20','0.20',{'bottom_solid_layers':'4','bridge_acceleration':'800','bridge_speed':'25','default_acceleration':'1000','external_perimeter_acceleration':'800','external_perimeter_speed':'30','fill_pattern':'gyroid','first_layer_speed':'20','gap_fill_speed':'25','infill_acceleration':'1000','infill_speed':'45','max_volumetric_speed':'3.5','perimeter_acceleration':'800','perimeter_speed':'40','perimeters':'3','small_perimeter_speed':'30','solid_infill_acceleration':'800','solid_infill_speed':'40','support_material_speed':'30','top_solid_infill_acceleration':'800','top_solid_infill_speed':'30','travel_speed':'200'})
    matches(find(ls,r'^  - condition: tool\.nozzle_diameter == 0\.25\s*$',find(ls,r'^  - condition: tool\.nozzle_high_flow')),'n025','0.25',skip=('0.05',))
    i25=find(ls,r'^  - condition: tool\.nozzle_diameter == 0\.25\s*$',find(ls,r'^  - condition: tool\.nozzle_high_flow'))
    custom(i25,'n025','0.25','0.05mm Ultra Fine','0.05','0.07',{'bottom_solid_layers':'10','top_solid_layers':'14','support_material_contact_distance':'0.1','max_volumetric_speed':'4'})
    hf=find(ls,r'^  - condition: tool\.nozzle_high_flow'); i=find(ls,r'^    - condition: tool\.nozzle_diameter == 0\.4\s*$',hf); e=block_end(ls,i)
    blk=['# 1.0 high-flow nozzle (T8): single-wall "vase" profiles from the PrusaSlicer 2.x presets','    - condition: tool.nozzle_diameter == 1','      id: t-hf10-root','      values:']
    for a,b in V10:
        assert a in known,a
        blk.append('        %s: %s'%(a,b))
    blk.append('      variants:')
    for h in ['0.40','0.50','0.60']:
        blk+=['      - condition: print.layer_height == %s'%h,'        name: %smm Vase @COREONEINDX 1.0HF'%h,'        id: t-hf10-%s'%h,'        values:','          perimeters: 1']
    ls[e:e]=blk
    matches(e+1,'hf10','1.0HF')
    matches(i,'hf04','0.4HF')
    S={'perimeter_speed':'300','external_perimeter_speed':'240','small_perimeter_speed':'204','infill_speed':'360','solid_infill_speed':'300','top_solid_infill_speed':'120','gap_fill_speed':'144','bridge_speed':'60','support_material_speed':'144','first_layer_speed':'54','first_layer_solid_infill_speed':'120','first_layer_speed_over_raft':'36','max_print_speed':'360','fill_pattern':'gyroid'}
    custom(i,'hf04','0.4HF','0.20mm Speed 120%','0.20','0.20',S)
    custom(i,'hf04','0.4HF','0.25mm Speed 120%','0.25','0.25',dict(S,perimeter_speed='264',solid_infill_speed='288'))
    custom(i,'hf04','0.4HF','0.07mm Extra Fine ColorMix','0.07','0.10',{'fill_pattern':'gyroid','fill_density':'8%','top_solid_layers':'9','bottom_solid_layers':'7'})
    custom(i,'hf04','0.4HF','0.12mm Detail ColorMix','0.12','0.15',{'fill_pattern':'gyroid','fill_density':'10%','top_solid_layers':'6','bottom_solid_layers':'5'})
    custom(i,'hf04','0.4HF','0.15mm Detail ColorMix','0.15','0.15',{'fill_pattern':'gyroid','fill_density':'10%','top_solid_layers':'6','bottom_solid_layers':'5'})
    # per-nozzle limits for 1.0
    d=find(ls,r'^  - condition: tool\.nozzle_diameter == 0\.8'); e=block_end(ls,d)
    ls[e:e]=['  - condition: tool.nozzle_diameter == 1','    id: tc-hf10','    values:','      deretract_speed: 15','      max_layer_height: 0.7','      min_layer_height: 0.2','      retract_before_wipe: 50%','      retract_length: 0.6','      retract_lift: 0.25','      retract_speed: 25','      wipe: 1']
    return '\n'.join(ls)
def printer_file(t):
    ls=t.split('\n'); d=find(ls,r'^- condition: tool\.nozzle_diameter == 0\.8'); e=block_end(ls,d)
    ls[e:e]=['- condition: tool.nozzle_diameter == 1','  id: dp-hf10','  values:','    default_print: 0.50mm']
    # start G-code moves into a helper that switches on the sheet: normal, or bed heater off for a cold plate (GECO)
    a=find(ls,r'^    start_gcode: \|'); b=a+1
    while b<len(ls) and not (code(ls[b]) and ind(ls[b])<=4): b+=1
    body=ls[a+1:b]; del ls[a:b]
    # TPU/FLEX on the first tool: hotter clean + 8 s soak before the first push (same change as the tool-change G-code; source: Kiddocteur, Prusa forum)
    i1=next(q for q,l in enumerate(body) if l.strip()=='{tc_deretract_speed = 60*10}'); assert 'filament_type[initial_tool]=="FLEX"' in body[i1-1]
    body.insert(i1+1,body[i1].replace('{tc_deretract_speed = 60*10}','{eject_temp = target_temp - 25}'))
    i2=next(q for q,l in enumerate(body) if l.strip()=='M104 S{target_temp}'); pad=body[i2][:len(body[i2])-len(body[i2].lstrip())]
    body[i2+1:i2+1]=[pad+'{if filament_type[initial_tool]=="FLEX"}',pad+'  G4 S8 ; FLEX soak - let the TPU melt before pushing',pad+'{endif}']
    cold=[]; bed=0
    for l in body:
        x=l.strip()
        if x.startswith('M140 S{first_layer_bed_temperature[initial_tool]}'):
            bed+=1
            if bed==1: cold.append(l.replace(x,'M140 S0 ; cold plate - bed heater off'))
            continue
        if x.startswith('M190 R{first_layer_bed_temperature[initial_tool]}'): cold.append(l.replace(x,'; cold plate: no bed wait')); continue
        if x.startswith(('M140 S115','M191 S{chamber_minimal_temperature[initial_tool]}','G29 G ; absorb heat')): continue
        if x=='{if first_layer_bed_temperature[initial_tool] <= 60}M106 S70{endif}': cold.append(l.replace(x,'M106 S70')); continue
        cold.append(l)
    assert bed==2 and len(body)-len(cold)==4,(bed,len(body)-len(cold))
    i=find(ls,r"^- '\*default_print_C1_indx\*'",find(ls,r'^kind: printer',1)); ls[i+1:i+1]=["- '*start_by_sheet*'"]
    # Wiper tool-change G-code (with the TPU/FLEX hotter clean + soak) from the user's PS3 printer preset
    if WIPER:
        w=yaml.safe_load(io.open(WIPER,encoding='utf-8'))['variants'][0]['values']['toolchange_gcode']
        a=find(ls,r'^    toolchange_gcode: '); b=a+1
        while b<len(ls) and not (code(ls[b]) and ind(ls[b])<=4): b+=1
        ls[a:b]=['    toolchange_gcode: '+json.dumps(w,ensure_ascii=False)]
    helper=['kind: printer',"id: '*start_by_sheet*'",'variants:','- condition: sheet.type != "cold"','  id: sbs-std','  values:','    start_gcode: |-']+body+['- condition: sheet.type == "cold"','  id: sbs-cold','  values:','    autoemit_temperature_commands: 0','    start_gcode: |-']+cold+['---']
    return '\n'.join(helper+ls)
txt['preset-tool-coreone-indx.yaml']=tool_file(txt['preset-tool-coreone-indx.yaml'])
txt['preset-print-coreone-indx.yaml']=print_file(txt['preset-print-coreone-indx.yaml'])
txt['preset-printer-coreone-indx.yaml']=printer_file(txt['preset-printer-coreone-indx.yaml'])
# --- collect ids
IDRE=re.compile(r'^(\s*(?:- )?id: )(.*)$')
ids=set()
for t in txt.values():
    for l in t.split('\n'):
        m=IDRE.match(l)
        if m: ids.add(unq(m.group(2)))
# --- filament top-level names
fname={}
for f,t in txt.items():
    for d in re.split(r'(?m)^---\s*$',t):
        if re.search(r'(?m)^kind: filament\s*$',d):
            m=re.search(r'(?m)^name: (.*)$',d)
            if m: fname[unq(m.group(1))]=unq(m.group(1))+' '+SUF
unresolved=set(); out={}
for f,t in txt.items():
    res=[]; inh=False; kind=None
    for l in t.split('\n'):
        if l.startswith('kind:'): kind=l.split(':',1)[1].strip()
        if l.strip()=='---': kind=None
        if 'base_model' in l: l=l.replace('COREONE_INDX',NB)
        m=IDRE.match(l)
        if m: l=m.group(1)+nid(unq(m.group(2)))
        if re.match(r'^\s*(unconditional_)?inherits:\s*$',l): inh=True; res.append(l); continue
        if inh:
            m=re.match(r'^(\s*- )(.*)$',l)
            if m:
                k=unq(m.group(2))
                if k in ids: l=m.group(1)+nid(k)
                else: unresolved.add((f,k))
            else: inh=False
        m=re.match(r'^(\s*(?:- )?name: )(.*)$',l)
        if m:
            n=unq(m.group(2)).replace('@COREONEINDX',SUF)
            if m.group(1)=='name: ' and n in fname: n=fname[n]
            if n=='Prusa CORE One INDX': n='CORE One INDX Mixed'
            l=m.group(1)+"'"+n.replace("'","''")+"'"
        m=re.match(r'^(\s*default_material: )(.*)$',l)
        if m and unq(m.group(2)) in fname: l=m.group(1)+"'"+fname[unq(m.group(2))]+"'"
        res.append(l)
    out[f]='\n'.join(res)
# --- vendor.yaml
v=rd('vendor.yaml'); docs=re.split(r'(?m)^---\s*$',v)
head=docs[0][:docs[0].index('printer_families:')]
head=head.replace('id: PrusaResearch','id: '+VID).replace('name: Prusa Research FFF','name: CORE One INDX Mixed Nozzles').replace(re.search(r'version: .*',head).group(0),'version: '+VER)
head+='printer_families:\n- label: CORE One INDX Mixed\n  base_model: %s\n  printer_configs_order:\n  - indxmix-8t\n'%NB
pd=next(d for d in docs if re.search(r'(?m)^kind: printer\s*$',d) and re.search(r'(?m)^id: COREONE_INDX\s*$',d))
pd=pd.replace('name: Prusa CORE One INDX','name: CORE One INDX Mixed').replace('id: COREONE_INDX','id: '+NB).replace('base_model: COREONE_INDX','base_model: '+NB)
for k in ['supports_non_high_flow_nozzle','supports_025_nozzle']:
    a='  %s:\n    default: false'%k; assert pd.count(a)==1,k; pd=pd.replace(a,'  %s:\n    default: true'%k)
def tool(i,n,d,hf): return '\nkind: tool\ntechnology: FFF\nid: %s\nname: %s\ncondition: printer.base_model == "%s"\nfeatures:\n%s  nozzle_diameter:\n    default: %s\n'%(i,n,NB,'  nozzle_high_flow:\n    default: true\n' if hf else '',d)
parts=[head,pd.rstrip('\n')+'\n',tool('indxmix-04hf','0.4 HF','0.4',1),tool('indxmix-04',"'0.4'",'0.4',0),tool('indxmix-025',"'0.25'",'0.25',0),tool('indxmix-10hf','1.0 HF','1.0',1),
 '\nkind: sheet\nname: Satin\nid: indxmix-satin\ntype: satin\n','\nkind: sheet\nname: PEI Smooth\nid: indxmix-pei-smooth\ntype: pei_smooth\n','\nkind: sheet\nname: PEI Textured\nid: indxmix-pei-textured\ntype: pei_textured\n',
 '\nkind: sheet\nname: PA Nylon\nid: indxmix-pa-nylon\ntype: pa_nylon\n','\nkind: sheet\nname: PP\nid: indxmix-pp\ntype: pp\n','\nkind: sheet\nname: GECO (cold)\nid: indxmix-geco\ntype: cold\nfeatures:\n  cold:\n    default: true\n',

 '\nkind: printer_config\nid: indxmix-8t\nname: CORE One INDX Mixed 8T\nprinter: %s\nlegacy_printer_model: [COREONE_INDX8T]\ntool_count: 8\ntools:\n - tool: indxmix-04hf\nsheet: indxmix-satin\n'%NB]
out['vendor.yaml']='---'.join(parts)
# --- validate + write
root=os.path.join(OUT,VID,VER); shutil.rmtree(OUT,ignore_errors=True); os.makedirs(os.path.join(root,'assets'))
for f,t in out.items():
    try: list(yaml.safe_load_all(t))
    except Exception as e: raise SystemExit('YAML error in %s: %s'%(f,str(e)[:300]))
    io.open(os.path.join(root,f),'w',encoding='utf-8',newline='').write(t.replace('\n','\r\n'))
for a in ['coreoneindx.svg','coreoneindx_bed.stl','COREONEINDX_thumbnail.svg']: shutil.copy(os.path.join(SRC,'assets',a),os.path.join(root,'assets',a))
man=[]
for dp,_,fs in os.walk(root):
    for x in sorted(fs):
        p=os.path.join(dp,x); man.append({'filename':os.path.relpath(p,root).replace(os.sep,'/'),'filehash':hashlib.sha256(open(p,'rb').read()).hexdigest()})
json.dump(sorted(man,key=lambda x:x['filename']),open(os.path.join(root,'manifest.json'),'w'),indent=2)
open(os.path.join(OUT,'manifest.json'),'w').write(json.dumps({'name':'CORE One INDX Mixed Nozzles','description':'CORE One INDX 8T with mixed nozzles (0.4 HF, 0.4, 0.25, 1.0 HF); generated from Prusa FFF profiles.','visibility':'','id':REPO,'version':2,'url':'','index_url':'','offline_archive_url':''},separators=(',',':'))+'\n')
import time
def zi(n):
    z=zipfile.ZipInfo(n,time.localtime()[:6]); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=0; z.external_attr=0; return z
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z: z.writestr(zi(VID+'.idx'),('min_slic3r_version = 3.0.0-alpha14\n%s CORE One INDX mixed nozzles, generated from Prusa FFF profiles\n'%VER).encode())
open(os.path.join(OUT,'vendor_indices.zip'),'wb').write(buf.getvalue())
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
    fs=[]
    for dp,_,ff in os.walk(OUT):
        for x in ff:
            p=os.path.join(dp,x); fs.append((os.path.relpath(p,OUT).replace(os.sep,'/'),open(p,'rb').read()))
    for n,bb in sorted(fs): z.writestr(zi(n),bb)
print('files',len(out),'ids',len(ids),'filament names',len(fname),'unresolved inherits',sorted(unresolved)[:10],len(unresolved))
