# Changelog

## 2026-11-20 — v0.11.1 setup & kasus terburuk untuk skill
- Skill kini punya **pesan pertama**: sebelum menyentuh Figma, designer diberi tahu apa yang akan dilakukan, apa yang dibutuhkan, apa yang diubah (hanya halaman sandbox), risiko, lalu ditanya satu pertanyaan. Penanda `.onboarded` di folder skill; pesan muncul lagi hanya bila versi skill naik.
- Added `registry/preflight.py` (hanya baca; exit 2 = FAIL): file wajib, JSON rusak, file kosong (placeholder Drive), jumlah entri vs `VERSION.json` (sinkron sebagian), salinan konflik, registry basi, skill lebih tua dari `min_skill_version`, versi Python. Diuji pada 8 salinan yang sengaja dirusak: semuanya terdeteksi, kontrol sehat OK.
- Added `skill/graphene-figma-builder/references/setup.md`: pesan pertama, 10 cek Figma berurutan, 17 kasus negatif/terburuk beserta perilaku aman dan larangan, pembersihan setelah gagal, bentuk pesan berhenti (apa terjadi, kenapa, apa yang perlu dilakukan, apa yang tidak diubah).
- `install.sh` menyalin `references/` dan menjaga `.onboarded`; `VERSION.json` punya `min_skill_version`.
- BELUM diuji: perilaku skill di sesi Claude nyata (apakah pesan pertama tampil lebih dulu), cek Figma B1–B10 (butuh plugin), cek library via `teamLibrary` (belum pernah dijalankan).

## 2026-11-20 — v0.11.0 skill untuk designer (draf)
- Added `skill/graphene-figma-builder/SKILL.md` (alur: cari folder data → cek koneksi Figma → plan → pilih sumber komponen → cek drift → build → verifikasi) dan `skill/install.sh` (memasang ke `~/.claude/skills`, menulis `DATA_PATH`). Installer diuji ke folder sementara; skill BELUM diuji dipicu oleh Claude di sesi nyata.
- Executor: contoh bisa `page:<nama halaman>` selain ID frame (lolos cek sintaks; BELUM dijalankan di Figma — plugin tidak terhubung).
- Added `registry/VERSION.json` + `registry/stamp.py` (stempel versi/tanggal untuk deteksi registry basi).
- Belum ada: skill pemelihara (refresh/tambah sistem desain), cek drift otomatis di executor (baru instruksi di skill), struktur multi-sistem (`systems.json`).

## 2026-11-19 — v0.10.0 executor (draf, BELUM teruji di Figma)
- Added `registry/executor.js` (op: page, frame, inst, text, slotAlign, stretch, fit, theme, verify; resumable via clientStorage, race-timeout, fallback impor vkey→component→set→seed) dan `registry/build.py` (plan.py → skrip figma_execute). Sintaks & kompilasi spec diperiksa offline.
- UJI 2026-11-19 (SWT 3.0, halaman `claude test`): impor via variant key berhasil untuk set bersloT (Section Layout, Key Value) ±0,1–1,8 dtk, tanpa hang (impor set bersloT lewat set key tetap menggantung). `new Function` tersedia di sandbox plugin.
- Executor end-to-end: 7 langkah, 28 instance, 0 detach/non-library, 24 dtk (3 komponen jatuh ke seed setelah timeout 7 dtk). Setelah variant key disimpan di `registry/variants.json` (10 komponen): ±9 dtk, 8 dtk di antaranya impor pertama Page Layout Template.
- Variant key diekstrak dari SHIELD (277) dan GUN (431) ke `registry/variants.json` (708 entri): menutup 598 dari 607 baris registry (SHIELD 220/222, GUN 378/385). Ekstraksi hanya-baca, per halaman ≤30 dtk.
- Uji Body kaya: percobaan pertama timeout di langkah Step1 Training Details lalu plugin mati; frame sisa dihapus. Diisolasi per komponen (import 0,5–2,2 dtk, createInstance 0,4 dtk, setProperties <10 ms, append ke slot 37 ms) — semua cepat, kegagalan TIDAK dapat direproduksi (dugaan: gangguan sesaat/beban plugin setelah ekstraksi besar di file lain). Batas waktu executor dinaikkan (impor 20 dtk, langkah 25 dtk).
- Op teruji (2026-11-19): `text` (78 ms, tetap INSTANCE), `stretch` (kartu 672→1392 px), `fit` (frame 900→1174 px; versi awal dengan extra tetap meleset 36 px, diganti hitung dari posisi slot). Frame uji sementara dihapus.
- Op `swapVariant` teruji: Wizard 4 langkah → 3 langkah (Property 1=Individual), 1,6 dtk, visual terverifikasi. Varian diambil dari set yang sudah ada di dalam instance; impor `importComponentByKeyAsync('c2d731fb…')` (varian Wizard Item) timeout 15 dtk walau set-nya sudah ter-impor → jangan impor ulang varian saudara, ambil dari `main.parent.children`.
- `build.py` kini mendukung resep berbentuk shell/body (list-page) → spec terkompilasi dengan benar (Rail, Sidebar, Header Nav, Page Header, Section Layout - Table, Table - Booking List).
- GAGAL 2026-11-19: impor `Page Layout Template` generik (ddb2f6c1…, shell list-page) timeout 20 dtk; percobaan kedua dengan batas 120 dtk mematikan plugin SWT 3.0 (bridge terputus). Sisa: frame kosong "List - Bookings (executor)" di `claude test` (y=2400), perlu dihapus. Jalur ini TIDAK aman: shell list-page belum bisa dibangun lewat executor.
- BERHASIL 2026-11-19 (jalur POOL): layar List - Bookings dibangun dengan komponen yang diambil dari frame contoh di file (`getMainComponentAsync` → `createInstance`, tanpa impor): Page Layout Template, Rail, Sidebar-SWT, Header Nav, Page Header, Section Layout - Table, Table - Booking List. 369 instance, 0 detach/non-library, tiap langkah <1,6 dtk. Executor kini punya `spec.example` + pool; `build.py --example <frameId>`.
- VALIDASI END-TO-END 2026-11-19: spec dari `build.py list-page --example 6315:27803 --extra …` dijalankan executor: 14 langkah, 2,2 dtk, 369 instance, 0 detach/non-library, semua `via: pool`; hasil visual sama dengan perbaikan manual. Op `stretch` (grow:false untuk Body/Content; default untuk Sidebar/Rail) + `fit` memperbaiki tabel melebar & Sidebar/Rail tak memanjang.
- (Catatan sebelumnya, SUDAH diperbaiki) Cacat visual list: tabel Column=Min 1608 px melebihi body 1096 px (perlu atur lebar/stretch), Sidebar/Rail tidak ikut memanjang saat frame ditinggikan (986 px). Belum diperbaiki di executor.
- Run ulang: 11 langkah, 84 instance, 0 detach/non-library, 3,2 dtk total, Dark mode via explicit mode `+Theme`. Visual: 3 kartu (Training Details, Station Configuration, Contact Information) tampil benar. Catatan: isi melebihi tinggi frame 900 → butuh op `fit` (belum diuji).
- Belum ada: 9 baris registry tanpa variant key (fallback seed), op isi Body kaya (kartu, form), pembanding waktu vs manual.

