#!/usr/bin/env python3
"""Cari komponen tanpa membaca semua file.
Pakai:  python3 registry/find.py <kata kunci...> [--lib SHIELD|GUN|Foundation] [--full] [--limit N]
        python3 registry/find.py --icon chevron
Contoh: python3 registry/find.py tombol --full ; python3 registry/find.py table booking --lib GUN
"""
import json,sys,os,re
D=os.path.dirname(os.path.abspath(__file__))
def L(n): return json.load(open(os.path.join(D,n)))
args=sys.argv[1:]
if not args or args[0] in('-h','--help'): print(__doc__); sys.exit(0)
def opt(name,default=None,flag=False):
    global args
    if name in args:
        i=args.index(name)
        if flag: args.pop(i); return True
        v=args[i+1]; del args[i:i+2]; return v
    return default
full=opt('--full',flag=True); lib=opt('--lib'); limit=int(opt('--limit','12')); icon=opt('--icon')
if icon:
    ic=L('icons.json'); hits=[(n,v) for n,v in ic.items() if icon.lower() in n.lower()]
    for n,v in hits[:60]: print(f"{n} | key {v['key']}")
    print(f"-- {len(hits)} icon cocok (tampil {min(60,len(hits))}). Impor: figma.importComponentByKeyAsync(key)"); sys.exit(0)
q=' '.join(args).lower(); al=L('aliases.json')
terms=set(q.split()); 
for w in list(terms):
    if w in al: terms|=set(al[w].split())
idx=L('index.json'); full_data={'SHIELD':None,'GUN':None,'Foundation':None}
def score(e):
    n=e['n'].lower(); p=e['p'].lower(); s=0
    for t in terms:
        if t in n: s+=3 + (2 if n==t or n.startswith(t) else 0)
        elif t in p: s+=1
    if not s: return 0
    if e['l']=='SHIELD': s+=0.5          # generik dulu
    if n.startswith('.'): s-=2           # private/base set
    return s
res=sorted([(score(e),e) for e in idx if (not lib or e['l'].lower()==lib.lower())],key=lambda x:-x[0])
res=[r for r in res if r[0]>0][:limit]
if not res: print('tidak ada hasil untuk:',q); sys.exit(1)
for s,e in res:
    print(f"[{e['l']}] {e['n']} | page: {e['p']} | {e['kind']} v{e['v']} | id {e['id']} | key {e['k']}")
    if full:
        data=full_data[e['l']] or L({'SHIELD':'shield.json','GUN':'gun.json','Foundation':'foundation-assets.json'}[e['l']]); full_data[e['l']]=data
        d=next(x for x in data if x['key']==e['k'])
        for a,v in d['axes'].items(): print(f"    axis {a} = {v['default']!r} | {' / '.join(map(str,v['options'][:14]))}")
        for b in d['booleans']: print(f"    bool {b['name']} = {b['default']}  (key {b['key']})")
        for t,v in d['texts'].items(): print(f"    text {t} = {v['default']!r}  (key {v['key']})")
        for x in d['instanceSwaps']: print(f"    swap {x['name']}  (key {x['key']})")
        for x in d['slots']: print(f"    slot {x['name']}  (key {x['key']})")
        if d.get('defaultSize'): print(f"    default {d['defaultSize'][0]}x{d['defaultSize'][1]} layout {d['layout']}")
