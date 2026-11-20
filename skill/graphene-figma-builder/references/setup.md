# Setup, first run and failure handling

Read this file in full on the first run, and whenever a check fails. Contents: A first-run message, B Figma checks in order, C worst and negative cases, D cleaning up after a failure, E how to stop.

## A. First-run message (show before any tool call)

Show this to the designer in the language they use (translate it, keep the meaning). Adjust nothing else. Then ask exactly one question and wait for the answer.

> **Sebelum mulai — apa yang akan saya lakukan**
>
> Saya akan membuat layar di Figma dari komponen Graphene/SHIELD/GUN yang sudah ada, memakai daftar komponen (registry) di folder design system, jadi saya tidak perlu memindai seluruh library.
>
> **Yang saya butuhkan dari kamu**
> 1. Figma **Desktop** terbuka dengan file target, dan plugin **Figma Desktop Bridge** berjalan di file itu (Plugins → Development → Figma Desktop Bridge).
> 2. MCP **figma-console** sudah terpasang di Claude.
> 3. Library **Graphene, SHIELD, GUN** aktif di file target (Assets → Libraries).
> 4. Idealnya satu halaman di file itu yang sudah berisi layar serupa. Dari situ saya mengambil komponen tanpa impor, yang jauh lebih stabil.
> 5. Kamu punya hak **edit** di file itu.
>
> **Yang akan saya ubah**
> - Hanya membuat frame baru di halaman sandbox (default: `claude test`) atau halaman yang kamu sebut. Saya tidak mengedit, memindah atau menghapus layar yang sudah ada, dan tidak menyentuh file Figma lain yang kebetulan terbuka.
>
> **Yang perlu kamu tahu**
> - Plugin Figma kadang berhenti merespons. Kalau itu terjadi saya berhenti dan memberi tahu; kamu perlu membuka plugin lagi, dan mungkin ada frame setengah jadi di halaman sandbox (saya akan menawarkan membersihkannya).
> - Waktu eksekusi 2–3 detik per layar sudah diukur pada dua pola (wizard dan daftar+tabel). Pola lain belum diuji. Waktu total termasuk persiapan belum diukur.
> - Kalau komponen atau token yang kamu butuhkan tidak ada, saya melaporkannya sebagai GAP; saya tidak mengarang.
> - Daftar komponen bisa tertinggal dari library. Kalau saya menemukan perbedaan, saya berhenti dan melapor, bukan menebak.
>
> **Satu pertanyaan:** lanjut? Kalau ya, sebutkan **file Figma target** dan **program** (SWT / CMT / CTT), dan kalau ada, **halaman yang sudah berisi layar serupa**.

After the designer says yes: write the marker, then continue with step 1 of SKILL.md.
Marker: `printf 'skill_version=1\ndate=%s\n' "$(date +%F)" > "<folder of SKILL.md>/.onboarded"`. If the write fails (read-only skill folder), carry on and show a two-line reminder of A once per conversation instead.
Show A again when the marker is missing or its `skill_version` is lower than this skill's version.
If the designer says no or asks questions, answer them and do not touch Figma.

## B. Figma checks, in order (stop at the first failure)

| # | Check | How | If it fails | Say to the designer |
|---|---|---|---|---|
| 1 | The Figma MCP tools exist | Look for `figma_*` tools; if they are deferred, load them with ToolSearch ("figma-console"). | None found | "Claude belum punya akses ke Figma. Pasang MCP figma-console (repo Southleft `figma-console-mcp`, ikuti README resminya) lalu mulai sesi baru. Saya tidak bisa melanjutkan tanpa itu." Do not try other routes (browser, REST). |
| 2 | Some file is connected | `figma_list_open_files` | Error or empty list | "Belum ada file Figma yang tersambung. Buka file target di Figma Desktop, lalu Plugins → Development → Figma Desktop Bridge, tunggu statusnya terhubung, kabari saya." Browser Figma cannot run the plugin; say so if they use it. |
| 3 | The target file is connected | Match the designer's file name or key in the list | Not listed, others are | List the connected file names, say "file target belum tersambung; plugin harus dibuka di file itu sendiri". Do **not** use another file "because it is the only one". |
| 4 | Several files, same or similar name | Compare file keys | Ambiguous | Ask which one (name + the key shown in its URL). Never guess. |
| 5 | The plugin answers | `figma_execute` with `return {ok:true}`, 15 s timeout, `fileKey` set | Error or timeout | "Plugin tidak merespons. Tutup lalu buka lagi Figma Desktop Bridge di file target." Retry once after they confirm; no loops. |
| 6 | Target is a Graphene project file, not a library | Read the file name; read the page list (names only) | Looks like a library (SHIELD/GUN/Graphene) or another brand | "File ini tampak seperti library, bukan file desain. Saya tidak menulis ke library." Stop. |
| 7 | Libraries enabled | Time-boxed (10 s) `figma.teamLibrary.getAvailableLibraryVariableCollectionsAsync()` and check names; **untested in this project**, so a failure of the call means "unknown", not "disabled" | Graphene collections absent | "Library Graphene/SHIELD/GUN belum aktif di file ini. Aktifkan di Assets → Libraries, lalu kabari saya." If the check itself fails or hangs, say it could not be verified and rely on check 8. |
| 8 | Example source exists | Page named by the designer: read only its top-level frame names (no deep scan) | Page missing or empty | Ask for a page with similar screens. If there is none, offer the import fallback and state it is less reliable. |
| 9 | Edit access | The first write is the test: create the sandbox frame | Error mentioning permission or read-only | "File ini hanya bisa dilihat; saya perlu hak edit." Stop. |
| 10 | Sandbox page | Find or create it (name from the designer, default `claude test`) | Creating fails | Report; do not fall back to a production page. |