## 2026-11-10 — v0.9.0 uji bangun layar nyata
- Dibuat halaman `claude test` di SWT 3.0 dengan 2 layar Create Booking Step 1 (Dark; Side Summary) dari registry: Page Layout Template - Create Booking, Header Nav, Wizard + swap Wizard Item, 3 kartu langkah, Section Layout + Key Value.
- Temuan teknis: impor set bersloT lewat key menggantung → ambil dari instance yang ada; bangun bertahap; Dark mode via explicit variable mode. Dicatat di registry/README.md, snippets.js, runbook.

## 2026-11-10 — v0.8.0 pola layar dari design file SWT 3.0
- Dipindai frame demi frame: 103 halaman, 1.523 frame, 1.233 dianalisis. Sumber instance: SHIELD 61,4%, icon Graphene 33,9%, GUN 3,7%, lain 1,0% (tanpa halaman backlog).
- Added `patterns/` (patterns.json, modules.json, module.py), `docs/08-screen-patterns.md`, `report/swt-patterns.html (privat, tidak ada di repo ini)` (galeri publik, wireframe skematik tanpa data/tautan).
- Recipes diverifikasi ulang: Header slot = SHIELD Header Nav {Breadcrumb=1} (bukan Page Header); overlay = frame terpisah; recipe baru: list-page-tabs, detail-tabs, detail-sections, dashboard, overlay-drawer, overlay-modal, toast, auth-login; `plan.py --module`.
- Catatan: pemindaian satu panggilan >60 dtk mematikan plugin; pakai potongan ≤40 dtk dengan progres di penyimpanan plugin.

## 2026-11-10 — v0.7.0 architecture corrected to 4 layers
- Arsitektur yang benar: **Graphene (L1: color, tipografi) → SHIELD (L2: main component) → GUN (L3: business component) → Design file (L4)**. Sebelumnya dokumen menyebut 3 layer dengan "Base = Graphene + SHIELD" — keliru.
- Updated: docs/01-architecture.md (privat, tidak ada di repo ini), README, CLAUDE.md, audit docs, findings (wording), knowledge graph (layers, nodes, edges), sources, PDF.
- Entri CHANGELOG lama yang menyebut "Base layer" dibiarkan sebagai riwayat.

## 2026-11-10 — v0.6.0 registry & screen recipes (mapping untuk agent)
- Added `registry/`: SHIELD (222) + GUN (385) + Foundation assets + 1,602 icons + tokens (key, id, axes, slots, defaults), `find.py`, `find_token.py`, `plan.py`, `recipes.json` (9 recipes × 3 programs, all refs validated), `snippets.js`.
- Added `docs/05-screen-recipes.md`, `docs/06-agent-runbook.md`.
- Verified in Figma (temp instances, removed): import by key, setProperties, instance-swap icon, slot fill, inner-text override. Found: `importVariableByKeyAsync` hangs the plugin; full-page scans crash it.
- Note: two throwaway test frames (`__registry_test__`) were left in GUN by crashed runs and were removed.

