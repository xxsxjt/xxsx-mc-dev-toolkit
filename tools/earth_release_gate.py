#!/usr/bin/env python3
"""Earth Series Pre-Deployment Release Gate & Anti-Regression Validator.

Enforces the user's non-negotiable quality rules across the active Earth-series
repositories before any JAR is deployed to the game instance:

1. Knowledge Tree & Icon Gate:
   - Every active discipline JSON in earth_lore must use a non-vanilla icon.
   - Every knowledge_node JSON across active mods must have an explicit "icon"
     field pointing to a non-vanilla item (<modid>:<item>), with no dangling
     prerequisites.
2. 3D Block Model Gate:
   - Apparatus, furniture, ritual, and workstation block models in
     xuanhuan_earth, fantasy_earth, and earth_theology must use multi-element
     3D geometry ("elements") and must not fall back to bare cube/cube_all.
3. Anti-Fake-Duration & Process-Quality Gate:
   - Consumable pills/medicines must not use 3-10s placeholder durations;
     grainfast/fasting pills must wire to persistent fasting state;
     single-slot pills, medicines, and forged implements must wire to
     continuous process components.
4. Chat-Spam Gate:
   - Block right-click handlers must not spam multiple fixed lines to chat via
     sendSystemMessage; dynamic status belongs on the actionbar (sendOverlayMessage).
5. Texture Dedup & Dimension Gate:
   - Item/block PNG textures in active mods must be valid PNGs and must not
     have rampant byte-identical duplicates within the same mod.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from PIL import Image

def _default_root() -> Path:
    """Prefer the current directory when it holds earth-series/, else this repo's parent."""
    cwd = Path.cwd()
    if (cwd / "earth-series").is_dir():
        return cwd
    return Path(__file__).resolve().parents[1]


# Portable defaults: run from the workspace root that contains `earth-series/`,
# or pass `--root <workspace>` explicitly. No machine-specific absolute paths.
ROOT = _default_root()
EARTH = ROOT / "earth-series"

# mod id -> relative target directory inside `earth-series/`.
MOD_TARGETS = {
    "earth_lore": "earth_lore/neoforge-26.1.2",
    "earth_on_minecraft": "earth_on_minecraft/neoforge-26.2",
    "xuanhuan_earth": "xuanhuan_earth/neoforge-26.2",
    "fantasy_earth": "fantasy_earth/neoforge-26.2",
    "earth_theology": "earth_theology/neoforge-26.1.2",
}

ACTIVE_MODS = {mod_id: EARTH / rel for mod_id, rel in MOD_TARGETS.items()}


def set_root(root: Path) -> None:
    """Rebind the workspace root and every derived mod path."""
    global ROOT, EARTH, ACTIVE_MODS
    ROOT = root.resolve()
    EARTH = ROOT / "earth-series"
    ACTIVE_MODS = {mod_id: EARTH / rel for mod_id, rel in MOD_TARGETS.items()}

APPARATUS_BLOCKS = {
    "xuanhuan_earth": [
        "alchemy_furnace",
        "talisman_table",
        "spirit_array_core",
        "array_pillar",
        "spirit_vein_node",
        "spirit_spring_stone",
    ],
    "fantasy_earth": [
        "aether_battery",
        "aether_crystal_cluster",
        "alchemy_table",
        "arcane_focus_mat",
        "offering_bowl",
        "rune_carving_table",
        "rune_stone",
        "ritual_pedestal",
        "ritual_candle",
        "ritual_circle_marker",
    ],
    "earth_theology": [
        "pew",
        "offering_tray",
        "censer",
        "scripture_lectern",
        "prayer_candle",
        "temple_keystone",
    ],
}


