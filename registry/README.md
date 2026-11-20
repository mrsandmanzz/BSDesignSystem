# Registry — peta komponen & token untuk agent

Tujuan: agent **tidak perlu membaca ulang seluruh komponen di Figma**. Semua yang dibutuhkan untuk memilih komponen, mengimpornya, dan mengisi propertinya sudah ada di sini. Dibangkitkan dari Figma pada 2026-11-10 (lihat `sources/figma-sources.md (privat, tidak ada di repo ini)` untuk cara refresh).

## Pakai ini, bukan scan Figma

| Kebutuhan | Perintah (murah, offline) |
|---|---|
| Cari komponen | `python3 registry/find.py tombol` · `table booking --lib GUN` · tambahkan `--full` untuk axis/properti |
| Cari icon | `python3 registry/find.py --icon calendar` |
| Cari token | `python3 registry/find_token.py danger background` |
| **Rencana build untuk satu pola layar** | `python3 registry/plan.py list-page --program SWT` (key, id, nilai property **sudah divalidasi**) |
| Daftar pola layar | `python3 registry/plan.py --list` |
| Kode bantu Plugin API | `registry/snippets.js` |

## Isi folder

| File | Isi |
|---|---|
| `shield.json` (222) | komponen UI generik: key, id, halaman, axis+opsi+default, boolean, text, swap, slot, ukuran default |
| `gun.json` (385) | komponen bisnis (SWT/CMT/CTT, operasional): sama |
| `foundation-assets.json` (6) | set aset: `.Icon`, Flag, Payment/Auth Provider, Company Logos, Brand Icons |
| `icons.json` (1.602) | nama icon → key komponen `Icon / …` (jangan dibaca penuh; gunakan `find.py --icon`) |
| `tokens.json`, `tokens.md` | token `+Theme` (warna Light/Dark, radius, width, sizing, page spacing) + primitif; `tokens.md` = contekan terbaca |
| `recipes.json` | pola layar: app-shell, list-page, detail-page, create-wizard, confirm-modal, form-modal, form-field, feedback, calendar-page |
| `index.json`, `aliases.json` | indeks ringkas + sinonim Indonesia/Inggris untuk pencarian |

## Cara impor di Figma (diuji)
- Set komponen: `figma.importComponentSetByKeyAsync(key)` → `set.defaultVariant.createInstance()` → `inst.setProperties({...})`.
- Komponen lepas (`kind: component`): `figma.importComponentByKeyAsync(key)`.
- Nilai axis harus persis string registry: `md*` (dengan bintang), `Collopsed` (typo library), axis `States`/`Disable` pada Toggle.
- **Default set sering bukan yang dipakai produk** (Button Size default `sm`, Button Icon `2xs`): selalu set `Size` eksplisit (`md*`).
- Slot: `inst.findAllWithCriteria({types:['SLOT']})` lalu `slot.appendChild(node)`.
- Teks tak terekspos (mis. Title Header Nav): ubah TEXT node di dalam instance (`loadFontAsync` dulu). Tetap instance.

## Terbukti saat membangun layar nyata (halaman `claude test` di SWT 3.0)
- `importComponentSetByKeyAsync` untuk set yang memiliki **slot** (mis. GUN `Section Layout`, SHIELD `Key Value`) **menggantung** (timeout 8 dtk, bisa mematikan plugin). Set tanpa slot (Header Nav, Wizard, Create Booking Step 1, Page Layout Template) impor normal (0,1–1 dtk).
- **Solusi:** ambil set dari instance yang sudah ada di file (`inst.getMainComponentAsync()` → `.parent` = set) lalu `defaultVariant.createInstance()`. Lihat `snippets.js` `setFromExistingInstance`.
- Bangun bertahap, satu `figma_execute` per bagian (<10 dtk); satu skrip besar yang menggabungkan semua impor pernah time-out.
- Anak instance di dalam frame auto-layout: set `layoutAlign='STRETCH'` agar lebar mengikuti kolom; Body slot: `counterAxisAlignItems='CENTER'` untuk menengahkan wrapper.
- Mode gelap: `frame.setExplicitVariableModeForCollection(collection, darkModeId)`; ambil `collection` dari variable yang sudah terikat (`getVariableByIdAsync` → `getVariableCollectionByIdAsync`). Teruji: seluruh layar berpindah ke Dark tanpa mengubah komponen.

## Larangan (menghemat waktu & mencegah crash)
- Jangan `findAll(() => true)` atau `loadAllPagesAsync()` pada file library: mematikan plugin (terjadi 3×). Gunakan `findAllWithCriteria`.
- Jangan `importVariableByKeyAsync`: menggantung (2×). Lihat `snippets.js` §7.
- Jangan membaca `shield.json`/`gun.json`/`icons.json` utuh ke konteks. Gunakan `find.py`/`plan.py`.

## Batas pengetahuan
Recipe disusun dari anatomi komponen (slot, ukuran, axis). Yang bertanda `verify` belum dibandingkan dengan layar produksi karena layer design file belum diaudit.

## Executor (v0.10, 2026-11-19)
`python3 registry/build.py <recipe> --program SWT [--module m] --name "<frame>" [--example <frameId>] [--extra langkah.json] [--dark]` → skrip untuk `figma_execute`.
- **Aman dulu:** beri `--example` = ID frame di file target yang SUDAH memakai komponen resep (executor membuat instance dari komponen utamanya, tanpa impor). Impor via key/variant key hanya cadangan; beberapa impor (Wizard Item varian, Page Layout Template generik) menggantung/mematikan plugin.
- Teruji (SWT 3.0, halaman `claude test`): wizard Create Booking (Dark, 3 kartu, swapVariant) dan List Bookings (tabel) — 2–3 dtk, 0 detach. Op: page, frame, inst, slotAlign, stretch, fit, text, swapVariant, theme, verify.
- Belum teruji: file target tanpa frame contoh, layar dashboard/detail/kalender, overlay (drawer/modal/toast).
