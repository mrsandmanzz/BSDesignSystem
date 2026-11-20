# Screen patterns — dipelajari dari design file SWT 3.0

Sumber: `SWT 3.0` (`DSZ8LJROLfQc6x81oAXk2I`), dipindai 2026-11-10: **103 halaman, 1.523 frame tingkat atas, 1.233 frame dianalisis strukturnya**. Pola di bawah adalah apa yang **benar-benar** dipakai di layar produksi, bukan tebakan dari komponen. Data mesin: `patterns/patterns.json`, `patterns/modules.json`; cari modul: `python3 patterns/module.py <kata>`; bangun: `python3 registry/plan.py <recipe> --program SWT --module <modul>`.

## 1. Fakta kunci

| Temuan | Angka | Arti untuk agent |
|---|---|---|
| Sumber instance (sampel, tanpa halaman backlog) | SHIELD **61,4%** · icon Graphene **33,9%** · GUN **3,7%** · lain **1,0%** | Layar dirakit dari SHIELD + icon; GUN sedikit tapi **struktural** (layout, badge domain, tabel keluarga) |
| Kerangka layar | 478 layar memakai `Page Layout Template` (Rail + Sidebar + **SHIELD Header Nav {Breadcrumb=1}** + Body) | Header slot = Header Nav, bukan Page Header |
| Wizard | 265 frame memakai `Page Layout Template - Create Booking` | Alur buat/ubah tanpa Rail/Sidebar |
| Overlay | Drawer 181 · Modal ≈176 · Toast 123 sebagai **frame terpisah** | Jangan menumpuk overlay di frame halaman |
| Tabel | 280 layar list; Section Layout - Table + tabel keluarga GUN | Pilih tabel GUN per modul, jangan merakit sel dari nol |
| Tab | Tab Group v2: 4 tab/tanpa margin (110×), 2 tab/margin (93×), 8 tab (30×) | |
| Anotasi | 290 frame (Sticker 269, Notes 21) | Bukan layar; abaikan |
| Backlog | halaman `[Backlog] TRMS CV`: 98 frame, 99% memakai UI kit lain | Jangan dijadikan acuan |
| Legacy | `Badge - Asset Status`, `Issued Asset List`, `Attendance` muncul sebagai instance dari library lain (salinan basi GUN, F-50) | Gunakan versi GUN lokal |

## 2. Anatomi layar 1440×900

```
┌──────┬────────────┬─────────────────────────────────────────┐
│ Rail │  Sidebar   │ Header   = SHIELD Header Nav {Breadcrumb=1} (60)
│ 56   │  240       ├─────────────────────────────────────────┤
│      │            │ Body 1096×792  (padding 24)             │
│      │            │   Page Header → Section Layout(s) / Tabs│
└──────┴────────────┴─────────────────────────────────────────┘
```
Semua layar aplikasi: `GUN Page Layout Template` → slot `Navigation Rail`, `Sidebar`, `Header`, `Body`.

## 3. Katalog pola

### P01 · App shell  (478 frame) — recipe `app-shell`
**Kapan:** Dasar semua layar aplikasi.

**Struktur:**
- GUN Page Layout Template (1440×900)
- slot Navigation Rail ← GUN Rail {Active=<modul>}
- slot Sidebar ← GUN Sidebar-<SWT|User Mgmt|Asset|Settings New> {Open Menu}
- slot Header ← SHIELD Header Nav {Breadcrumb=1} (478/478)
- slot Body 1096×792 ← pola P02–P08

**Aturan:** Tinggi frame mengikuti isi (900–2364); Page Layout Template ikut membesar. Body selalu dimulai SHIELD Page Header (≈120 layar) atau langsung Section Layout - Table dengan Section Header.

### P02 · List + tabel  (280 frame) — recipe `list-page`
**Kapan:** Daftar data: Booking List, Training Results, Asset/User/Rank, Activity Log, Settings tabel.

**Struktur:**
- [SHIELD Page Header]
- GUN Section Layout - Table {Table is=Default|Scrollable|No Pagin, Top Content, Mid Content}
-   Section Header (SHIELD) → judul + aksi kanan
-   slot Content ← tabel keluarga GUN (State=Filled|Empty|Search-Empty)
-   SHIELD Pagination (kecuali No Pagin)