def check_knowledge_nodes(errors: list[str], warnings: list[str]) -> int:
    all_nodes: dict[str, tuple[str, Path, dict]] = {}
    for mod_id, mod_dir in ACTIVE_MODS.items():
        res = mod_dir / "src" / "main" / "resources" / "data"
        if not res.exists():
            continue
        for p in res.rglob("earth_lore/knowledge_node/**/*.json"):
            rel = p.relative_to(res)
            parts = rel.parts
            # data/<namespace>/earth_lore/knowledge_node/<disc>/<slug>.json
            ns = parts[0]
            sub = "/".join(parts[3:]).replace(".json", "")
            node_id = f"{ns}:{sub}"
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"[KNOWLEDGE] Invalid JSON {p}: {exc}")
                continue
            all_nodes[node_id] = (mod_id, p, data)

    for node_id, (mod_id, p, data) in sorted(all_nodes.items()):
        icon = data.get("icon", "")
        if not icon or not isinstance(icon, str):
            errors.append(f"[ICON-MISSING] {node_id} ({p.name}) has no 'icon' field")
        elif icon.startswith("minecraft:"):
            errors.append(f"[ICON-VANILLA] {node_id} ({p.name}) uses vanilla icon '{icon}'")
        for pre in data.get("prerequisites", []):
            if pre not in all_nodes:
                errors.append(f"[DANGLING-PREREQ] {node_id} references missing prerequisite '{pre}'")

    # Check active discipline icons in earth_lore
    active_disciplines = {"geo", "eng", "che", "med", "mat", "agr", "xua", "mag", "the"}
    disc_dir = ACTIVE_MODS["earth_lore"] / "src" / "main" / "resources" / "data" / "earth_lore" / "earth_lore" / "discipline"
    if disc_dir.exists():
        for p in disc_dir.glob("*.json"):
            if p.stem not in active_disciplines:
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            icon = data.get("icon", "")
            if not icon or icon.startswith("minecraft:"):
                errors.append(f"[DISCIPLINE-ICON] Discipline {p.name} uses vanilla or empty icon '{icon}'")

    # Check every knowledge_node icon resolves to an existing item model/texture in its mod
    for node_id, (mod_id, p, data) in sorted(all_nodes.items()):
        icon = data.get("icon", "")
        if ":" in icon and not icon.startswith("minecraft:"):
            icon_ns, icon_slug = icon.split(":", 1)
            if icon_ns in ACTIVE_MODS:
                target_assets = ACTIVE_MODS[icon_ns] / "src" / "main" / "resources" / "assets" / icon_ns
                item_def = target_assets / "items" / f"{icon_slug}.json"
                item_model = target_assets / "models" / "item" / f"{icon_slug}.json"
                if not item_def.exists() and not item_model.exists():
                    errors.append(f"[ICON-BROKEN] {node_id} icon '{icon}' has no item definition or model in {icon_ns}")

    return len(all_nodes)


def check_model_textures_and_items(errors: list[str]) -> None:
    for mod_id, mod_dir in ACTIVE_MODS.items():
        assets = mod_dir / "src" / "main" / "resources" / "assets" / mod_id
        if not assets.exists():
            continue
        tex_dir = assets / "textures"
        model_block_dir = assets / "models" / "block"
        model_item_dir = assets / "models" / "item"
        items_dir = assets / "items"

        # Check all block models for particle, unresolved #var, cross-atlas item textures, and missing PNGs
        if model_block_dir.exists():
            for p in sorted(model_block_dir.glob("*.json")):
                data = json.loads(p.read_text(encoding="utf-8"))
                textures = data.get("textures", {})
                elements = data.get("elements", [])
                if elements and "particle" not in textures:
                    errors.append(f"[MODEL-PARTICLE] {mod_id}:block/{p.stem} has elements but no 'particle' texture")
                for k, v in textures.items():
                    if not isinstance(v, str):
                        continue
                    if v.startswith("#"):
                        ref_key = v[1:]
                        if ref_key not in textures:
                            errors.append(f"[MODEL-UNRESOLVED-VAR] {mod_id}:block/{p.stem} texture '{k}' -> '{v}' not defined in textures")
                    elif ":item/" in v or v.startswith("item/"):
                        errors.append(f"[MODEL-CROSS-ATLAS] {mod_id}:block/{p.stem} references item texture '{v}' in block model (rejected by SimpleModelWrapper)")
                    elif v.startswith(f"{mod_id}:"):
                        rel_tex = v.split(":", 1)[1]
                        if not (tex_dir / f"{rel_tex}.png").exists():
                            errors.append(f"[MODEL-TEX-MISSING] {mod_id}:block/{p.stem} references missing texture '{v}'")
                for el in elements:
                    for face_name, face in el.get("faces", {}).items():
                        ftex = face.get("texture", "")
                        if ftex.startswith("#"):
                            ref_key = ftex[1:]
                            if ref_key not in textures:
                                errors.append(f"[MODEL-FACE-UNRESOLVED] {mod_id}:block/{p.stem} face '{face_name}' -> '{ftex}' not in textures")

        # Check all item models for missing PNGs
        if model_item_dir.exists():
            for p in sorted(model_item_dir.glob("*.json")):
                data = json.loads(p.read_text(encoding="utf-8"))
                textures = data.get("textures", {})
                for k, v in textures.items():
                    if isinstance(v, str) and v.startswith(f"{mod_id}:"):
                        rel_tex = v.split(":", 1)[1]
                        if not (tex_dir / f"{rel_tex}.png").exists():
                            errors.append(f"[ITEM-TEX-MISSING] {mod_id}:item/{p.stem} references missing texture '{v}'")

        # Check every registered item in Java has assets/<mod_id>/items/<slug>.json
        java_dir = mod_dir / "src" / "main" / "java"
        if java_dir.exists():
            for jf in java_dir.rglob("*.java"):
                src = jf.read_text(encoding="utf-8")
                for m in re.finditer(r'(?:ITEMS\.register(?:SimpleItem|Item)?|DeferredItem<[^>]+>\s+[A-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+)\(\s*"([a-z0-9_]+)"\s*[,)]', src):
                    slug = m.group(1)
                    if not (items_dir / f"{slug}.json").exists():
                        errors.append(f"[ITEM-DEF-MISSING] {mod_id}:{slug} registered in {jf.name} has no assets/{mod_id}/items/{slug}.json")


