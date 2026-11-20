# Screen recipes — membuat layar dari komponen yang benar

Tujuan: ketika designer meminta *"buatkan layar daftar booking SWT"*, agent **tidak membangun dari nol** dan **tidak memindai library**. Ia memilih recipe, menjalankan `python3 registry/plan.py <recipe> --program <SWT|CMT|CTT>`, dan mendapat key + nilai property yang sudah divalidasi. Runbook langkah demi langkah: `docs/06-agent-runbook.md`.

> Status: recipe disusun dari **anatomi komponen** yang dibaca dari Figma (slot, ukuran, axis) dan semua referensinya divalidasi otomatis terhadap registry (9 recipe × 3 program, 0 masalah). Item bertanda **verify** belum dibandingkan dengan layar produksi (layer design file belum diaudit).

## 1. Anatomi layar 1440×900

```
┌──────┬────────────┬───────────────────────────────────────────┐
│ Rail │  Sidebar   │ Header (slot, 1144×60)                    │
│ 56   │  240       ├───────────────────────────────────────────┤
│ ×900 │  ×900      │ Body (slot, 1096×792)                     │
│      │            │   ↳ Section Layout / Section Layout - Table│
└──────┴────────────┴───────────────────────────────────────────┘
GUN Page Layout Template  (id 4:665)  slot: Navigation Rail · Sidebar · Header · Body
```
Spacing halaman memakai token `page spacing/*`: page 24 · section 20 · sub-section 16 / 12 (lihat `registry/tokens.md`). Slot dan Section Layout sudah terikat token; **hindari membuat frame kustom**.

## 2. Pola → komponen (ringkas)

| Pola | Komponen utama | Catatan kunci |
|---|---|---|
| Kerangka layar | GUN `Page Layout Template` | Rail.Active = program; Sidebar = `Sidebar-SWT/CMT/CTT` |
| Daftar + tabel | GUN `Section Layout - Table` (`Table is` Default/Scrollable/No Pagin) + tabel GUN + SHIELD `Pagination` | Pagination sudah ada di dalam, kecuali `No Pagin` |
| Detail | GUN `Section Layout` + SHIELD `Key Value` + GUN `Badge - … Status` | Header: SHIELD `Page Header/Left Content` Item *Booking Details / Assignment Details / Asset Details / User…* |
| Wizard | GUN `Page Layout Template - Create Booking` + `Header Nav - Create Booking` + `Wizard - Create Booking` | `Located` First/Mid/Last; item per program |
| Konfirmasi | GUN `Modal Confirmation - <Delete/Remove/Archive/Cancel Booking/…>` | Termasuk Scrim 1440×900 |
| Modal form | SHIELD `Modal` (Size xs–full) + slot | Domain: `Modal - Import Booking`, `Modal - SWT - Import Nominal Roll …` |
| Filter | GUN `Filter - <program/halaman>` (360×818) di SHIELD `Drawer Right` | **verify** penempatan |
| Field | SHIELD `Input`, `Text Area`, `Input - Single Select`, `Date Picker`, `Checkbox`, `Radio `, `Toggle` | Selalu set `Size` eksplisit |
| Umpan balik | SHIELD `Toast`, `Alert`; GUN `Empty State - Business Components` | |
| Kalender | GUN `Calendar Booking List - Month SWT/CMT/CTT`, `Week New`, `Day New` | F-56: kartu kalender SHIELD menyarangkan Badge GUN |

## 3. Matriks program

| | SWT | CMT | CTT |
|---|---|---|---|
| Rail `Active` | `SWT` | `CMT` | `CTT` |
| Sidebar | `Sidebar-SWT` | `Sidebar-CMT` (+ menu *Master Data*) | `Sidebar-CTT` |
| Header Nav `Program` | `SWT` (Ongoing/Onboarding: `SWT-Collective`/`SWT-Marksmanship`) | `CMT` | `CTT` |
| Tabel booking | `Table - Booking List` | `Table - CMT - Booking List` | `Table - CTT - Booking List` |
| Filter booking | `Filter - SWT - Booking List` | `Filter - CMT - Booking List` | `Filter - CTT - Booking List` |
| Wizard item | `Wizard Item - Create Booking SWT` | `… CMT` | `… CTT` |
| Kalender | `Calendar Booking List - Month SWT` | `… Month CMT` | `… Month CTT` |
| Dropdown khusus | — | `Dropdown List - CMT CTT` (Role, Platform Type, Call Sign, Training Type/Course) | sama |

## 4. Resep terperinci

Gunakan `plan.py` untuk key/id. Bagian ini menjelaskan *mengapa* dan jebakannya.

### R1 · app-shell
`GUN Page Layout Template` (komponen lepas, `importComponentByKeyAsync`). Isi 4 slot:
`Navigation Rail` ← `Rail{Active}` · `Sidebar` ← `Sidebar-{program}{Open Menu}` · `Header` ← `Page Header` (**verify**) · `Body` ← isi layar.

