#!/usr/bin/env python3
"""Cari modul/halaman SWT 3.0: Rail Active, Sidebar+Open Menu, header, komponen isi, state frame, contoh frame.
Pakai: python3 patterns/module.py <kata>   contoh: module.py booking | module.py "asset list" | module.py --list"""
import json,sys,os
D=os.path.dirname(os.path.abspath(__file__)); M=json.load(open(os.path.join(D,'modules.json')))
a=sys.argv[1:]
if not a or a[0] in('-h','--help'): print(__doc__); sys.exit(0)
if a[0]=='--list':
    for m in M: print(f"{m['page']:55} frames {m['frames']:3} {m['kinds']}")
    sys.exit(0)
q=' '.join(a).lower(); hits=[m for m in M if q in m['page'].lower()]
if not hits: print('tidak ada modul untuk:',q); sys.exit(1)
for m in hits[:6]:
    print(f"## {m['page']}  flags={m['flags']}  frames={m['frames']} {m['kinds']}")
    print('  rail Active =',m['rail'],'| sidebar',m['sidebar'],'| header',m['header'])
    print('  isi:',[c for c,_ in [(x[0],x[1]) for x in m['content']]][:8])
    print('  state frame:',m['stateNames'][:14])
    for k,v in m['examples'].items(): print('  contoh',k,':',[(e['name'],e['id']) for e in v])