def check_loot_tables_and_settlements(errors: list[str]) -> None:
    for mod_id, mod_dir in ACTIVE_MODS.items():
        java_dir = mod_dir / "src" / "main" / "java"
        data_dir = mod_dir / "src" / "main" / "resources" / "data" / mod_id
        lang_dir = mod_dir / "src" / "main" / "resources" / "assets" / mod_id / "lang"
        if not java_dir.exists():
            continue
        for jf in java_dir.rglob("*.java"):
            src = jf.read_text(encoding="utf-8")
            # Check LOOT_TABLE references
            for m in re.finditer(r'Registries\.LOOT_TABLE\s*,\s*(?:Identifier\.fromNamespaceAndPath\(\s*[A-Za-z0-9_.]+\s*,\s*"([^"]+)"\s*\)|[A-Za-z0-9_.]+\.id\(\s*"([^"]+)"\s*\))', src):
                lt_path = m.group(1) or m.group(2)
                lt_file = data_dir / "loot_table" / f"{lt_path}.json"
                if not lt_file.exists():
                    errors.append(f"[LOOT-TABLE-MISSING] {mod_id} {jf.name} references loot table '{mod_id}:{lt_path}' but {lt_file.relative_to(mod_dir)} does not exist")
            # Check settlement dirty blocks
            if "SettlementFeature" in jf.name:
                for bad_blk in ("Blocks.MYCELIUM", "Blocks.PODZOL", "Blocks.RED_MUSHROOM_BLOCK", "Blocks.PACKED_MUD", "Blocks.GRAVEL"):
                    if bad_blk in src:
                        errors.append(f"[SETTLEMENT-DIRTY-BLOCK] {mod_id} {jf.name} still places ruin/mushroom/mud block {bad_blk}")

        if lang_dir.exists():
            for lf in lang_dir.glob("*.json"):
                raw = lf.read_text(encoding="utf-8")
                if "区块安全加载后初始化" in raw or "奥术聚落锚点" in raw or "宗门聚落锚点" in raw:
                    errors.append(f"[ANCHOR-LANG] {mod_id} {lf.name} still contains legacy anchor text ('锚点' / '区块安全加载后初始化')")

    # Check MagicSettlementAnchorBlockEntity does not teleport player in openSettlementPanel
    magic_be = ACTIVE_MODS["fantasy_earth"] / "src" / "main" / "java" / "com" / "xxsx" / "fantasyearth" / "settlement" / "MagicSettlementAnchorBlockEntity.java"
    if magic_be.exists():
        src = magic_be.read_text(encoding="utf-8")
        if "player.teleportTo(" in src and "openMenu" not in src:
            errors.append("[MAGIC-BOARD-GUI] fantasy_earth MagicSettlementAnchorBlockEntity.openSettlementPanel teleports player instead of opening board GUI")

    # Check XuanhuanSettlementAnchorBlock & MagicSettlementAnchorBlock only create BlockEntity on LOWER half
    for mod_id, rel_cls in [
        ("xuanhuan_earth", "com/xxsx/xuanhuanearth/settlement/XuanhuanSettlementAnchorBlock.java"),
        ("fantasy_earth", "com/xxsx/fantasyearth/settlement/MagicSettlementAnchorBlock.java"),
    ]:
        cls_f = ACTIVE_MODS[mod_id] / "src" / "main" / "java" / rel_cls
        if cls_f.exists():
            src = cls_f.read_text(encoding="utf-8")
            idx = src.find("newBlockEntity(")
            if idx != -1 and "DoubleBlockHalf.LOWER" not in src[idx:idx + 320] and "DoubleBlockHalf.UPPER" not in src[idx:idx + 320]:
                errors.append(f"[BOARD-UPPER-BE] {mod_id} {cls_f.name}.newBlockEntity creates BlockEntity on UPPER half (causes chunk load error)")

    # Check ProcessingMachineScreen does not have GUI manual crank button
    proc_screen = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "java" / "com" / "xxsx" / "earthonminecraft" / "client" / "ProcessingMachineScreen.java"
    if proc_screen.exists():
        src = proc_screen.read_text(encoding="utf-8")
        if "manualButton" in src:
            errors.append("[GUI-CRANK-BUTTON] earth_on_minecraft ProcessingMachineScreen still renders a GUI manual crank button instead of world hand_crank block")

    # Check EarthMedicalAndWeaponSupport tooltip format crash
    med_support = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "java" / "com" / "xxsx" / "earthonminecraft" / "EarthMedicalAndWeaponSupport.java"
    if med_support.exists():
        src = med_support.read_text(encoding="utf-8")
        if "duration %.1fs" in src or "持续 %.1f秒" in src:
            errors.append("[TOOLTIP-FORMAT-CRASH] earth_on_minecraft EarthMedicalAndWeaponSupport uses %.1f for int regenSeconds() (throws IllegalFormatConversionException)")

    # Check VoxelShape (getShape) on 3D machine/apparatus blocks
    for mod_id, rel_cls in [
        ("earth_on_minecraft", "com/xxsx/earthonminecraft/ProcessingMachineBlock.java"),
        ("xuanhuan_earth", "com/xxsx/xuanhuanearth/XuanhuanMachineBlock.java"),
        ("xuanhuan_earth", "com/xxsx/xuanhuanearth/XuanhuanBlock.java"),
        ("fantasy_earth", "com/xxsx/fantasyearth/MagicMachineBlock.java"),
        ("earth_theology", "com/xxsx/earththeology/TheologyBlocks.java"),
    ]:
        cls_f = ACTIVE_MODS[mod_id] / "src" / "main" / "java" / rel_cls
        if cls_f.exists():
            src = cls_f.read_text(encoding="utf-8")
            if "getShape(" not in src:
                errors.append(f"[VOXEL-SHAPE-MISSING] {mod_id} {cls_f.name} does not override getShape() (3D block has full 16x16x16 hitbox)")


