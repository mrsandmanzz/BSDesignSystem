# CLAUDE.md — Graphene design system, agent package

You are working with the Graphene design system (layers: **Graphene → SHIELD → GUN → Design file**; Graphene = color & typography, SHIELD = main components, GUN = business components). This repository holds the lookup data and the tools an agent needs to build Figma screens with the right components. Audit reports, the PDF report and the knowledge graph are kept privately and are not here.

## Fast path
Do not scan the Figma libraries. Use `registry/`: `python3 registry/plan.py --list`, `plan.py <recipe> --program <SWT|CMT|CTT>`, `find.py <word>`, `find_token.py <word>`. Follow `docs/06-agent-runbook.md` and `docs/05-screen-recipes.md`. Never run `findAll(()=>true)` or `loadAllPagesAsync` on library files (they kill the plugin) and never `importVariableByKeyAsync` (it hangs).

## Screen patterns
Read `docs/08-screen-patterns.md`, run `python3 patterns/module.py <module>` and `registry/plan.py <recipe> --program SWT --module <module>`. Frame = GUN Page Layout Template; Header slot = SHIELD Header Nav {Breadcrumb=1}; overlays (drawer, modal, toast) are separate frames; build the full state set (Empty, Filled, Search, Filter, Add/Edit, Toast, Confirm).

## Build with the skill
`bash skill/install.sh` installs the skill `graphene-figma-builder`. It explains itself to the designer on first use, runs `registry/preflight.py`, plans from the registry and builds with `registry/executor.js`. See `skill/graphene-figma-builder/SKILL.md` and `references/setup.md`.

## Non-negotiables
- Bind to `+Theme` tokens only; never raw hex/px, never `.Brand`/`Color` directly.
- Never invent tokens or components; report a GAP (what is needed, what was searched, closest alternatives).
- Never rename or delete published variables.
- Before any Figma write, verify the active file (`figma_list_open_files`, `figma_get_status`) and pass the target `fileKey`.
- Figma live data outranks this repository. If they differ, stop, report the difference, and let the maintainer refresh the registry.
- Prefer GUN (L3) for domain screens and the component of the right programme (SWT/CMT/CTT). Avoid legacy SHIELD rows (collections `System`, `3-Spacing`, `Size`, `Spacings`) unless the task needs them.
- Do not guess the Design-file layer; ask for the file URL and a page with similar screens.

## When you learn something new
Update the relevant doc, `registry/VERSION.json` (`python3 registry/stamp.py`) and add a `CHANGELOG.md` line.
