#!/usr/bin/env python3
"""preflight.py — cek lokal sebelum membangun layar. HANYA membaca; tidak mengubah apa pun.

Pakai:  python3 registry/preflight.py [--skill-version N] [--json] [--max-age-days 45]
Keluar: 0 = semua OK/WARN, 2 = ada FAIL (jangan lanjut build).
Cek Figma (MCP, plugin, file target, library, frame contoh) dilakukan Claude lewat tool, lihat references/setup.md.

Yang dideteksi (kasus negatif/terburuk di sisi folder data):
  file wajib hilang · JSON rusak/terpotong · file kosong (placeholder Drive "hanya online") · jumlah entri
  tidak cocok dengan VERSION.json (sinkron sebagian) · salinan konflik Drive/Dropbox/Git · registry basi ·
  skill lebih tua dari yang dibutuhkan registry · Python terlalu lama.
"""
import argparse, datetime, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
REQUIRED = ["registry/plan.py", "registry/build.py", "registry/executor.js", "registry/find.py", "registry/recipes.json",
            "registry/shield.json", "registry/gun.json", "registry/variants.json", "registry/VERSION.json",
            "patterns/patterns.json", "patterns/modules.json", "CLAUDE.md"]
JSONS = ["registry/recipes.json", "registry/shield.json", "registry/gun.json", "registry/variants.json",
         "registry/VERSION.json", "patterns/patterns.json", "patterns/modules.json", "registry/index.json"]
CONFLICT = re.compile(r"(\(\d+\)|conflict|konflik|\bcopy\b|salinan|\.orig$|\.rej$|~$)", re.I)

checks = []
def add(id, status, msg, fix=""):
    checks.append({"id": id, "status": status, "msg": msg, "fix": fix})

def count(path):
    d = json.load(open(path))
    if isinstance(d, dict): return len([k for k in d if not str(k).startswith("_")])
    return len(d)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-version", type=int, default=None)
    ap.add_argument("--max-age-days", type=int, default=45)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if sys.version_info < (3, 8):
        add("python", "FAIL", "Python %s terlalu lama (butuh 3.8+)." % sys.version.split()[0], "Pasang Python 3 terbaru.")
    else:
        add("python", "OK", "Python %s." % sys.version.split()[0])

    missing = [f for f in REQUIRED if not (ROOT / f).exists()]
    if missing:
        add("files", "FAIL", "File wajib hilang: " + ", ".join(missing),
            "Sinkronisasi folder belum lengkap. Tunggu Drive selesai menyinkronkan, atau minta pemelihara mengirim ulang folder.")
    else:
        add("files", "OK", "Semua file wajib ada.")

    empty = [f for f in REQUIRED if (ROOT / f).exists() and (ROOT / f).stat().st_size == 0]
    if empty:
        add("empty", "FAIL", "File kosong (0 byte): " + ", ".join(empty),
            "Kemungkinan file Drive berstatus 'hanya online'. Klik kanan folder → Offline access / 'Available offline', lalu tunggu selesai.")

    bad = []
    for f in JSONS:
        p = ROOT / f
        if p.exists() and p.stat().st_size > 0:
            try: json.load(open(p))
            except Exception as e: bad.append("%s (%s)" % (f, str(e)[:60]))
    if bad:
        add("json", "FAIL", "JSON rusak/terpotong: " + "; ".join(bad),
            "Sinkronisasi terputus di tengah atau file teredit. Sinkronkan ulang folder; jangan edit file registry dengan tangan.")
    elif not missing:
        add("json", "OK", "Semua JSON terbaca.")

    ver = None
    vp = ROOT / "registry/VERSION.json"
    if vp.exists() and vp.stat().st_size > 0:
        try: ver = json.load(open(vp))
        except Exception: ver = None
    if ver:
        mism = []
        for k, v in (ver.get("counts") or {}).items():
            p = ROOT / "registry" / (k + ".json")
            if p.exists() and p.stat().st_size > 0:
                try:
                    n = count(p)
                    if n != v: mism.append("%s: tercatat %s, ada %s" % (k, v, n))
                except Exception: pass
        if mism:
            add("counts", "FAIL", "Jumlah entri tidak cocok dengan VERSION.json (" + "; ".join(mism) + ").",
                "Sinkron sebagian atau ada yang mengubah file. Sinkronkan ulang; jika tetap, minta pemelihara menjalankan registry/stamp.py setelah refresh.")
        else:
            add("counts", "OK", "Jumlah entri cocok dengan VERSION.json.")
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(ver["date"])).days
            if age > a.max_age_days:
                add("age", "WARN", "Registry berumur %d hari (batas %d). Komponen di library mungkin sudah berubah." % (age, a.max_age_days),
                    "Beri tahu pemelihara untuk refresh. Boleh lanjut, tapi cek drift ekstra teliti.")
            else:
                add("age", "OK", "Registry versi %s, %s (%d hari)." % (ver.get("version"), ver.get("date"), age))
        except Exception:
            add("age", "WARN", "Tanggal di VERSION.json tidak terbaca.", "Minta pemelihara menjalankan registry/stamp.py.")
        need = ver.get("min_skill_version")
        if need and a.skill_version is not None and a.skill_version < need:
            add("skill", "FAIL", "Skill versi %s lebih tua dari yang dibutuhkan registry (%s)." % (a.skill_version, need),
                "Jalankan ulang: bash skill/install.sh, lalu mulai sesi Claude baru.")
        elif a.skill_version is not None:
            add("skill", "OK", "Versi skill %s cocok." % a.skill_version)
    elif not missing:
        add("version", "WARN", "VERSION.json tidak terbaca; umur registry tidak diketahui.", "Minta pemelihara menjalankan registry/stamp.py.")

    conflicts = []
    for p in list((ROOT / "registry").glob("*")) + list((ROOT / "patterns").glob("*")) + list(ROOT.glob("*")):
        if p.is_file() and CONFLICT.search(p.name): conflicts.append(str(p.relative_to(ROOT)))
    if conflicts:
        add("conflict", "WARN", "Ada salinan konflik: " + ", ".join(conflicts[:6]),
            "Dua orang mengubah file yang sama. Jangan pakai salinan itu; minta pemelihara menentukan versi yang benar.")
    else:
        add("conflict", "OK", "Tidak ada salinan konflik.")

    worst = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "OK")
    if a.json:
        print(json.dumps({"overall": worst, "root": str(ROOT), "checks": checks}, ensure_ascii=False, indent=1))
    else:
        for c in checks:
            print("[%s] %s: %s" % (c["status"], c["id"], c["msg"]))
            if c["status"] != "OK" and c["fix"]: print("      → " + c["fix"])
        print("HASIL:", worst)
    sys.exit(2 if worst == "FAIL" else 0)

if __name__ == "__main__":
    main()