def check_3d_block_models(errors: list[str]) -> int:
    checked = 0
    # Check all block models across all active mods for parent+elements override bug
    for mod_id, mod_dir in ACTIVE_MODS.items():
        model_dir = mod_dir / "src" / "main" / "resources" / "assets" / mod_id / "models" / "block"
        if not model_dir.exists():
            continue
        for p in model_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"[MODEL-JSON] {mod_id}:{p.name} invalid JSON: {exc}")
                continue
            parent = data.get("parent", "")
            elements = data.get("elements", [])
            if elements and parent not in ("", "minecraft:block/block", "block/block", "minecraft:block/thin_block", "block/thin_block"):
                errors.append(
                    f"[MODEL-PARENT-OVERRIDE] {mod_id}:{p.name} defines both parent='{parent}' and 'elements' (child elements overwrite parent geometry in Minecraft!)"
                )

    for mod_id, blocks in APPARATUS_BLOCKS.items():
        model_dir = ACTIVE_MODS[mod_id] / "src" / "main" / "resources" / "assets" / mod_id / "models" / "block"
        for b in blocks:
            p = model_dir / f"{b}.json"
            if not p.exists():
                errors.append(f"[MODEL-MISSING] {mod_id}: block model {b}.json not found")
                continue
            checked += 1
            data = json.loads(p.read_text(encoding="utf-8"))
            parent = data.get("parent", "")
            elements = data.get("elements", [])
            if parent in ("minecraft:block/cube_all", "minecraft:block/cube", "block/cube_all", "block/cube") and not elements:
                errors.append(f"[MODEL-CUBE] {mod_id}:{b} is still a flat cube ({parent}) without 3D elements")
            elif not elements and not parent.startswith(f"{mod_id}:block/"):
                errors.append(f"[MODEL-EMPTY] {mod_id}:{b} has no 3D elements")
            elif len(elements) == 1 and elements[0].get("from") == [0, 0, 0] and elements[0].get("to") == [16, 16, 16]:
                errors.append(f"[MODEL-SIMPLE] {mod_id}:{b} is still a 16x16x16 full cube element")
    return checked


