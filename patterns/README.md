# Patterns — pola layar dari design file SWT 3.0

Dipelajari dari layar produksi (103 halaman, 1.523 frame, 1.233 dianalisis struktur). Dipakai agent untuk meniru pola yang benar, bukan menebak.

| File | Isi |
|---|---|
| `patterns.json` | 14 pola (shell, wizard, auth, overlay, anotasi): struktur slot, state frame, aturan, jumlah frame |
| `modules.json` | 78 modul/halaman: Rail Active, Sidebar + Open Menu, Header, komponen isi, nama state frame, contoh frame (id + link internal) |
| `module.py` | `python3 patterns/module.py <kata>` atau `--list` |
| `../docs/08-screen-patterns.md` | dokumentasi terbaca untuk agent dan manusia |
| `../report/swt-patterns.html (privat, tidak ada di repo ini)` | galeri publik (wireframe skematik, tanpa data dan tautan) |

Bangun dengan: `python3 registry/plan.py <recipe> --program SWT --module <modul>` (recipe terverifikasi terhadap SWT 3.0).
