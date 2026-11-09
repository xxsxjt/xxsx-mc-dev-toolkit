#!/usr/bin/env python3
"""Offline isometric 3D block-model renderer & UV/texture auditor for Minecraft Java block models.

Renders every multi-element 3D block model in active Earth-series mods into a static
contact-sheet PNG (workflow-reports/earth-3d-blocks-preview.png) so UV squashing,
wrong face textures, and single-texture reuse are immediately visible without starting the game.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
EARTH = ROOT / 'earth-series'
OUT_PATH = ROOT / 'workflow-reports' / 'earth-3d-blocks-preview.png'

MOD_DIRS = {
    'earth_lore': EARTH / 'earth_lore' / 'neoforge-26.1.2',
    'earth_theology': EARTH / 'earth_theology' / 'neoforge-26.1.2',
    'xuanhuan_earth': EARTH / 'xuanhuan_earth' / 'neoforge-26.2',
    'fantasy_earth': EARTH / 'fantasy_earth' / 'neoforge-26.2',
}

def resolve_tex_path(mod_id: str, mod_dir: Path, textures: dict, ref: str) -> Path | None:
    seen = set()
    val = ref
    while isinstance(val, str) and val.startswith('#'):
        k = val[1:]
        if k in seen or k not in textures:
            return None
        seen.add(k)
        val = textures[k]
    if not isinstance(val, str):
        return None
    ns, rel = val.split(':', 1) if ':' in val else (mod_id, val)
    target_mod = MOD_DIRS.get(ns, mod_dir)
    p = target_mod / 'src' / 'main' / 'resources' / 'assets' / ns / 'textures' / f'{rel}.png'
    return p if p.is_file() else None

def iso_project(x: float, y: float, z: float, cx: float, cy: float, scale: float) -> tuple[float, float]:
    # Standard isometric projection looking from South-East-Top (+X right-up, +Z left-up, +Y up)
    px = cx + (x - z) * math.cos(math.radians(30)) * scale
    py = cy + (x + z) * math.sin(math.radians(30)) * scale - y * scale
    return px, py

def sample_face_color(img: Image.Image, uv: list[float], shade: float) -> tuple[int, int, int, int]:
    w, h = img.size
    u1 = max(0, min(w - 1, int(uv[0] * w / 16.0)))
    v1 = max(0, min(h - 1, int(uv[1] * h / 16.0)))
    u2 = max(u1 + 1, min(w, int(math.ceil(uv[2] * w / 16.0))))
    v2 = max(v1 + 1, min(h, int(math.ceil(uv[3] * h / 16.0))))
    crop = img.crop((u1, v1, u2, v2)).convert('RGBA')
    px = list(crop.getdata())
    opaque = [p for p in px if p[3] > 32]
    if not opaque:
        return (120, 120, 120, 180)
    r = int(sum(p[0] for p in opaque) / len(opaque) * shade)
    g = int(sum(p[1] for p in opaque) / len(opaque) * shade)
    b = int(sum(p[2] for p in opaque) / len(opaque) * shade)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255)

def render_model_card(mod_id: str, mod_dir: Path, model_path: Path) -> Image.Image:
    card = Image.new('RGBA', (220, 240), (28, 31, 38, 255))
    draw = ImageDraw.Draw(card)
    data = json.loads(model_path.read_text(encoding='utf-8'))
    textures = data.get('textures', {})
    elements = data.get('elements', [])
    tex_cache: dict[str, Image.Image] = {}

    def get_tex(ref: str) -> Image.Image:
        if ref not in tex_cache:
            tp = resolve_tex_path(mod_id, mod_dir, textures, ref)
            tex_cache[ref] = Image.open(tp).convert('RGBA') if tp else Image.new('RGBA', (16, 16), (255, 0, 255, 255))
        return tex_cache[ref]

    # Sort elements back-to-front by (x + y + z)
    sorted_elems = sorted(elements, key=lambda e: sum(e.get('from', [0, 0, 0])) + sum(e.get('to', [16, 16, 16])))
    cx, cy, scale = 110.0, 145.0, 5.5
    squash_count = 0
    for el in sorted_elems:
        x1, y1, z1 = el.get('from', [0, 0, 0])
        x2, y2, z2 = el.get('to', [16, 16, 16])
        faces = el.get('faces', {})
        dx, dy, dz = abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)
        for fn, fd in faces.items():
            uv = fd.get('uv')
            if uv and len(uv) == 4:
                uw, uh = abs(uv[2] - uv[0]), abs(uv[3] - uv[1])
                if fn in ('north', 'south') and ((dx <= 4 and uw >= 12) or (dy <= 4 and uh >= 12)):
                    squash_count += 1
                elif fn in ('east', 'west') and ((dz <= 4 and uw >= 12) or (dy <= 4 and uh >= 12)):
                    squash_count += 1
                elif fn in ('up', 'down') and ((dx <= 4 and uw >= 12) or (dz <= 4 and uh >= 12)):
                    squash_count += 1
        # Draw visible isometric faces: south (+Z), east (+X), up (+Y)
        if 'south' in faces:
            fd = faces['south']
            uv = fd.get('uv', [x1, 16 - y2, x2, 16 - y1])
            col = sample_face_color(get_tex(fd.get('texture', '')), uv, 0.78)
            pts = [iso_project(x1, y1, z2, cx, cy, scale), iso_project(x2, y1, z2, cx, cy, scale),
                   iso_project(x2, y2, z2, cx, cy, scale), iso_project(x1, y2, z2, cx, cy, scale)]
            draw.polygon(pts, fill=col, outline=(18, 20, 24, 255))
        if 'east' in faces:
            fd = faces['east']
            uv = fd.get('uv', [16 - z2, 16 - y2, 16 - z1, 16 - y1])
            col = sample_face_color(get_tex(fd.get('texture', '')), uv, 0.62)
            pts = [iso_project(x2, y1, z2, cx, cy, scale), iso_project(x2, y1, z1, cx, cy, scale),
                   iso_project(x2, y2, z1, cx, cy, scale), iso_project(x2, y2, z2, cx, cy, scale)]
            draw.polygon(pts, fill=col, outline=(18, 20, 24, 255))
        if 'up' in faces:
            fd = faces['up']
            uv = fd.get('uv', [x1, z1, x2, z2])
            col = sample_face_color(get_tex(fd.get('texture', '')), uv, 1.0)
            pts = [iso_project(x1, y2, z1, cx, cy, scale), iso_project(x2, y2, z1, cx, cy, scale),
                   iso_project(x2, y2, z2, cx, cy, scale), iso_project(x1, y2, z2, cx, cy, scale)]
            draw.polygon(pts, fill=col, outline=(18, 20, 24, 255))

    unique_pngs = {v for k, v in textures.items() if k != 'particle' and not str(v).startswith('#')}
    bad = squash_count > 0 or (len(elements) >= 4 and len(unique_pngs) <= 1)
    border = (220, 72, 64, 255) if bad else (72, 188, 110, 255)
    draw.rectangle([0, 0, 219, 239], outline=border, width=2)
    draw.text((8, 6), f'{mod_id}', fill=(170, 180, 195, 255))
    draw.text((8, 20), f'{model_path.stem}', fill=(240, 244, 250, 255))
    draw.text((8, 216), f'el={len(elements)} tex={len(unique_pngs)} sq={squash_count}', fill=border)
    return card

def main() -> int:
    cards: list[Image.Image] = []
    for mod_id, mod_dir in MOD_DIRS.items():
        mdir = mod_dir / 'src' / 'main' / 'resources' / 'assets' / mod_id / 'models' / 'block'
        if not mdir.exists():
            continue
        for p in sorted(mdir.glob('*.json')):
            data = json.loads(p.read_text(encoding='utf-8'))
            if data.get('elements'):
                cards.append(render_model_card(mod_id, mod_dir, p))
    cols = 6
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * 228 + 12, rows * 248 + 12), (16, 18, 22, 255))
    for idx, card in enumerate(cards):
        r, c = divmod(idx, cols)
        sheet.paste(card, (12 + c * 228, 12 + r * 248))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_PATH)
    print(f'Rendered {len(cards)} 3D block models -> {OUT_PATH}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
