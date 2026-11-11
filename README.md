# xxsx Minecraft Mod Development Toolkit

A public, reusable toolkit for multi-version Minecraft mod development, asset validation, Blockbench model review, and release checks. License: `AGPL-3.0-only`.

## Toolkit Layout

- `tools/mcver.py` and `tools/mcver_target.py`: multi-version project audits, supported-version matrices, split-package checks, target scaffolding, and game-instance `doctor` checks.
- `skills/minecraft-modeling-item/scripts/audit_model.py` and `tools/render_block_models_preview.py`: structural 3D model review, UV aspect-ratio squash checks, single-texture reuse detection, and orthographic isometric previews with UV/texture reuse overlays.
- `tools/validate_pixel_assets.py`: pixel-icon gate for 16x16 base materials and 32x32 complex artifacts — size, RGBA, binary alpha, transparent corners/margins, opaque color ramp depth, and SHA-256 uniqueness.
- `tools/earth_release_gate.py`: pre-release static checks for knowledge-node icons, 3D block models, UV distortion, reused textures, flat palettes / no-alpha silhouettes, duplicate names (`[LANG-DUP-NAME]`), 3D block items rendered as flat 2D, redundant/orphan block PNGs, continuous-process properties, and spam-prone content.
- `tools/bb_mcp_client.py`: direct HTTP client for Blockbench MCP without opening dialogs.
- `skills/`: localized development, publishing, modeling, and creature workflow skills. Machine caches and credentials are excluded.
- `playbook/MC-DEV-PLAYBOOK.md`: generalized development playbook; replace `<INSTANCE_ROOT>` with paths appropriate to your installation.

Python tools may have optional dependencies. Check each script's `--help` and imports before running it in a fresh environment. The modeling skill self-test is `python skills/minecraft-modeling-item/scripts/selftest.py`.

### Portable path handling

All shipped tools read the workspace root from the current working directory by default and accept an explicit `--root <workspace>` override. They do not embed machine-specific drive letters or user directories, so the same scripts work in any checkout.

```bash
# run from a workspace root that contains earth-series/
python tools/earth_release_gate.py
python tools/render_block_models_preview.py --out workflow-reports/preview.png

# or point at a workspace elsewhere
python tools/earth_release_gate.py --root <workspace>
python tools/render_block_models_preview.py --root <workspace>

# pixel icons: 16x16 simple materials, 32x32 complex artifacts
python tools/validate_pixel_assets.py <mod>/textures/item/*.png --size 16
python tools/validate_pixel_assets.py <mod>/textures/item/<artifact>.png --size 32
```

## Modeling and Asset Rules

- Do not assign full-face `[0, 0, 16, 16]` UVs to a thin edge; use UV dimensions that match the face to avoid stretching.
- Do not map one texture across every part of a multi-part model. Give distinct parts appropriate texture regions or images.
- Simple materials stay 16x16 RGBA; complex artifacts (ritual swords, compasses, 3/4 books, talismans, bags) use 32x32 RGBA with a cold-shadow to warm-highlight ramp, a dark cohesive outline, and transparent corners.
- Do not stack concentric shrinking white cubes into a cone tower. Build real plinths, columns, wide tabletops, and hanging cloth instead.
- A functional block that already has a 3D model must use that block model as its item model; do not add a redundant 2D item PNG or leave orphan block textures behind.
- Multiblock cores (altars, array cores) are formed in place by placing the base and surrounding fixtures, then right-clicking with a focus item; do not ship a single-block crafting recipe for the assembled core.
- Do not start `runClient` unless the project owner explicitly requests a runtime launch.
- For generated animated images (including `gpt-image-2.6` output), split frames from the source on disk into individual PNGs and define animation timing in `.png.mcmeta`. Do not fake animation by embedding a contact sheet as a single frame.

## Architecture References

- `skills/zershyan-mcmod-style/references/single-block-nbt-ber.md`: single-block core + NBT assembly + oversized `BlockEntityRenderer`. Covers crafting/hand-absorption into `DataComponents`, server-side O(1) ticking, client multi-part rendering for water-wheel rows and array rings, render-bounds inflation against frustum culling, place/sync/drop data closure, and near/far core highlight outlines.
- `skills/zershyan-mcmod-style/references/index.md`: routing table for all reference topics (registration, networking, config, attachments, datagen, build, rendering, and the single-block BER pattern).

## Multi-channel item tinting (discipline + tier)

Literature, talismans, and artifacts that need both a discipline color and a T0–T4 tier must use layered tint sources rather than repainting the whole icon:

| Layer | Texture | Role | Tint |
|---|---|---|---|
| layer0 | `<item>.png` | paper / base material, original color | `minecraft:constant` = -1 |
| layer1 | `<item>_cover.png` | leather cover body, neutral grayscale | `<mod>:discipline` |
| layer2 | `<item>_tier_trim.png` | corner guards, clasps, scroll caps, wax-seal ring | `<mod>:tier` |

The trim mask must stay near-neutral gray and cover only local accents; otherwise the tier color multiplies into muddy tones. Items without tiers keep two layers and skip the empty trim layer. See playbook §11.2 for the full JSON/Java skeleton.

## Worldgen and settlement rules

- `*_halo` alteration rock may replace natural bare rock only. Never include `BlockTags.SUBSTRATE_OVERWORLD` (grass, dirt, podzol, rooted dirt, moss), farmland, village ground, or dirt paths in its replacement targets.
- Early-game prospecting on grass, riverbanks, and foothills uses low loose 3D pebbles placed above the ground, in low density, avoiding village structures.
- Duplicate display names across different registration IDs are blocked by `[LANG-DUP-NAME]`.
- New adult villagers default to `minecraft:none`. When adopting a settlement, deterministically guide roughly 75%–80% of unemployed adults into a matching `VillagerProfession` and mod trades, keyed by settlement ID plus entity UUID.

## Upstream Credits & References

- Mod architecture conventions: [Zershyan/zershyan-mcmod-style](https://github.com/Zershyan/zershyan-mcmod-style). This toolkit adapts the skill for multi-version subdirectories such as `neoforge-26.1.2` and `neoforge-26.2`, Java 25, and gradual package-name migration in existing projects.
- Mod publishing and conventions: [Zershyan/mcmod-publish-with-narrafork](https://github.com/Zershyan/mcmod-publish-with-narrafork). The localized `preflight.py` workflow adds multi-module project support and automatic fallback parsing of `neoforge.mods.toml`.
- Minecraft item and block modeling: [Srar-Git/minecraft-modeling-item](https://github.com/Srar-Git/minecraft-modeling-item). The included audit adds `uv_aspect_squash` (UV aspect-ratio distortion) and `multi_part_single_texture` (blocking one texture reused across multiple model parts).
- Blockbench MCP plugin: [jasonjgardner/blockbench-mcp-plugin](https://github.com/jasonjgardner/blockbench-mcp-plugin). Plugin URL: <https://jasonjgardner.github.io/blockbench-mcp-plugin/mcp.js>; local endpoint: <http://localhost:3000/bb-mcp>.

The toolkit includes localized/adapted copies and utilities. Consult each skill's `LICENSE` and upstream project terms when redistributing components independently. No API keys, tokens, cookies, browser profiles, or other credentials belong in this repository.

