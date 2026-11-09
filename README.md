# xxsx Minecraft Mod Development Toolkit

A public, reusable toolkit for multi-version Minecraft mod development, asset validation, Blockbench model review, and release checks. License: `AGPL-3.0-only`.

## Toolkit Layout

- `tools/mcver.py` and `tools/mcver_target.py`: multi-version project audits, supported-version matrices, split-package checks, target scaffolding, and game-instance `doctor` checks.
- `skills/minecraft-modeling-item/scripts/audit_model.py` and `tools/render_block_models_preview.py`: structural 3D model review, UV aspect-ratio squash checks, single-texture reuse detection, and orthographic isometric previews with UV/texture reuse overlays.
- `tools/validate_pixel_assets.py`: hard transparency and palette checks for 16x16 RGBA pixel icons.
- `tools/earth_release_gate.py`: pre-release static checks for knowledge-node icons, 3D block models, UV distortion, reused textures, continuous-process properties, spam-prone content, and duplicate textures.
- `tools/bb_mcp_client.py`: direct HTTP client for Blockbench MCP without opening dialogs.
- `skills/`: localized development, publishing, modeling, and creature workflow skills. Machine caches and credentials are excluded.
- `playbook/MC-DEV-PLAYBOOK.md`: generalized development playbook; replace `<INSTANCE_ROOT>` with paths appropriate to your installation.

Python tools may have optional dependencies. Check each script's `--help` and imports before running it in a fresh environment. The modeling skill self-test is `python skills/minecraft-modeling-item/scripts/selftest.py`.

## Modeling and Asset Rules

- Do not assign full-face `[0, 0, 16, 16]` UVs to a thin edge; use UV dimensions that match the face to avoid stretching.
- Do not map one texture across every part of a multi-part model. Give distinct parts appropriate texture regions or images.
- Do not start `runClient` unless the project owner explicitly requests a runtime launch.
- For generated animated images (including `gpt-image-2.6` output), split frames from the source on disk into individual PNGs and define animation timing in `.png.mcmeta`. Do not fake animation by embedding a contact sheet as a single frame.

## Upstream Credits & References

- Mod architecture conventions: [Zershyan/zershyan-mcmod-style](https://github.com/Zershyan/zershyan-mcmod-style). This toolkit adapts the skill for multi-version subdirectories such as `neoforge-26.1.2` and `neoforge-26.2`, Java 25, and gradual package-name migration in existing projects.
- Mod publishing and conventions: [Zershyan/mcmod-publish-with-narrafork](https://github.com/Zershyan/mcmod-publish-with-narrafork). The localized `preflight.py` workflow adds multi-module project support and automatic fallback parsing of `neoforge.mods.toml`.
- Minecraft item and block modeling: [Srar-Git/minecraft-modeling-item](https://github.com/Srar-Git/minecraft-modeling-item). The included audit adds `uv_aspect_squash` (UV aspect-ratio distortion) and `multi_part_single_texture` (blocking one texture reused across multiple model parts).
- Blockbench MCP plugin: [jasonjgardner/blockbench-mcp-plugin](https://github.com/jasonjgardner/blockbench-mcp-plugin). Plugin URL: <https://jasonjgardner.github.io/blockbench-mcp-plugin/mcp.js>; local endpoint: <http://localhost:3000/bb-mcp>.

The toolkit includes localized/adapted copies and utilities. Consult each skill's `LICENSE` and upstream project terms when redistributing components independently. No API keys, tokens, cookies, browser profiles, or other credentials belong in this repository.