## C. Worst and negative cases

| Case | Detected by | Safe behaviour | Never |
|---|---|---|---|
| Folder missing or moved (Drive not synced, path changed) | `DATA_PATH` points nowhere; `registry/plan.py` absent | Say the folder was not found; ask for the new path; offer to rewrite `DATA_PATH` | Search the disk broadly; build without the registry |
| Drive placeholder files (online-only) or partial sync | preflight: `empty`, `counts`, `json` | Stop; tell them to make the folder available offline and wait for the sync to finish | Use half-synced data |
| Conflict copies (two editors) | preflight: `conflict` | Warn; name the files; ignore them; tell the maintainer | Pick one silently |
| `python3` missing | `python3 --version` fails | Say what is missing and how to get it; stop | Hand-write the plan from memory |
| Registry stale | preflight: `age`, or drift check in step 4 of SKILL.md | Warn (age) or stop (drift) and name the component and property that differ | Rename values on your own |
| Skill older than the registry needs | preflight: `skill` | Tell them to rerun `bash skill/install.sh` and start a new session | Continue with old rules |
| Designer refuses a permission prompt (bash, Figma tool) | Tool call denied | Explain in one sentence what the call does and why; do not retry the same call; if they still decline, stop | Work around the refusal by another tool |
| Plugin dies mid-build | `figma_execute` error, bridge gone | Stop. Report how many steps ran. Ask to reopen the plugin. Offer to remove the half-built frame (section D) | Retry in a loop; raise timeouts |
| Import times out | Executor `komponen tak bisa diambil` / `timeout` | Ask for a page that already uses the component (example source); do not raise the timeout | Run longer imports (one killed the plugin) |
| Library not enabled or component not accessible | Import fails for every component, or check 7 | Ask to enable the library | Draw look-alike shapes |
| Needed component or token does not exist | `find.py` returns nothing | Report a GAP: what is needed, what was searched, the closest alternatives | Invent a name, value or hex |
| Unknown programme or module | The designer did not say | Ask: SWT, CMT or CTT, and the module | Default silently |
| Production page named as the target | Page name looks like production, or the designer says so | Build in the sandbox page anyway and say so; moving it is their decision. Only write to a production page if they ask in so many words | Overwrite existing frames |
| Several designers work in the same file | Frames appear that this session did not create | Touch only frames this session created; use a unique frame name (add the date and time) | Rename or delete others' frames |
| Very large file | Page list is long | Never scan all pages; only the named example page | `loadAllPagesAsync`, `findAll(() => true)` |
| Figma Desktop closed or on another account | Bridge not listed after opening | Ask them to check they are in the right Figma account and the file is open in the desktop app | Retry silently |
| Registry says a recipe is not tested (dashboard, detail, calendar, overlays) | `references` in the DS folder, `registry/README.md` | Say it is untested, build in the sandbox, verify more carefully | Claim it is proven |

## D. Cleaning up after a failure

- Only frames this session created, on the sandbox page, can be offered for removal. Say which frames (name and size), and delete only after a clear yes.
- Nothing outside the sandbox page is removed.
- After the cleanup, report what is left.

## E. How to stop (use this shape every time)

1. **What happened** (one sentence, plain words).
2. **Why it matters** (what cannot be done now).
3. **What you need to do** (numbered, specific, as few steps as possible).
4. **What I did not change** (state it; designers worry about this most).

Do not blame the designer, do not hide the error text, and do not claim anything is fixed unless you checked.
