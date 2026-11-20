# Agent Playbook — rules for Claude working with Graphene

Read `README.md` first, then `docs/02-tokens.md (privat, tidak ada di repo ini)`. This file says **how to act**.

## 1. Hard rules (never break)

1. **Bind to `+Theme` only.** Colors, radii, sizes, page spacing come from `+Theme`. Never bind to `.Brand` or `Color` directly, and never write raw hex/px.
2. **No new tokens, components or styles without an explicit request.** Missing something → report a gap (§6).
3. **Do not detach base/remote component instances.** Change variants/properties instead.
4. **Light and Dark must both work.** Use tokens, which carry both modes. Check the file/frame is not forcing a mode override unless asked.
5. **`content (…)`, `system type/*`, `last updated/*` are sample data, not styling tokens.** Never bind fills/strokes/sizes to them.
6. **Do not rename or delete published variables.** Renames are breaking. Use the deprecation flow (§5).
7. **Verify the target file before any write.** Call `figma_get_status` / `figma_list_open_files`; several files are connected at once. Pin with `figma_navigate … lock:true` for long edits.
8. **Source of components = SHIELD.** SHIELD instances resolve to Foundation's Rose theme. Foundation's own docs frames use a stale Indigo template library: never copy colors from them. When color matters, read the instance's *bound variable* and resolve from its own collection. Do not use components flagged ⚠ legacy or `domain` in `docs/03-components.md (privat, tidak ada di repo ini)` for generic UI.
9. **Domain work → GUN.** For SWT/CMT/CTT screens use GUN components first (then SHIELD, then Foundation). GUN instances nest SHIELD components and Foundation icons; do not detach. Programme variants are separate sets (e.g. Filter - SWT/CMT/CTT): choose the matching one.
10. **Trust the live variables over the Figma doc pages.** The Color doc page still says "Indigo"; real primary is Rose.

## 2. Naming convention (target; current file is mixed)

Use for **new** tokens and when proposing renames:

- lowercase, kebab-case, `/` for hierarchy, no spaces, no emoji, no Title Case.
- `{property}/{role}/{variant?}/{state?}` — e.g. `color/background/danger/soft`, not `color/background/danger/invert/soft`.
- Decimal in numeric scales with `-` is allowed only in primitives (`space-0-5`).
- Do not name tokens after color (`orange`) when they alias a brand role (`brand-2`). Name by role/intent.
- Mode names: `light`/`dark`, otherwise `default`.

## 3. Picking the right token (decision tables)

### Text color
| You are styling… | Use |
|---|---|
| Body/paragraph on normal surface | `color/text/default` (or `text/body` for secondary) |
| Secondary / helper text | `color/text/caption` |
| Placeholder | `color/text/placeholder` |
| Disabled | `color/text/disabled` |
| Link / visited | `color/text/link` / `color/text/visited` |
| Text on a **solid** brand/status fill (button, filled badge) | `color/text/base` (exception: warning solid in Light = 1.92:1 → use dark text; audit F-23) |
| Text on a **soft/tinted** status fill | `color/text/{danger|success|warning|info|primary}` — **never** `text/invert/*` (it equals the tint colour: contrast 1.00:1, audit F-62) |
| Status text on neutral surface | `color/text/{status}` |
| Always black / always white regardless of mode | `color/text/true black` / `true white` |

### Background color
| You are styling… | Use |
|---|---|
| Page canvas | `color/background/main background` |
| Card/panel | `color/background/surface lv1` → nested `surface lv2` |
| Modal | `color/background/modal` (tinted header: `modal colored`) |
| Subtle neutral fill | `color/background/default/soft` |
| Primary action (solid) | `color/background/primary/{default,hovered,pressed,focused,loading}` |
| Status solid | `color/background/{info,success,warning,danger}/{state}` |
| Status soft (alert, tag) | `color/background/{status}/invert/soft` or `…/invert/default` |
| Divider line | `color/background/divider` |
| Disabled | `color/background/disabled` |

### State mapping (interaction)
`default → hovered → pressed`; `focused` = same as default fill + focus ring (stroke); `loading` = pressed color. Disabled uses `…/disabled` tokens on bg, text and border (no state suffix).

### Radius
Buttons `border/radius-button/{size}`; form fields `border/radius-form/{size}`; cards/sections `border/radius/section` (12) or `…/default` (8); modals `border/radius/modal` (16); pills/avatars `border/radius/full`.

### Size & spacing
Control height: `sizing/component {5xs…lg}` (16–44). Modals/drawers/dropdowns: `sizing/modal|drawer|dropdown *`. Page rhythm: `page spacing/page|section|sub-section 1|sub-section 2` (padding/gap/radius) — `lv2` variants for nested/denser layouts. TV layouts: `tv page spacing/*`.

### Typography
Choose `{weight}/text-{size}` text style. Body default = `Regular/text-sm` (14/20) or `Regular/text-base` (16/24). Headings are not defined as roles; use `Semi Bold|Bold/text-xl…3xl` and say so in the handoff. Uppercase labels: `Caps Header/*`.

## 4. Workflows (figma-console MCP)

**Before any task**
1. `figma_get_status` (probe) → confirm file name.
2. `figma_search_components` at start of each session; nodeIds go stale between sessions.

**Build/modify**
1. Search for an existing component/variant first.
2. Instantiate with `figma_instantiate_component`; change via `figma_set_instance_properties` (direct text edits on instances fail silently).
3. Bind fills/strokes to variables (find by name in `+Theme`); batch with `figma_batch_*` tools.
4. Screenshot (`figma_take_screenshot`), check alignment/spacing/auto-layout (hug vs fill), fix, re-screenshot (max 3 iterations).
5. Place new work inside a Section/Frame, never loose on canvas.

**Audit a design file**
1. List unbound fills/strokes, hard-coded radii/gaps, detached instances.
2. Report per frame: token that should replace it, using the tables above.
3. Do not auto-fix without confirmation unless asked.

## 5. Change management (rename / move / delete)

`add new → alias old to new → migrate consumers → mark old "deprecated" in description → remove after one release`. Never in-place rename a published variable. Record every change in `CHANGELOG.md`.

## 6. Reporting a gap

When no token/component fits, stop and output:

```
GAP
  need:      <what you tried to express>
  searched:  <tokens/components checked>
  closest:   <nearest existing option and why it fails>
  proposal:  <suggested token/component, layer (base|business), name per §2>
```

Do not substitute a raw value.

## 7. Open questions the agent must not guess

- Business-layer file(s), UI component library file(s), and which design files consume them (audit F-02). Ask.
- Whether the 319 `content (…)` strings are still in use by any design file (audit F-01). Ask before moving/deleting.
- Intended split between `Spacing` and `Sizing` (audit F-08).