**State frame yang lazim:** List - Empty; List - Filled; Search - Filled; Search - Empty Result; Drawer - Filter; Drawer - Filter - Selected; List - Filter Applied; List - Filter Applied - Empty; Dropdown - More; Toast - Success; Add/Edit - Empty/Error/Filled; Confirmation - Delete

**Aturan:** Filter, Add/Edit, dan konfirmasi adalah frame overlay terpisah (P11/P12), bukan di dalam frame list. Tabel lebar didokumentasikan lewat frame 'Sticker' selebar 1440+1540·n (token sticker size).

### P03 · List + tab  (147 frame) — recipe `list-page-tabs`
**Kapan:** Tab di atas/dalam tabel: Notifications, tab Nominal Roll/Lane/Blackout pada detail, tab pada hasil pelatihan.

**Struktur:**
- Page Header (opsional)
- GUN Section Layout - Table {Top Content=True}
-   slot 🔄 Top Content ← SHIELD Tab Group v2 {Number of Tab 2–8, With Margin}
-   slot Content ← tabel per tab

### P04 · Detail bertab  (212 frame) — recipe `detail-tabs`
**Kapan:** Booking Details (per status), Training Result Details, Site Management Details.

**Struktur:**
- Page Header (Left Content Item: Booking Details|Assignment Details|Asset Details|User|Base Station…)
- SHIELD Tab Group v2 {Number of Tab=4, With Margin=False} (tab paling umum)
- GUN Booking Details - Details - <Upcoming|Ongoing|Return|Completed|Cancelled>  ATAU  Section Layout - Table

**State frame yang lazim:** Details; Details - No Briefing Room; Details - Nominal Roll Empty; Details - Blackout Conflict (Multi CW); Dropdown - More Icon

**Aturan:** Status booking memilih set GUN per status; ada varian Multi CW terpisah.

### P05 · Detail berbasis section  (23 frame) — recipe `detail-sections`
**Kapan:** Settings (General, Notification), Asset/User Details, Asset Tracking, System Health.

**Struktur:**
- Page Header
- GUN Section Layout (1096 penuh, atau Row 536+536 dua kolom)
-   SHIELD Key Value / Input / Radio Group di slot Content

**Aturan:** Settings memakai Rail Active=Settings + Sidebar-Settings New.

### P06 · Dashboard  (20 frame) — recipe `dashboard`
**Kapan:** Dashboard.

**Struktur:**
- Page Header
- Row: GUN Data Display - Booking ×2 (536×156)
- GUN Data Display - Booking Team
- GUN Calendar Dashboard - Day|Week|Range|Month {State}

**State frame yang lazim:** Dashboard - Empty; Dashboard - Filled; Dashboard - Hover; Dashboard - Tab Inactive; Filled - All Completed

### P07 · Kalender booking  (21 frame) — recipe `calendar-page`
**Kapan:** Booking List mode kalender.

**Struktur:**
- Page Header
- GUN Calendar Booking List - Day New|Week New|Month SWT {State}

**Aturan:** F-56: kartu kalender SHIELD menyarangkan Badge milik GUN.

### P08 · Edit multi-tabel  (9 frame) — recipe `list-page`
**Kapan:** Resource Planning (View/Edit).

**Struktur:**
- Page Header
- Section Layout
- Section Layout - Table {No Pagin}
- Section Layout - Table {Scrollable} + SHIELD Scroll Bar + Pagination

**Aturan:** Mode Edit: frame 2000–2400px tinggi; state Edit - Add New Empty/Filled Error.

### P09 · Wizard buat/ubah  (265 frame) — recipe `create-wizard`
**Kapan:** Create Booking (5 langkah), Onboarding (4), Edit Detail List.

**Struktur:**
- GUN Page Layout Template - Create Booking (tanpa Rail/Sidebar)
- slot Header ← GUN Header Nav - Create Booking {Program} | Header Nav - Onboarding {SWT-Collective|SWT-Marksmanship} | Header Nav - Edit Detail List | Header Nav - Ongoing Session
- slot Wizard ← GUN Wizard - Create Booking {Located=First|Mid|Last, Skip Button} + swap Wizard Item
- slot Body: kolom 640 (Wrapper) atau Row 1392 = Column 288 + Column 1080

**State frame yang lazim:** Empty; Collective; Dropdown …; Empty Error; Filled; Toast - Success; Discard Booking

**Aturan:** Langkah SWT: Create Booking → Schedule → Lane Config → Nominal Roll → Review (Modal). Langkah Nominal Roll memakai Drawer Right (Add Trainee) dan Modal Import.