def check_3d_model_uv_and_textures(warnings: list[str]) -> None:
    """Detect UV aspect-ratio squashing ([0,0,16,16] on thin elements) and single-texture reuse across multi-part 3D models."""
    for mod_id in ("earth_lore", "earth_theology", "xuanhuan_earth", "fantasy_earth"):
        model_dir = ACTIVE_MODS[mod_id] / "src" / "main" / "resources" / "assets" / mod_id / "models" / "block"
        if not model_dir.exists():
            continue
        for p in sorted(model_dir.glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            elements = data.get("elements", [])
            if len(elements) < 3:
                continue
            textures = data.get("textures", {})
            unique_pngs = {v for k, v in textures.items() if k != "particle" and not str(v).startswith("#")}
            if len(elements) >= 4 and len(unique_pngs) <= 1:
                warnings.append(f"[MODEL-SINGLE-TEX] {mod_id}:block/{p.stem} has {len(elements)} 3D elements but only 1 texture {list(unique_pngs)}")
            squashed = 0
            for el in elements:
                fr = el.get("from", [0, 0, 0])
                to = el.get("to", [16, 16, 16])
                dx, dy, dz = abs(to[0] - fr[0]), abs(to[1] - fr[1]), abs(to[2] - fr[2])
                for face_name, face in el.get("faces", {}).items():
                    uv = face.get("uv")
                    if not uv or len(uv) != 4:
                        continue
                    uw, uh = abs(uv[2] - uv[0]), abs(uv[3] - uv[1])
                    if face_name in ("north", "south") and ((dx <= 4 and uw >= 12) or (dy <= 4 and uh >= 12)):
                        squashed += 1
                    elif face_name in ("east", "west") and ((dz <= 4 and uw >= 12) or (dy <= 4 and uh >= 12)):
                        squashed += 1
                    elif face_name in ("up", "down") and ((dx <= 4 and uw >= 12) or (dz <= 4 and uh >= 12)):
                        squashed += 1
            if squashed:
                warnings.append(f"[MODEL-UV-SQUASH] {mod_id}:block/{p.stem} has {squashed} faces mapping full 16px UV onto <=4px thin geometry")


def check_occlusion_and_worldgen_interactions(errors: list[str]) -> None:
    # 1. Every helper or registration for 3D non-full-cube blocks must include .noOcclusion()
    eom_main = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "java" / "com" / "xxsx" / "earthonminecraft" / "EarthOnMinecraft.java"
    if eom_main.exists():
        src = eom_main.read_text(encoding="utf-8")
        for b in (
            "IRONWORKING_ANVIL =",
            "private static DeferredBlock<SettlementBoardBlock> settlementBoardBlock",
            "private static DeferredBlock<EnergyGeneratorBlock> energyGeneratorBlock",
            "private static DeferredBlock<PowerCableBlock> powerCableBlock",
            "private static DeferredBlock<ControlPanelBlock> controlPanelBlock",
            "private static DeferredBlock<ConveyorBeltBlock> conveyorBeltBlock",
        ):
            idx = src.find(b)
            if idx != -1 and ".noOcclusion()" not in src[idx:idx + 520]:
                errors.append(f"[BLOCK-NO-OCCLUSION] earth_on_minecraft {b} is missing .noOcclusion()")

    for mod_id, main_rel, required_tokens in [
        (
            "xuanhuan_earth",
            "com/xxsx/xuanhuanearth/XuanhuanEarth.java",
            ["SPIRIT_VEIN_NODE =", "SPIRIT_SPRING_STONE =", "ARRAY_PILLAR =", "ALCHEMY_FURNACE =", "TALISMAN_TABLE =", "SPIRIT_ARRAY_CORE ="],
        ),
        (
            "fantasy_earth",
            "com/xxsx/fantasyearth/FantasyEarth.java",
            [
                "private static DeferredBlock<MagicMachineBlock> machineBlock",
                "private static DeferredBlock<ArcaneFocusMatBlock> focusMatBlock",
                "AETHER_BATTERY =",
                "RUNE_STONE =",
                "SETTLEMENT_ANCHOR =",
            ],
        ),
    ]:
        java_file = ACTIVE_MODS[mod_id] / "src" / "main" / "java" / main_rel
        if java_file.exists():
            src = java_file.read_text(encoding="utf-8")
            for tok in required_tokens:
                idx = src.find(tok)
                if idx != -1 and ".noOcclusion()" not in src[idx:idx + 620]:
                    errors.append(f"[BLOCK-NO-OCCLUSION] {mod_id} {tok} is missing .noOcclusion()")

    # 2. Villager idle effect & unemployed villager trade bug
    lore_events = ACTIVE_MODS["earth_lore"] / "src" / "main" / "java" / "com" / "xxsx" / "earthlore" / "LoreEvents.java"
    if lore_events.exists():
        src = lore_events.read_text(encoding="utf-8")
        idx = src.find("EntityInteract.class")
        end_marker = "        });\n        bus.addListener(TradeWithVillagerEvent.class"
        end_idx = src.find(end_marker, idx) if idx != -1 else -1
        if idx != -1 and "playVillagerTeachingFeedback" in src[idx:(end_idx if end_idx != -1 else idx + 650)]:
            errors.append("[VILLAGER-IDLE-EFFECT] earth_lore LoreEvents.onEntityInteract triggers playVillagerTeachingFeedback on normal right-click")

    res_mgr = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "java" / "com" / "xxsx" / "earthonminecraft" / "living" / "ResidentProfileManager.java"
    if res_mgr.exists():
        src = res_mgr.read_text(encoding="utf-8")
        if "VillagerProfession.NONE" not in src:
            errors.append("[VILLAGER-NONE-TRADES] ResidentProfileManager.java does not guard against adding trades to VillagerProfession.NONE unemployed villagers")

    # 3. Lootr barrel compatibility in settlement/sanctuary features
    for mod_id, feat_rel in [
        ("xuanhuan_earth", "com/xxsx/xuanhuanearth/settlement/XuanhuanSettlementFeature.java"),
        ("fantasy_earth", "com/xxsx/fantasyearth/settlement/MagicSettlementFeature.java"),
        ("earth_theology", "com/xxsx/earththeology/TheologySanctuaryFeature.java"),
    ]:
        feat_file = ACTIVE_MODS[mod_id] / "src" / "main" / "java" / feat_rel
        if feat_file.exists():
            src = feat_file.read_text(encoding="utf-8")
            if "Blocks.BARREL" in src and ("setLootTable" not in src or "barrel.setItem(" in src):
                errors.append(f"[LOOTR-BARREL] {mod_id} {feat_file.name} places Blocks.BARREL without setting a LootTable (breaks Lootr barrel conversion)")

    # 4. 2-block-tall settlement board / notice monument check
    for mod_id, cls_rel in [
        ("earth_on_minecraft", "com/xxsx/earthonminecraft/SettlementBoardBlock.java"),
        ("xuanhuan_earth", "com/xxsx/xuanhuanearth/settlement/XuanhuanSettlementAnchorBlock.java"),
        ("fantasy_earth", "com/xxsx/fantasyearth/settlement/MagicSettlementAnchorBlock.java"),
    ]:
        cls_file = ACTIVE_MODS[mod_id] / "src" / "main" / "java" / cls_rel
        if cls_file.exists():
            src = cls_file.read_text(encoding="utf-8")
            if "DOUBLE_BLOCK_HALF" not in src and "DoubleBlockHalf" not in src:
                errors.append(f"[BOARD-2BLOCK] {mod_id} {cls_file.name} is not a 2-block-tall (DoubleBlockHalf) settlement notice board")

    # 5. Curios integration check
    for mod_id in ("earth_theology", "xuanhuan_earth", "fantasy_earth"):
        curios_dir = ACTIVE_MODS[mod_id] / "src" / "main" / "resources" / "data" / "curios" / "tags" / "item"
        if not curios_dir.exists() or not list(curios_dir.glob("*.json")):
            errors.append(f"[CURIOS-TAGS] {mod_id} is missing data/curios/tags/item/*.json curio slot tags")

    # 6. PewBlock sitting check in earth_theology
    theology_blocks = ACTIVE_MODS["earth_theology"] / "src" / "main" / "java" / "com" / "xxsx" / "earththeology" / "TheologyBlocks.java"
    if theology_blocks.exists():
        src = theology_blocks.read_text(encoding="utf-8")
        idx = src.find("class PewBlock")
        if idx != -1 and "useItemOn" not in src[idx:]:
            errors.append("[PEW-SEAT] earth_theology PewBlock does not override useItemOn (holding any item prevents sitting)")

    # 7. Iron ore cave exposure & aether crystal density check
    for ore_cfg in ("poor_magnetite_lens.json", "magnetite_lens.json", "chalcopyrite_vein.json", "bituminous_coal_seam.json"):
        p = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "resources" / "data" / "earth_on_minecraft" / "worldgen" / "configured_feature" / ore_cfg
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            dc = data.get("config", {}).get("discard_chance_on_air_exposure", 0.0)
            if dc > 0.35:
                errors.append(f"[ORE-VISIBILITY] earth_on_minecraft {ore_cfg} has high discard_chance_on_air_exposure={dc} (hides ores in caves)")

    crystal_pf = ACTIVE_MODS["fantasy_earth"] / "src" / "main" / "resources" / "data" / "fantasy_earth" / "worldgen" / "placed_feature" / "aether_crystal_cluster.json"
    if crystal_pf.exists():
        raw = crystal_pf.read_text(encoding="utf-8")
        if '"count": 6' in raw and "rarity_filter" not in raw:
            errors.append("[CRYSTAL-DENSITY] fantasy_earth aether_crystal_cluster.json still spawns count=6 per chunk without rarity_filter")


def check_pills_and_jei(errors: list[str]) -> None:
    # 1. Check JEI slot y-coordinate in earth_on_minecraft
    jei_file = ACTIVE_MODS["earth_on_minecraft"] / "src" / "main" / "java" / "com" / "xxsx" / "earthonminecraft" / "integration" / "jei" / "ProcessingJeiCategory.java"
    if jei_file.exists():
        src = jei_file.read_text(encoding="utf-8")
        if "int y = 12;" in src:
            errors.append("[JEI-OVERLAP] ProcessingJeiCategory.java still places output/catalyst slots at y = 12 overlapping process text at y = 16")

    # 2. Check xuanhuan_earth pill durations & PillComponent process fields
    pill_comp = ACTIVE_MODS["xuanhuan_earth"] / "src" / "main" / "java" / "com" / "xxsx" / "xuanhuanearth" / "PillComponent.java"
    if pill_comp.exists():
        src = pill_comp.read_text(encoding="utf-8")
        for field in ("herbPotency", "fireHarmony", "erysipelasToxicity", "potencyMultiplier"):
            if field not in src:
                errors.append(f"[PILL-PROCESS] PillComponent.java is missing continuous alchemy field '{field}'")

    pills_file = ACTIVE_MODS["xuanhuan_earth"] / "src" / "main" / "java" / "com" / "xxsx" / "xuanhuanearth" / "XuanhuanPills.java"
    if pills_file.exists():
        src = pills_file.read_text(encoding="utf-8")
        if "MobEffects.SATURATION, 10," in src or "MobEffects.REGENERATION, 5," in src:
            errors.append("[PILL-FAKE-DURATION] XuanhuanPills.java still contains 5-10s placeholder durations")


def check_chat_spam_and_lang_keys(errors: list[str]) -> None:
    """Forbid sendSystemMessage in gameplay classes and enforce complete zh_cn/en_us lang keys and clean UTF-8."""
    for mod_id, mod_dir in ACTIVE_MODS.items():
        java_dir = mod_dir / "src" / "main" / "java"
        lang_dir = mod_dir / "src" / "main" / "resources" / "assets" / mod_id / "lang"
        if not java_dir.exists():
            continue
        zh = json.loads((lang_dir / "zh_cn.json").read_text(encoding="utf-8")) if (lang_dir / "zh_cn.json").exists() else {}
        en = json.loads((lang_dir / "en_us.json").read_text(encoding="utf-8")) if (lang_dir / "en_us.json").exists() else {}
        required_keys: set[str] = set()
        chat_files: list[str] = []
        for jf in sorted(java_dir.rglob("*.java")):
            raw = jf.read_bytes()
            try:
                src = raw.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"[JAVA-UTF8] {mod_id}/{jf.name} is not valid UTF-8")
                continue
            if "\ufffd" in src:
                errors.append(f"[JAVA-MOJIBAKE] {mod_id}/{jf.name} contains Unicode replacement character U+FFFD")
            rel_parts = jf.relative_to(java_dir).parts
            if "command" not in rel_parts and "Command" not in jf.name and "Test" not in jf.name:
                cnt = src.count(".sendSystemMessage(")
                if cnt > 0:
                    chat_files.append(f"{jf.name}({cnt})")
            for m in re.finditer(r'Component\.translatable\(\s*"([a-z0-9_.-]+)"', src):
                k = m.group(1)
                if not k.endswith(".") and mod_id in k and k != "guide.earth_on_minecraft.line":
                    required_keys.add(k)
        if mod_id == "xuanhuan_earth":
            si = java_dir / "com" / "xxsx" / "xuanhuanearth" / "SpiritImplementItem.java"
            if si.exists():
                stxt = si.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r'([A-Z_]+)\("([a-z0-9_]+)",\s*[0-9.]+D,\s*[0-9.]+D,\s*[0-9.]+D,\s*[0-9.]+D\)', stxt):
                    imp_id = m.group(2)
                    required_keys.add(f"item.xuanhuan_earth.{imp_id}")
                    required_keys.add(f"tooltip.xuanhuan_earth.{imp_id}")
                    required_keys.add(f"message.xuanhuan_earth.implement.cast.{imp_id}")
            xp = java_dir / "com" / "xxsx" / "xuanhuanearth" / "XuanhuanPills.java"
            if xp.exists():
                ptxt = xp.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r'"(message\.xuanhuan_earth\.[a-z0-9_.-]+)"', ptxt):
                    required_keys.add(m.group(1))
        if chat_files:
            errors.append(
                f"[CHAT-SPAM-SYSTEM-MSG] {mod_id} uses sendSystemMessage in {len(chat_files)} non-command classes (must use sendOverlayMessage): {', '.join(chat_files[:8])}"
            )
        missing_zh = sorted(k for k in required_keys if k not in zh)
        missing_en = sorted(k for k in required_keys if k not in en)
        if missing_zh:
            errors.append(f"[LANG-KEY-MISSING-ZH] {mod_id} zh_cn.json missing {len(missing_zh)} keys: {', '.join(missing_zh[:8])}")
        if missing_en:
            errors.append(f"[LANG-KEY-MISSING-EN] {mod_id} en_us.json missing {len(missing_en)} keys: {', '.join(missing_en[:8])}")
        if mod_id != "earth_on_minecraft":
            for kind_prefix in (f"item.{mod_id}.", f"block.{mod_id}."):
                by_val: dict[str, list[str]] = defaultdict(list)
                for k, v in zh.items():
                    if k.startswith(kind_prefix) and k.count(".") == 2:
                        by_val[str(v).strip()].append(k)
                dups_lang = {v: ks for v, ks in by_val.items() if len(ks) > 1}
                if dups_lang:
                    sample = "; ".join(f"{v}={ks}" for v, ks in list(dups_lang.items())[:5])
                    errors.append(f"[LANG-DUP-NAME] {mod_id} zh_cn.json has duplicate {kind_prefix}* names: {sample}")


