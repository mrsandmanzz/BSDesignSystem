# BS Design System — agent package

Lookup data and tools that let Claude build Figma screens from the correct Graphene / SHIELD / GUN components, in a few calls, without scanning the component libraries.

**Layers:** Graphene (L1: color, typography) → SHIELD (L2: main components) → GUN (L3: business components) → design files (L4).

## What is in this repository

| Path | Purpose |
|---|---|
| `skill/` | The Claude skill `graphene-figma-builder` and its installer |
| `registry/` | Component and token lookup (`find.py`, `plan.py`, `build.py`), recipes, variant keys, the screen executor (`executor.js`), `preflight.py`, `VERSION.json` |
| `patterns/` | Screen patterns learned from the SWT 3.0 design file, with a per-module helper |
| `docs/` | Agent playbook, screen recipes, runbook, screen patterns |
| `CLAUDE.md` | Rules loaded automatically by Claude Code |

Audit reports, the PDF report and the knowledge graph are kept privately.

## Install the skill

```bash
git clone https://github.com/mrsandmanzz/BSDesignSystem.git
cd BSDesignSystem
bash skill/install.sh
```

Then start a new Claude session and ask for a screen, for example "buatkan layar daftar Bookings untuk SWT". On first use the skill explains what it will do and needs before it touches Figma.

Requirements: Figma Desktop with the Desktop Bridge plugin running in the target file, the figma-console MCP installed in Claude, Graphene/SHIELD/GUN libraries enabled in the file, and edit access.

## Status

Verified on a real design file: the wizard (Create Booking) and the list page with a table, each built in 2–3 seconds, with 0 detached instances. Other recipes are validated against the registry but not yet built through the executor. See `CHANGELOG.md` and `registry/README.md` for what is proven and what is not.

## Keeping the registry current

`registry/VERSION.json` records the date and the entry counts; `registry/preflight.py` warns when the registry is old or incomplete. When the libraries change, the registry must be refreshed by the maintainer, because renamed properties or variants make the plan look valid when it is not.