### P10 · Login (tanpa shell)  (5 frame) — recipe `auth-login`
**Kapan:** Autentikasi.

**Struktur:**
- Frame 1440×900: gambar 800×900 + Right Content 640×900
- Wrapper 384: Page Header, Form (SHIELD Input, Input - Password, Button lg primary)

**State frame yang lazim:** Login - Empty; Login - Filled; Login - Empty Error; Login - Filled Error

### P11 · Overlay: Drawer kanan  (181 frame) — recipe `overlay-drawer`
**Kapan:** Filter, Tambah/Ubah, detail ringkas.

**Struktur:**
- Frame 1440×900 terpisah: SHIELD Drawer Right {Size=md 155× | lg 22× | 2xl 4×} + Scrim
- Header: SHIELD Drawer Header; slot isi: GUN Filter - SWT - <halaman>, GUN Add Trainee SWT, SHIELD Input-Summary (Read Only), Alert - Booking Conflict with Blackout, Listbox

**State frame yang lazim:** Drawer - Filter; Drawer - Filter - Selected; Add - Empty; Add - Empty Error; Add - Filled; Add - Filled Error; Edit

**Aturan:** Overlay tidak ditaruh di dalam frame halaman.

### P12 · Overlay: Modal  (176 frame) — recipe `overlay-modal`
**Kapan:** Konfirmasi dan modal form.

**Struktur:**
- Frame 1440×900 terpisah: SHIELD Modal Confirmation {Status Warning sm 49× | Danger sm 13× | Warning md 10× | Neutral sm 5× | Success sm 2×}
- atau SHIELD Modal {Size lg 47× | xs 18× | md 14× | full 6×, With Scroll Bar} + Modal Header + Scrim
- domain: GUN Modal Confirmation - Delete|Remove|Move to archive|Cancel Booking|Bulk|Discard; Modal - SWT - Import Nominal Roll; Booking - Select Courseware/Assignment Modal

**State frame yang lazim:** Confirmation; Confirmation - Delete; Confirmation - Delete - Blocked; Discard; Select Courseware; Import List - Separate - Filled

### P13 · Toast  (123 frame) — recipe `toast`
**Kapan:** Umpan balik setelah aksi.

**Struktur:**
- SHIELD Toast with Container {Variant=Page|Default, Line, With Button} 1440×128 sebagai anak root frame halaman (di atas Body)

**Aturan:** State frame diberi nama 'Toast - Success'/'Toast - Saved'.

### P14 · Anotasi (bukan layar)  (290 frame) — recipe `None`
**Kapan:** Sticker (269) dan Notes (21).

**Struktur:**
- SHIELD Sticker/Notes dari Design Annotations; lebar 1440+1540·n

**Aturan:** Abaikan saat meniru layar; jangan dihitung sebagai pola.

## 4. Konvensi frame (cara designer menamai dan memecah state)

- **Satu halaman Figma = satu modul**; di dalamnya satu frame per state. Nama state konsisten: `List - Empty`, `List - Filled`, `Search - Filled`, `Search - Empty Result`, `Drawer - Filter`, `Drawer - Filter - Selected`, `List - Filter Applied`, `Dropdown - <apa>`, `Toast - Success`, `Add - Empty/Empty Error/Filled/Filled Error`, `Edit`, `Confirmation - Delete`, `Discard`, `Tooltip`.
- Kata yang paling sering di nama frame: Empty 210, Filled 203, List 143, Toast 123, Details 118, Error 85, Add 78, Dropdown 75, Confirm 70, Filter 40, Edit 36.
- **Tinggi frame** = isi (900 dasar; 914/1000/1200+ bila konten panjang). Lebar tetap 1440 (login 1440, wizard 1440).
- **Frame 'Sticker'** (lebar 1440+1540·n = token `sticker size/Size n`) memuat anotasi/spec di sisi layar; **'Notes'** untuk catatan.
- **Nama halaman** memakai `↪` untuk anak modul, penanda ❌/🟡/🔴 dan `Synced VC/NC`, `RFS`, `WU`. Kode warna di `[INDEX]`: In Progress, In Review, Completed, Abandoned, Note/Info. Arti pasti 🟡/🔴/RFS/WU **belum dikonfirmasi**.
- **Alur baku modul baru:** Empty → Filled → Search (Filled/Empty Result) → Drawer Filter (open/selected/applied/empty) → Add/Edit (Empty/Error/Filled/Filled Error) → Toast → Confirmation.