def check_block_models_avoid_redundant_textures(errors: list[str], warnings: list[str]) -> None:
    """Ensure every block item renders its 3D block model directly and flag orphaned/unreferenced block PNGs."""
    for mod_id, mod_dir in ACTIVE_MODS.items():
        res = mod_dir / "src" / "main" / "resources" / "assets" / mod_id
        bs_dir = res / "blockstates"
        bm_dir = res / "models" / "block"
        im_dir = res / "models" / "item"
        it_dir = res / "items"
        tb_dir = res / "textures" / "block"
        ti_dir = res / "textures" / "item"
        blocks = [f.stem for f in sorted(bs_dir.glob("*.json"))] if bs_dir.exists() else []
        for b in blocks:
            if b in ("structure_projection", "settlement_anchor", "shrine_altar", "spirit_grass_crop", "spirit_herb_crop"):
                continue
            im_f = im_dir / f"{b}.json"
            it_f = it_dir / f"{b}.json"
            if im_f.exists():
                im_data = json.loads(im_f.read_text(encoding="utf-8"))
                par = im_data.get("parent", "")
                if par in ("minecraft:item/generated", "item/generated", "minecraft:item/handheld", "item/handheld"):
                    errors.append(
                        f"[BLOCK-ITEM-FLAT-2D] {mod_id}:models/item/{b}.json uses 2D '{par}' instead of inheriting 3D block model '{mod_id}:block/{b}'"
                    )
            if (ti_dir / f"{b}.png").exists():
                errors.append(
                    f"[BLOCK-REDUNDANT-ITEM-PNG] {mod_id}:textures/item/{b}.png is redundant; block item should render 3D model '{mod_id}:block/{b}' directly"
                )
        if mod_id in ("earth_theology", "xuanhuan_earth", "fantasy_earth", "earth_lore") and tb_dir.exists():
            referenced: set[str] = set()
            for mdir in (bm_dir, im_dir):
                if not mdir.exists():
                    continue
                for mf in mdir.glob("*.json"):
                    mdata = json.loads(mf.read_text(encoding="utf-8"))
                    for v in mdata.get("textures", {}).values():
                        if isinstance(v, str) and v.startswith(f"{mod_id}:block/"):
                            referenced.add(v.split(":block/", 1)[1] + ".png")
            all_tb = {f.relative_to(tb_dir).as_posix() for f in tb_dir.rglob("*.png")}
            orphans = sorted(all_tb - referenced)
            if orphans:
                warnings.append(
                    f"[BLOCK-ORPHAN-PNG] {mod_id} has {len(orphans)} unreferenced textures/block/*.png (e.g. {', '.join(orphans[:6])})"
                )


