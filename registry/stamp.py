#!/usr/bin/env python3
"""Tulis registry/VERSION.json (tanggal + jumlah entri). Jalankan setelah setiap refresh registry.
Pakai: python3 registry/stamp.py [--note "teks"]"""
import json, sys, datetime, pathlib
H = pathlib.Path(__file__).parent
def n(f):
    d = json.load(open(H / f)); 
    return len([k for k in d if not str(k).startswith("_")]) if isinstance(d, dict) else len(d)
note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
prev = {}
try: prev = json.load(open(H / "VERSION.json"))
except Exception: pass
v = {"version": (prev.get("version", 0) or 0) + 1, "date": datetime.date.today().isoformat(),
     "counts": {k: n(k + ".json") for k in ("shield", "gun", "icons", "variants", "tokens")},
     "min_skill_version": prev.get("min_skill_version", 1),
     "note": note or prev.get("note", "")}
json.dump(v, open(H / "VERSION.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(v, ensure_ascii=False))
