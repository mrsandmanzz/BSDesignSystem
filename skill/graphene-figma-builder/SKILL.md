---
name: graphene-figma-builder
description: Build or modify Figma screens with the Graphene design system (Graphene tokens → SHIELD main components → GUN business components; programmes SWT, CMT, CTT) using a prebuilt registry instead of scanning the libraries. Use this whenever the user asks to create, draft, duplicate or restyle a screen, page, flow, wizard, list, detail, dashboard, modal, drawer or toast in Figma for a Graphene/SHIELD/GUN/SWT/CMT/CTT project, asks which component or token to use, or mentions "design system", "buat layar", "bikin screen", "pakai component", "Dark mode" in a Figma file — even if they never name the design system. On the first call it explains to the designer what it will do and needs before touching anything. Do not use for unrelated Figma work (illustration, other brands' systems).
---

# Graphene Figma builder

Skill version: 1

Build screens from the right components in a few calls. A registry (lookup tables) plus a small executor replaces library scanning, which is slow and has crashed the Figma plugin, and replaces guessing component names, which gives screens that look right but use the wrong variant.

Two things matter most, and the rest of this file serves them:
1. The designer is told what will happen before anything happens (first run), and told plainly when something blocks the work.
2. When a check fails, stop and say what to do. A half-working build that looks right is worse than no build.

Details, message templates and the full list of failure cases are in `references/setup.md` (in the folder of this SKILL.md). Read it on the first run and whenever a check fails.

## 1. First run: inform before acting

Look for the file `.onboarded` in the folder of this SKILL.md. If it is missing, or its `skill_version` is lower than 1, this is a first run:

- Read section A of `references/setup.md` and show that message to the designer in their language. Make **no** Figma or file-writing tool call before they answer. Reading `.onboarded` and `references/setup.md` is fine.
- Ask the one question it ends with (continue? which Figma file, which programme, which page has similar screens).
- If they say yes, write the marker as section A describes, then continue. If they say no or have questions, answer and stop.

Why: designers are handing a tool write access to their Figma file. They decide with full information, once, up front.

## 2. Find the data folder

Resolve `$DS` (the folder with `registry/plan.py`) in this order: the file `DATA_PATH` next to this SKILL.md (one line, an absolute path); the environment variable `GRAPHENE_DS_PATH`; ask the designer for the folder. If the folder is missing or moved, follow section C of the setup file and offer to rewrite `DATA_PATH`.

Never open or print the large JSON files (`shield.json`, `gun.json`, `icons.json`, `variants.json`). Query them with the scripts, which return only matches; reading them whole wastes context.

## 3. Preflight (always, every session)

```bash
cd "$DS" && python3 registry/preflight.py --skill-version 1
```

- Exit code 2 (`FAIL`): stop. Tell the designer using the shape in section E of the setup file: what happened, why, what to do, what you did not change. Use the check's `msg` and `fix` text.
- `WARN`: say it in one sentence and continue (for example, a registry older than 45 days: drift checking becomes more important).
- `OK`: continue silently, but mention the registry date once.

Then run the Figma checks in section B of the setup file, in order, and stop at the first failure. The target file must be connected and named by the designer; do not use a file because it is the only one connected. Pass the target `fileKey` to every `figma_execute` call. Other connected files belong to other projects: never run anything there.

## 4. Plan from the registry

```bash
python3 registry/plan.py --list
python3 patterns/module.py <module>
python3 registry/plan.py <recipe> --program <SWT|CMT|CTT> --module <module>
python3 registry/find.py <word> [--lib GUN|SHIELD] --full
python3 registry/find_token.py <word>
```

Ask for the programme and module if the designer did not say; do not default. Prefer GUN over SHIELD for domain screens, and the programme's own component. If nothing fits, report a GAP (what is needed, what you searched, closest alternatives); never invent a component, token or value. Colours bind to `+Theme` tokens only. Screen sets follow `$DS/docs/08-screen-patterns.md`; overlays are separate frames. If a recipe is listed as untested in `$DS/registry/README.md`, say so and verify more carefully.

## 5. Choose the component source

Prefer a page that already uses the components: the executor makes instances from components already in the file, with no library import. Use `--example page:<page name>` or a frame ID. Imports by key have hung or killed the plugin for some components, so they are a fallback and you must say it is less reliable. Never raise an import timeout.

## 6. Drift check, then build

For the components in the plan, compare the property names and values the plan expects against the file (read the property definitions through `figma_execute`, only for these components). A difference means the registry is stale: stop, name the component and the property, and tell the designer to inform the maintainer. Do not rename values yourself.

```bash
python3 registry/build.py <recipe> --program <P> --module <m> --name "<frame name> <date time>" \
  --example page:<Name> [--extra steps.json] [--dark] > build.js
```

Paste `build.js` into `figma_execute` with the target `fileKey`. The result is `{done, next, total, failed, error, log}`. If `done` is false, read `error`, fix the cause, do not retry blindly. Build in the sandbox page (default `claude test`) or the page the designer names; moving the result is their decision. Use a unique frame name so nobody's work is overwritten.

Extra steps (`--extra`, a JSON list): `inst` into a slot, `text`, `swapVariant`, `stretch`, `fit`, `theme`. See `$DS/registry/README.md` and the top of `$DS/registry/executor.js`.

## 7. Verify and report

- Screenshot the new frame (`figma_capture_screenshot`, scale 0.5, target file active).
- `verify` should show 0 detached and 0 non-library instances.
- Check visible defects: tables wider than the body, sidebar not full height, content overflowing the frame.
- Report: what was built (components, programme), where it is, GAPs, build time, and what you did not verify.

## Rules that protect the file and the plugin

- Never `findAll(() => true)`, `loadAllPagesAsync` or `importVariableByKeyAsync` on library files.
- Keep each `figma_execute` under about 40 seconds.
- Do not modify, rename or delete published variables or components, or anyone's existing frames.
- If the plugin disconnects, stop, tell the designer to reopen it, and offer to clean up half-built frames (section D). No retry loops.
- When Figma and the registry disagree, Figma wins; report the difference.
