#!/usr/bin/env python3
"""Cari token tanpa membaca file besar.  python3 registry/find_token.py <kata> [kata...]
Contoh: python3 registry/find_token.py danger background ; python3 registry/find_token.py radius button ; python3 registry/find_token.py page spacing"""
import json,sys,os
D=os.path.dirname(os.path.abspath(__file__)); t=json.load(open(os.path.join(D,'tokens.json')))
q=[w.lower() for w in sys.argv[1:]]
if not q: print(__doc__); sys.exit(0)
n=0
for grp in ('color','radius','width','sizing','pageSpacing','typography'):
    for name,e in t[grp].items():
        if all(w in name.lower() for w in q):
            v=f"light {e['light']} | dark {e['dark']}" if 'light' in e else f"value {e.get('value')}"
            print(f"{name} | {v} | key {e['key']}"); n+=1
print(f'-- {n} cocok (hanya token +Theme; primitif ada di tokens.json → primitives)')