## 5. Peta modul (Rail · Sidebar · isi)

| Modul (halaman) | Frame | Rail Active | Sidebar · Open Menu | Komponen isi utama |
|---|---|---|---|---|
| [NEW MARKSMANSHIP SCREEN]  | 8 | SWT | Sidebar-SWT | Bookings | Section Layout, Section Layout - Table, Box Tab Group |
| Login  | 5 | SWT | Sidebar-SWT | Default | Input, Input - Password, Data Display - Booking |
| Dashboard  | 24 | SWT | Sidebar-SWT | Default | Data Display - Booking, Data Display - Booking Team, Search Item-List |
| Notifications  | 11 | Default | Sidebar-SWT | Default | Notifications List, Section Layout - Table, Tab Group v2 |
| Today's Booking  | 17 | SWT | Sidebar-SWT | Bookings | Section Layout - Table, Advanced Tab Group, Table - Today's Booking - Bookings |
| Booking List  | 52 | SWT | Sidebar-SWT | Bookings | Table - Booking List, Section Layout - Table, Tab Group v2 |
| Step 1 - Create Booking | Token Synced VC Synced VC | 18 | — | — | Create Booking SWT - Step 1 - Trai, Create Booking SWT - Step 1 - Stat, Create Booking SWT - Step 1 - Cont |
| Step 2 - Schedule | Token Synced VC Synced VC | 19 | — | — | Courseware Vertical - Schedule, Section Layout - Table, Create Booking - Schedule Options |
| Step 3 - Lane Config | Synced NC Synced NC | 58 | — | — | Create Booking - Lane Config Item, Courseware Vertical - Lane, Section Layout - Table |
| Step 4 - Nominal Roll | Synced NC Synced NC | 69 | — | — | Section Layout - Table, Drawer Right, Tab Group v2 |
| Step 5 - Review Booking  | 9 | SWT | Sidebar-SWT | Bookings | Listbox Item/Single Item New, Create Booking - Review Booking - , Modal |
| Create Booking: Individual ❌ ❌ | 15 | SWT | Sidebar-SWT | Bookings | Create Booking - Schedule Options , Create Booking SWT - Step 1 - Trai, Create Booking SWT - Step 1 - Stat |
| Booking Details: Upcoming  | 66 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Section Layout, Alert |
| Booking Details: Upcoming (Asset Issued)  | 3 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Upcomi |
| Booking Details: Upcoming (The Day)  | 8 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Upcomi, Alert |
| Step 1 - Nominal Roll  | 44 | — | — | Section Layout - Table, Modal, Tab Group v2 |
| Step 2 - Config  | 12 | — | — | Create Booking - Lane Config Item, Box Tab Group, Modal Confirmation |
| Step 3 - Detail List  | 30 | — | — | Onboarding - Detail List - Edit, Section Layout, Box Tab Group |
| Step 4 - Review  | 9 | — | — | Onboarding - Review Booking - SWT, Modal, Section Layout |
| Booking Details: Ongoing  | 2 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Ongoin |
| Ongoing Session (Marksmanship) 🟡 🟡 | 80 | — | — | Section Layout, Section Layout - Table, Box Tab Group |
| Ongoing Session (Collective) 🔴 🔴 | 5 | — | — | Modal Confirmation, Result, Section Layout |
| Booking Details: Return Assets  | 8 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Return, Modal Confirmation |
| Booking Details: Completed  | 2 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Comple |
| Booking Details: Cancelled  | 1 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Cancel |
| Booking Details: Overdue  | 4 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details - Details - Cancel, Booking Details - Details - Return |
| Booking Details: Upcoming  | 41 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Modal, Booking Details Item - Details Mul |
| Booking Details: Ongoing  | 27 | SWT | Sidebar-SWT | Bookings | Tab Group v2, Booking Details Item - Details Mul, Booking Details - Courseware Selec |
| Booking Details: Completed  | 1 | SWT | Sidebar-SWT | Bookings | Booking Details Item - Details Mul, Booking Details - Courseware Selec, Tab Group v2 |
| Training Results List  | 9 | SWT | Sidebar-SWT | Default | Section Layout - Table, Table - Training Result List, Drawer Right |
| Training Result Details (Marksmanship, Judge  | 24 | SWT | Sidebar-SWT | Default | Tab Group v2, Section Layout - Table, Training Details - Booking Details |
| Training Result Details (Collective)  | 8 | SWT | Sidebar-SWT | Default | Tab Group v2, Training Result - Detail List Stat, Section Layout - Table |
| Training Result Details (Multiple CW)  | 4 | SWT | Sidebar-SWT | Default | Training Details - Courseware Sele, Training Details - Booking Details, Tab Group v2 |
| Resource Planning  | 11 | SWT | Sidebar-SWT | Default | Section Layout - Table, Table - Resource Planning - System, Section Layout |
| Operational Availability  | 14 | SWT | Sidebar-SWT | Default | Data Display - Training Result, Sy, Section Layout - Table, Table - Operational Availability N |
| All Reports ❌ ❌ | 2 | SWT | Sidebar-SWT | Reports | Section Layout - Table |
| Assets Audit Report ❌ ❌ | 4 | SWT | Sidebar-SWT | Reports | Section Layout - Table, Table - Report Assets Audit Report, Modal |
| Site Management List | Synced VC Synced VC | 15 | SWT | Sidebar-SWT | Default | Section Layout - Table, Table - Site Management, Drawer Right |
| Site Management Details - Available | Synced Synced VC | 60 | SWT | Sidebar-SWT | Default | Date Picker/date-item, Drawer Right, Tab Group v2 |
| Lane Details | Synced VC Synced VC | 5 | SWT | Sidebar-SWT | Default | Lane Details, Section Layout - Table, Tab Group v2 |
| Site Management Details - Offline  | 2 | SWT | Sidebar-SWT | Default | Base Station Details, Tab Group v2, Section Layout - Table |
| Data Export  | 4 | SWT | Sidebar-SWT | Data | Radio Group, Section Layout, Checkbox Group |
| Data Import  | 11 | SWT | Sidebar-SWT | Data | Modal, Modal - Import Booking, Section Layout - Table |
| SHM  | 3 | SWT | Sidebar-SWT | System Hardware | Data Display - Training Result, Sy, Notifications List, Chart - Asset |
| Asset List | RFS 🟡 🟡 RFS | 39 | SWT | Sidebar-SWT | System Hardware | Section Layout - Table, Tab Group v2, Listbox Item/Single Item New |
| Asset Details | RFS RFS | 17 | SWT | Sidebar-SWT | System Hardware | Table - System Hardware - Asset De, Asset Details, Tab Group v2 |
| Assignment List | RFS🟡 🟡 RFS | 18 | SWT | Sidebar-SWT | System Hardware | Section Layout - Table, Tab Group v2, Table - Assignment List New |
| Action - Issue Asset (Admin & Maintenance)  | 39 | SWT | Sidebar-SWT | System Hardware | Section Layout - Table, Table - Issue Asset (Maintenance) , Issue Asset Step 1 - Personnel |
| Action - Issue Asset (Booking)🟡 🟡 | 87 | SWT | Sidebar-SWT | Bookings | Section Layout - Table, Table - Issue Asset (Booking) - Sc, Table - Issue Asset (Booking) - Su |
| Assignment Details - Issued  | 20 | SWT | Sidebar-SWT | System Hardware | Assignment Details - Details, Section Layout - Table, Table - Assignment Details - Asset |
| Action - Top Up Asset🟡 🟡 | 18 | SWT | Sidebar-SWT | System Hardware | Section Layout - Table, Table - Issue Asset (Booking) - Sc, Table - Issue Asset (Booking) - Su |
| Assignment Details - Pending Return  | 4 | SWT | Sidebar-SWT | System Hardware | Assignment Details - Details, Section Layout - Table, Tab Group v2 |
| Assignment Details - Return Assets  | 7 | SWT | Sidebar-SWT | System Hardware | Assignment Details - Details, Section Layout - Table, Table - Assignment Details - Asset |
| Action - Return Assets🟡 🟡 | 52 | SWT | Sidebar-SWT | System Hardware | Section Layout - Table, Table - Return Asset (Booking) - S, Table - Return Asset (Maintenance) |
| Assignment Details - Returned  | 4 | SWT | Sidebar-SWT | System Hardware | Assignment Details - Details, Section Layout - Table, Table - Assignment Details - Asset |
| Assignment Details - Missing  | 4 | SWT | Sidebar-SWT | System Hardware | Assignment Details - Details, Section Layout - Table, Table - Assignment Details - Asset |
| RFID Reader Listing | RFS RFS | 24 | SWT | Sidebar-SWT | RFID Config | Section Layout - Table, Table - RFID - List, Drawer Right |
| Antenna Listing | RFS RFS | 22 | SWT | Sidebar-SWT | RFID Config | Listbox Item/Single Item New, Drawer Right, Section Layout - Table |
| System Health 🟡 🟡 | 14 | SWT | Sidebar-SWT | Default | System Health - Card, Section Layout, Alert - System Health |
| User List | RFS RFS | 36 | Users | Sidebar-User Mgmt | Default | Listbox Item/Single Item New, Section Layout - Table, Tab Group v2 |
| User Details | RFS RFS | 7 | Users | Sidebar-User Mgmt | Default | Key Value, Section Layout, Section Layout - Table |
| User Role | RFS RFS | 15 | Users | Sidebar-User Mgmt | Default | Drawer Right, Section Layout - Table, Table - User Mgmt - User Role |
| User Permission | RFS RFS | 4 | Users | Sidebar-User Mgmt | Default | Section Layout - Table, Table - User Mgmt - User Permissio |
| Rank | RFS RFS | 15 | Users | Sidebar-User Mgmt | Default | Section Layout - Table, Table - User Mgmt - Rank, Drawer Right |
| Asset Type | RFS RFS | 16 | Asset | Sidebar-Asset | Default | Listbox Item/Single Item New, Drawer Right, Section Layout - Table |
| Asset Category | RFS RFS | 16 | Asset | Sidebar-Asset | Default | Drawer Right, Section Layout - Table, Table - System Hardware - Asset Ca |
| Asset Tracking | WU WU | 42 | Asset | Sidebar-Asset | Default | Tab Group v2, Section Layout, SubSection in Section Layout |
| Briefing Room | Synced VC NC Synced VC | 17 | Briefing Rooms | — | Section Layout - Table, Table - Settings - Briefing Room, Drawer Right |
| Activity Log  | 19 | Activity Log | Sidebar-SWT | Default | Section Layout - Table, Table - Activity Log, Drawer Right |
| System Maintenance ❌ ❌ | 4 | System maintenance | — | System Maintenance - Data Item, Tab Group v2, Section Layout |
| General  | 3 | Settings | Sidebar-Settings New | Default | Section Layout, Input, Radio Group |
| Location  | 17 | Settings | Sidebar-Settings New | Default | Section Layout - Table, Table - Settings - Location, Drawer Right |
| Notification  | 4 | Settings | Sidebar-Settings New | Default | Radio Group, Section Layout, Tab Group v2 |
| System Version  | 12 | Settings | Sidebar-Settings New | Default | Section Layout - Table, Table - Settings - System Version, Drawer Right |
| IP Whitelisting [Staging Only]  | 3 | Settings | Sidebar-Settings New | Default | Section Layout - Table, Table - Settings - IP Whitelisting, Alert |
| Cover  | 1 | — | — | Thumbnail Cover |
| [Backlog] TRMS CV  | 98 | — | — | Navbar, chevron-down, Navigation |

## 6. Cara agent memakai ini

1. `python3 patterns/module.py <modul>` → Rail/Sidebar/Header, state frame yang diharapkan, contoh frame.
2. `python3 registry/plan.py <recipe> --program SWT --module <modul>` → rencana build (key + property tervalidasi).
3. Buat **set state lengkap** (alur baku di §4), bukan hanya satu layar.
4. Overlay (drawer/modal/toast) = frame terpisah; ikuti ukuran dan state di pola P11–P13.
5. Verifikasi dengan screenshot + `lintFrame`; bandingkan dengan frame contoh (link di `modules.json`).

## 7. Temuan tentang design file ini (untuk audit layer 4)

| Temuan | Detail |
|---|---|
| GUN kurang dimanfaatkan sebagai pemilik domain | hanya 3,7% instance; tabel, badge, dan wizard domain tersedia di GUN |
| Salinan basi komponen GUN | `Badge - Asset Status`, `Issued Asset List`, `Attendance`, `Ongoing Session Detail List Status` terdeteksi sebagai instance dari library lain |
| UI kit lain masih ada | halaman backlog `[Backlog] TRMS CV`, serta ±1% instance di halaman lain (`Tables/Table cell`, `Button/Button`, `Navbar`) |
| Penamaan | nama halaman berpenanda emoji tidak seragam; arti belum terdokumentasi |
| Tidak ada token/style lokal | file mengonsumsi Graphene (0 collection lokal) — sesuai arsitektur |
