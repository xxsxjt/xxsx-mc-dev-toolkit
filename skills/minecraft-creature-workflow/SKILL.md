---
name: minecraft-creature-workflow
description: Build, review, and validate Minecraft creature assets and entity workflows for NPCs, mobs, elite mobs, and bosses. Routes Blockbench projects to Java, Bedrock, or GeckoLib outputs, tracks asset licenses and provenance, and verifies deliverables without treating unknown third-party files as reusable.
metadata:
  short-description: Build and validate Minecraft creature assets
---

# Minecraft Creature Workflow

Use this skill for a concrete Minecraft creature task: model design, Blockbench project work, textures, bones, animations, Java entity rendering, Bedrock resource-pack output, GeckoLib integration, asset cataloging, or delivery validation.

Do not use it for generic Minecraft gameplay questions, server administration, or importing an unknown mod archive. Keep those tasks outside this workflow.

## Operating rules

- Establish the target edition, Minecraft version, loader or Bedrock pack version, and creature class before editing files. Creature classes are `npc`, `mob`, `elite`, and `boss`; they describe gameplay intent, not a license or renderer.
- Treat the Blockbench `.bbmodel` as an editable source project, not as a universal runtime format. Select a target-specific project format and export only what that target consumes.
- Keep model geometry, textures, skeleton/bone names, animations, sounds, particles, Java code, and Bedrock JSON in separate inventory entries. They can have different authors and licenses.
- Prefer original or user-provided assets. For third-party assets, require an original source URL, revision or release marker, license evidence, and a rights decision for commercial use, modification, and redistribution. A public download, repository license, or marketplace label is not enough.
- If license evidence is missing, mark the asset `unverified` and do not include it in a reusable delivery or redistribute it. Do not invent authors, licenses, mod entries, or compatibility.
- Keep source files and exports together with a manifest, SHA-256 hashes, attribution/NOTICE material, and a validation report. Never execute code from a model archive or copy secrets into a report.
- Ask for explicit confirmation immediately before downloading, transforming, redistributing, publishing, or overwriting third-party material. Read-only discovery and validation can proceed without that mutation.

## Route the work

1. Read `references/input-output.md` for required inputs, outputs, and creature-class scope.
2. Read `references/format-routing.md` for the selected Blockbench, Java, Bedrock, or GeckoLib path.
3. Read `references/licensing-provenance.md` before using any non-original asset.
4. Use `references/asset-manifest.template.json` for every deliverable package. Use `scripts/validate_creature_package.py` to produce a report.
5. Report five separate states: discovered, license-verified, downloaded, converted, and runtime-validated. Do not collapse them into “done”.

## Modeling workflow

- Start from a short creature brief: silhouette, scale, pose, hitbox assumptions, materials, animation list, and whether the creature needs variants, armor, emissive regions, or attachable equipment.
- Build a stable root bone and a readable hierarchy. Bone names are an integration contract: record them before writing animation code and keep exported names stable.
- Establish UV layout and texture dimensions before detailing. Check transparent pixels, atlas boundaries, animation frame naming, and texture path casing.
- Author locomotion first, then idle, look-at, attack, hurt, death, spawn, and special/boss phases as needed. Define loop, length, transition, blend, and trigger conditions for each animation.
- Preview the model in the target format and test at in-game scale. A successful export is not proof that the renderer, resource path, animation controller, or server-side class is correct.

## Engine boundaries

- Java Edition vanilla-style models generally require Java model classes or generated layer definitions plus a client-only renderer registration appropriate to the exact loader/version. Keep rendering code on the physical client and validate Dedicated Server loading separately.
- Bedrock uses resource-pack geometry, textures, animations, animation controllers, render controllers, and client entity definitions. Geometry and animation identifiers must match the JSON references; use Molang queries and controller states for conditional behavior.
- GeckoLib uses `.geo.json`, `.animation.json`, textures, a `GeoModel`, and controller code. The model, texture, and animation resource paths are code-level contracts. Controllers can conflict when multiple controllers animate the same bone, so define ownership and priority explicitly.
- Fabric, Forge, NeoForge, and Quilt are separate compatibility targets. Do not infer a renderer API or Java version from the mod name; lock each target from its project build files and version-matched documentation.
- A generic OBJ, glTF, or FBX file is a conversion source only. It is not a direct Java, Bedrock, or GeckoLib entity asset until the geometry, UVs, hierarchy, animation semantics, and resource paths have been converted and validated.

## Delivery gate

A package is ready only when it has:

- a target and version record;
- an editable source or an explicit reason it is unavailable;
- target exports and a file inventory;
- per-file source, license, attribution, and SHA-256 records;
- a validation report with failures and limitations;
- a preview or runtime check appropriate to the selected target.

If no reusable third-party model was found, deliver the empty catalog plus official documentation references. That is a valid result and is safer than filling the catalog with unverified downloads.
