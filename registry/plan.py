#!/usr/bin/env python3
"""Ubah recipe menjadi rencana build siap-eksekusi (key, id, nilai property valid) TANPA membaca seluruh registry.
Pakai: python3 registry/plan.py list-page --program SWT --module bookings   (modul: lihat recipes.json → modules)
       python3 registry/plan.py --list
Setiap ref divalidasi: nama ada, nilai axis valid. Hasil: JSON ke stdout."""
import json,sys,os,re
D=os.path.dirname(os.path.abspath(__file__)); L=lambda n:json.load(open(os.path.join(D,n)))
R=L('recipes.json'); reg={'SHIELD':{e['name']:e for e in L('shield.json')},'GUN':{e['name']:e for e in L('gun.json')}}
a=sys.argv[1:]
if not a or a[0] in('-h','--help'): print(__doc__); sys.exit(0)
if a[0]=='--list':
    for k,v in R['recipes'].items(): print(f"{k:16} {v['title']}")
    print('program:',', '.join(R['programs'])); sys.exit(0)
name=a[0]; prog=a[a.index('--program')+1] if '--program' in a else 'SWT'
P=dict(R['programs'][prog]); rec=R['recipes'][name]; problems=[]
if '--module' in a:
    mod=R['modules'][a[a.index('--module')+1]]; P.update({'rail':mod['rail'],'sidebar':mod['sidebar'],'menu':mod['menu']})
for k in ('rail','sidebar','menu'):
    if '--'+k in a: P[k]=a[a.index('--'+k)+1]
P.setdefault('menu','Default')
def fmt(s): 
    return re.sub(r'\{(\w+)\}',lambda m:P.get(m.group(1),m.group(0)),s) if isinstance(s,str) else s
def resolve(node):
    if not isinstance(node,dict): return node
    out={}
    for k,v in node.items():
        if k=='ref':
            lib,nm=fmt(v).split(':',1); out['ref']=f'{lib}:{nm}'; e=reg[lib].get(nm)
            if not e: problems.append(f'TIDAK ADA: {lib}:{nm}'); continue
            out.update({'id':e['id'],'key':e['key'],'kind':e['kind'],'page':e['page'],'defaultSize':e['defaultSize']})
            props=node.get('props',{}); chk={}
            for pk,pv in props.items():
                pv=fmt(pv); ax=e['axes'].get(pk)
                if ax is None: problems.append(f'{nm}: axis "{pk}" tidak ada (ada: {", ".join(e["axes"])})')
                elif ax['options'] and pv not in ax['options']: problems.append(f'{nm}: nilai "{pv}" untuk {pk} tidak valid (opsi: {ax["options"]})')
                chk[pk]=pv
            out['props']=chk
            tx={}
            for tk,tv in node.get('texts',{}).items():
                t=e['texts'].get(tk)
                if not t: problems.append(f'{nm}: text "{tk}" tidak ada (ada: {list(e["texts"])})')
                else: tx[t['key']]=tv
            if tx: out['textProps']=tx
            if e['slots']: out['slots_available']=[s['name'] for s in e['slots']]
        elif k in('props','texts'): continue
        elif k=='slots': out['slots']={sk:resolve(sv) for sk,sv in v.items()}
        elif isinstance(v,dict): out[k]=resolve(v)
        elif isinstance(v,list): out[k]=[resolve(x) if isinstance(x,dict) else fmt(x) for x in v]
        else: out[k]=fmt(v)
    return out
def build(rec):
    res={'recipe':name,'program':prog,'title':rec['title'],'size':rec.get('size')}
    if rec.get('extends'):
        base=R['recipes'][rec['extends']]; res['shell']=resolve(base['tree']); 
        if 'headerOverride' in rec: res['shell']['slots']['Header']=resolve(rec['headerOverride'])
    for k in ('tree','body','bodyPrefix','then','alt','generic','variants','adjacent','domain','fields','states'):
        if k in rec: res[k]=resolve(rec[k])
    res['notes']=(R['recipes'][rec['extends']].get('notes',[]) if rec.get('extends') else [])+rec.get('notes',[])
    return res
out=build(rec); out['problems']=problems
print(json.dumps(out,ensure_ascii=False,indent=1))
sys.exit(1 if problems else 0)
