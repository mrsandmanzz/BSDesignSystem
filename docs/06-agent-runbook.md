# Agent runbook — dari permintaan designer sampai layar jadi

Prinsip: **cari di registry, bukan di Figma**. Registry sudah memuat key, axis, slot, dan ukuran semua komponen (`registry/README.md`). Waktu agent dipakai untuk menyusun layar, bukan membaca ulang 600 komponen.

## 0 · Prasyarat (30 detik)
1. `figma_get_status` → pastikan file target benar (banyak file terhubung sekaligus). Pin dengan `figma_navigate … lock:true` untuk kerja panjang.
2. Library **Foundation, SHIELD, GUN** harus ter-enable di file target; jika import gagal, minta designer mengaktifkannya (Assets → Libraries).
3. Jangan membuka/scan file library untuk "melihat komponen". Itu tugas registry.

## 1 · Pahami permintaan
Tentukan: **program** (SWT/CMT/CTT), **jenis layar** (list, detail, wizard, modal…), **data/teks** yang harus muncul. Kurang jelas → tanya satu pertanyaan, jangan menebak program.

## 2 · Pilih pola
Cek dulu modul yang dimaksud: `python3 patterns/module.py <modul>` (Rail Active, Sidebar + Open Menu, state frame yang diharapkan). Pola terverifikasi: `docs/08-screen-patterns.md`.

`python3 registry/plan.py --list` → pilih recipe. Contoh:
```bash
python3 registry/plan.py list-page --program SWT --module bookings   # kerangka + body + variasi
python3 registry/plan.py create-wizard --program CMT
```
Hasil JSON berisi `ref`, `key`, `kind` (set/component), `props` (sudah divalidasi), `textProps` (key lengkap), `slots`. Masalah (`problems`) berarti nama/nilai tidak valid → perbaiki sebelum menyentuh Figma.

## 3 · Cari komponen tambahan (bila perlu)
```bash
python3 registry/find.py tabel aset --lib GUN
python3 registry/find.py tombol --full          # axis, boolean, text, slot lengkap
python3 registry/find.py --icon calendar        # key icon
python3 registry/find_token.py warning text
```

## 4 · Bangun (satu `figma_execute` per bagian, ≤ 30 detik)
Gunakan `registry/snippets.js`. Urutan:
1. Buat frame layar di kanvas (1440×900 untuk kerangka); `placeFrame`.
2. `makeInstance(key, kind, props)` untuk kerangka → isi slot dengan `fillSlot` (Rail, Sidebar, Header, Body).
3. Isi body: Section Layout → slot Content → tabel/Key Value/field.
4. Ganti teks: properti teks (`textProps`) atau `setInnerText` untuk teks tak terekspos.
5. Icon: `swapIcon` dengan key dari `find.py --icon`.
6. Data contoh: gunakan teks realistis sesuai domain; jangan bind ke token `content (…)` Foundation (itu data contoh, bukan token gaya).

Aturan teknis yang sudah terbukti:
- **Set bersloT** (GUN Section Layout, SHIELD Key Value…): jangan impor lewat key (menggantung); ambil dari instance yang sudah ada di file (`setFromExistingInstance`).
- Bangun per bagian (<10 dtk per panggilan); Body slot ber-auto-layout vertikal; `layoutAlign='STRETCH'` untuk anak.
- Nilai axis persis registry (`md*`, `Collopsed`); set **Size eksplisit**.
- Selalu `setProperties` dalam satu panggilan; nama properti non-variant memakai key lengkap dengan `#id`.
- Jangan detach; jangan ubah fill/stroke/radius/gap instance.
- Token pada node kustom: hindari frame kustom. Bila tak terhindarkan, pakai `boundVariableByName` + `bindFill` (snippets §7); **jangan** `importVariableByKeyAsync`.
- Jangan `findAll(()=>true)` pada file besar; pakai `findAllWithCriteria`.

## 5 · Verifikasi (wajib)
1. `figma_take_screenshot` pada frame → cek tata letak, teks terpotong, slot kosong.
2. `lintFrame(frame)`: 0 instance tanpa main component, 0 non-library, fill tak terikat hanya pada elemen kustom yang disengaja.
3. Bandingkan dengan `docs/05-screen-recipes.md` §5 (hindari).
4. Maksimal 3 iterasi perbaikan, lalu laporkan sisa masalah.

## 6 · Serahkan
Laporkan: recipe yang dipakai, program, daftar komponen (nama + page), penyimpangan (GAP / *verify*), temuan audit yang relevan (mis. tidak ada state focus: F-54).

## 7 · Anggaran waktu/konteks (aturan jempol)
| Langkah | Cara | Hindari |
|---|---|---|
| Cari komponen | `find.py` / `plan.py` (milidetik) | memindai file library (menit, bisa crash) |
| Tahu properti | `--full` | membuka Dev Mode satu per satu |
| Token | `find_token.py` / `registry/tokens.md` | membaca halaman docs Foundation (stale, Indigo) |
| Cek hasil | screenshot + `lintFrame` | audit penuh file |

## 8 · Pembaruan registry
Bila komponen berubah di Figma: jalankan ulang ekstraksi (lihat `sources/figma-sources.md (privat, tidak ada di repo ini)`, bagian *How to re-extract*; registry dibangkitkan dari `findAllWithCriteria` + `componentPropertyDefinitions`), proses ke `registry/*.json`, dan catat di `CHANGELOG.md`.