def check_textures(warnings: list[str]) -> int:
    total_pngs = 0
    min_colors = 10
    for mod_id, mod_dir in ACTIVE_MODS.items():
        tex_dir = mod_dir / "src" / "main" / "resources" / "assets" / mod_id / "textures"
        if not tex_dir.exists():
            continue
        hashes: dict[str, list[str]] = defaultdict(list)
        flat_palettes: list[str] = []
        for p in tex_dir.rglob("*.png"):
            total_pngs += 1
            rel_str = p.relative_to(tex_dir).as_posix()
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            hashes[h].append(rel_str)
            if rel_str.startswith(("item/", "block/")):
                try:
                    with Image.open(p) as im:
                        w, h_px = im.size
                        valid_dim = w in (16, 32, 64, 128, 256) and h_px >= w and (h_px % w == 0)
                        if not valid_dim:
                            warnings.append(f"[TEXTURE-DIM] {mod_id}/{rel_str} has non-power-of-two/strip size {w}x{h_px}")
                        rgba = im.convert("RGBA")
                        px_list = list(rgba.get_flattened_data() if hasattr(rgba, "get_flattened_data") else rgba.getdata())
                        is_tint_overlay = rel_str.endswith(("_cover.png", "_tier_trim.png", "_overlay.png"))
                        colors = {px[:3] for px in px_list if px[3] > 16}
                        if len(colors) < (3 if is_tint_overlay else min_colors):
                            flat_palettes.append(f"{rel_str}({len(colors)}c)")
                        if rel_str.startswith("item/") and sum(1 for px in px_list if px[3] <= 16) < 24:
                            flat_palettes.append(f"{rel_str}(no-alpha-silhouette)")
                except Exception as exc:
                    warnings.append(f"[TEXTURE-READ] {mod_id}/{rel_str} failed to decode: {exc}")
        dups = {h: paths for h, paths in hashes.items() if len(paths) > 1}
        if dups:
            sample = "; ".join(", ".join(paths[:3]) for paths in list(dups.values())[:3])
            warnings.append(f"[TEXTURE-DUP] {mod_id} has {len(dups)} duplicate texture hash groups (e.g. {sample})")
        if flat_palettes:
            sample = ", ".join(flat_palettes[:6])
            warnings.append(
                f"[TEXTURE-FLAT-PALETTE] {mod_id} has {len(flat_palettes)} textures with <{min_colors} distinct RGB shades (e.g. {sample})"
            )
    return total_pngs


def main() -> int:
    parser = argparse.ArgumentParser(description="Earth-series pre-release gate (read-only).")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="workspace root containing earth-series/ (default: current working directory)",
    )
    args = parser.parse_args()
    if args.root is not None:
        set_root(args.root)
    if not EARTH.is_dir():
        print(f"EARTH_GATE error: no earth-series/ under {EARTH.parent}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    node_count = check_knowledge_nodes(errors, warnings)
    check_model_textures_and_items(errors)
    check_loot_tables_and_settlements(errors)
    model_count = check_3d_block_models(errors)
    check_3d_model_uv_and_textures(warnings)
    check_occlusion_and_worldgen_interactions(errors)
    check_pills_and_jei(errors)
    check_chat_spam_and_lang_keys(errors)
    check_block_models_avoid_redundant_textures(errors, warnings)
    png_count = check_textures(warnings)

    print(f"EARTH_GATE nodes={node_count} models_checked={model_count} pngs={png_count} errors={len(errors)} warnings={len(warnings)}")
    for w in warnings:
        print(f"  WARN: {w}")
    for e in errors:
        print(f"  ERR:  {e}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