### R2 · list-page
Body ← `Section Layout - Table{Table is=Default, Top Content=False, Mid Content=False}`; slot `Content` ← tabel; slot `🔄 Right Content` ← `Button` primary (label *Buat Baru*, icon `Icon / plus` lewat swap `🔄 Prefix Icon`).
- **Tabel:** pilih keluarga GUN (`find.py table <topik> --lib GUN`). Bila tidak ada, rakit dari SHIELD `Table - Header Cell` (State: Checkbox/Text/Empty/Text with Sort/Text Align Right) + `Table - Body Cell` (State: 34 tipe, mis. *Text Bold*, *Text+Badge*, *Text Primary Success*); tinggi header 48, baris 64.
- **Kosong:** ganti Content dengan `Empty State - Business Components{What=Table|Search|…}`.
- **Judul section:** `Section Header` (SHIELD) di dalam layout; Left Content Item *Title & Subtitle / & Count*. Teks judul bukan property → ubah TEXT node.

### R3 · detail-page
Header = `Page Header` dengan Left Content `Item` sesuai entitas. Body ← `Section Layout`; isi dengan baris `Key Value` (Type Text/Badge/Text+Badge/Chips, Layout Left-Left/Left-Right/Vertical). Status domain memakai Badge GUN (Booking/Asset/Assignment/Stage/Site Mgmt/Attendance…), **bukan** SHIELD `Badge` generik. Untuk detail booking SWT ada set siap pakai per status (`Booking Details - Details - Upcoming|Ongoing|Completed|Return Asset|Cancelled`, juga `Multi CW`).

### R4 · create-wizard
`GUN Page Layout Template - Create Booking` (tanpa Rail/Sidebar): slot `Header` ← `Header Nav - Create Booking{Program}`; `Wizard` ← `Wizard - Create Booking{Located, Skip Button}` dengan swap `Wizard Item` ← `Wizard Item - Create Booking {SWT|CMT|CTT}`; `Body` ← form langkah. Header Nav: Title/Subtitle diubah lewat TEXT node (diuji: tetap instance). Alur lain: `Wizard - Others` (Onboarding, Asset Audit, Ongoing Session).

### R5 · confirm-modal
Pakai set GUN yang sudah mengikat teks domain: `Modal Confirmation - Delete{What=Role|Rank|Briefing room|Location|SystemVersion|Base Station|Lane|…, Blocked Delete}`, `- Cancel Booking{What=Toast|Modal, Booking is=…}`, `- Remove`, `- Move to archive`, `- Restore from archive`, `- Reset Password`, `- Bulk`, `- Discard`, `- Alarm On Off`, `- Ready For Return Assets`. Generik: SHIELD `Modal Confirmation{Status=Warning|Success|Danger|Neutral, Size}` + `Scrim`.

### R6 · form-field
Lihat `recipes.json → form-field`. Aturan: label/placeholder/caption lewat properti teks (`Label Text`, `Placeholder Text`, `Caption Text`), validasi lewat `Status`, `Disabled`/`Read-only` sebagai axis. Date Picker: **hanya** `Date Picker`, bukan `.Date Picker - Month`, `.Datetime Picker`, `.xDate Picker - Booking` (legacy, F-32/F-59).

## 5. Hindari (temuan audit yang memengaruhi pembuatan layar)

| Hindari | Alasan | Gunakan |
|---|---|---|
| Set legacy `.Date Picker - Month`, `.Datetime Picker`, `.Date Picker - Date Range`, `.Attachment File`, `.xDate Picker - Booking` | token lama, font Poppins, F-32/F-59 | `Date Picker`, `Dropzone` |
| `Table - Training Results - Nominal Roll (Old)`, `… Duplicated`, `Table - Operational Availability` (ada `New`) | generasi lama (F-49) | versi `New` / tanpa `(Old)` |
| `text/invert/{role}` untuk teks di fill tint | kontras 1,00:1 (F-62) | `text/{role}` |
| Teks putih di warning solid (Light) | 1,92:1 (F-23) | teks gelap |
| Komponen tanpa state focus untuk elemen interaktif | belum ada focus state (F-54) | beri catatan handoff; jangan mengarang fokus |
| SHIELD baris domain (Notifications List, Table - Body Cell - CMT/CTT Role, Sidebar Item/Program …) | dimiliki ganda (F-44) | versi GUN bila ada |
| Detach instance, hex/px mentah, frame kustom | memutus propagasi | slot + Section Layout |

## 6. Jika recipe tidak cukup
Laporkan GAP (format di `docs/04-agent-playbook.md` §6) alih-alih membuat komponen baru. Sertakan hasil `find.py` yang sudah dicoba.
