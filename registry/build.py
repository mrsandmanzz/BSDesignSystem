#!/usr/bin/env python3
"""build.py — ubah rencana plan.py menjadi skrip siap-jalan untuk figma_execute.

Pakai:
  python3 registry/build.py create-wizard --program SWT --name "Create Booking - Step 2" --page "claude test" > build.js
  # lalu jalankan isi build.js lewat figma_execute BERULANG sampai hasilnya {done:true}.
Opsi: --dark (tambah bingkai mode Dark), --budget MS (default 18000).
Spec bisa disunting: tambahkan langkah 'inst' ke slot Body (lihat executor.js untuk op yang ada).
Status: kompiler ini menghasilkan spec dari rencana; eksekusi di Figma BELUM terverifikasi sampai uji kelayakan jalan.
"""
import argparse, json, subprocess, sys, pathlib

HERE = pathlib.Path(__file__).parent

VARS = json.loads((HERE / "variants.json").read_text())

def ref_of(n):
    r = ref_of0(n)
    if n["key"] in VARS: r["vkey"] = VARS[n["key"]]
    return r

def ref_of0(n):
    return {"key": n["key"], "kind": n["kind"], "name": n["ref"].split(":", 1)[1],
            "slotSet": any(s in n["ref"] for s in ("Section Layout", "Key Value"))}

def compile_shell(plan, name, page, dark):
    """Resep berbentuk shell/body/bodyPrefix (list-page dst). Body = [bodyPrefix?] + body; slot isi lewat --extra (parent {slot:{inst:'body',name:'Content'}})."""
    shell = plan["shell"]; size = plan.get("size") or shell["defaultSize"]
    steps = [{"op": "page", "name": page},
             {"op": "frame", "id": "frame", "name": name, "size": size, "parent": "page"},
             {"op": "inst", "id": "root", "ref": ref_of(shell), "props": shell.get("props", {}), "parent": {"frame": "frame"}}]
    for slot, node in (shell.get("slots") or {}).items():
        if isinstance(node, dict) and "key" in node:
            steps.append({"op": "inst", "id": "s_" + slot.lower().replace(" ", "_"), "ref": ref_of(node),
                          "props": node.get("props", {}), "parent": {"slot": {"inst": "root", "name": slot}}})
    bp = plan.get("bodyPrefix")
    if bp:
        steps.append({"op": "inst", "id": "bodyprefix", "ref": ref_of(bp), "props": bp.get("props", {}),
                      "parent": {"slot": {"inst": "root", "name": "Body"}}})
    b = plan.get("body")
    if b:
        steps.append({"op": "inst", "id": "body", "ref": ref_of(b), "props": b.get("props", {}),
                      "parent": {"slot": {"inst": "root", "name": "Body"}}})
    for extra in (plan.get("extra_steps") or []): steps.append(extra)
    steps.append({"op": "verify", "frame": "frame"})
    if dark: steps.append({"op": "theme", "frame": "frame", "mode": "Dark"})
    return {"id": name.replace(" ", "_"), "root": "frame", "steps": steps, "problems": plan.get("problems", [])}

def compile_spec(plan, name, page, dark):
    if "shell" in plan: return compile_shell(plan, name, page, dark)
    size = plan["size"]; root = plan["tree"]
    steps = [{"op": "page", "name": page},
             {"op": "frame", "id": "frame", "name": name, "size": size, "parent": "page"},
             {"op": "inst", "id": "root", "ref": ref_of(root), "props": root.get("props", {}),
              "parent": {"frame": "frame"}}]
    for slot, node in (root.get("slots") or {}).items():
        if not isinstance(node, dict) or "key" not in node:
            continue  # slot konten diisi manual oleh agent (op inst dengan parent.slot)
        sid = "s_" + slot.lower()
        steps.append({"op": "inst", "id": sid, "ref": ref_of(node), "props": node.get("props", {}),
                      "parent": {"slot": {"inst": "root", "name": slot}}})
    for extra in (plan.get("extra_steps") or []): steps.append(extra)
    steps.append({"op": "verify", "frame": "frame"})
    if dark:
        steps.append({"op": "theme", "frame": "frame", "mode": "Dark"})
    return {"id": name.replace(" ", "_"), "root": "frame", "steps": steps,
            "problems": plan.get("problems", [])}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe"); ap.add_argument("--program", default="SWT"); ap.add_argument("--module")
    ap.add_argument("--name", default="Screen"); ap.add_argument("--page", default="claude test")
    ap.add_argument("--dark", action="store_true"); ap.add_argument("--budget", type=int, default=18000)
    ap.add_argument("--extra", help="file JSON berisi langkah tambahan (mis. isi slot Body)")
    ap.add_argument("--example", help="ID frame contoh di file target yang sudah memakai komponen resep (jalur pool tanpa impor)")
    ap.add_argument("--spec-only", action="store_true")
    a = ap.parse_args()
    cmd = [sys.executable, str(HERE / "plan.py"), a.recipe, "--program", a.program]
    if a.module: cmd += ["--module", a.module]
    plan = json.loads(subprocess.check_output(cmd))
    if a.extra: plan['extra_steps'] = json.load(open(a.extra))
    spec = compile_spec(plan, a.name, a.page, a.dark)
    if a.example: spec['example'] = a.example
    if a.spec_only:
        print(json.dumps(spec, indent=1, ensure_ascii=False)); return
    code = (HERE / "executor.js").read_text()
    print(code + "\nreturn await exec(" + json.dumps(spec, ensure_ascii=False) + ", {budgetMs:" + str(a.budget) + "});")

if __name__ == "__main__":
    main()
