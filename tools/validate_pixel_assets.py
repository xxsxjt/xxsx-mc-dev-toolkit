"""Validate Minecraft pixel item icons: size, binary alpha, silhouette, palette and uniqueness.

Supports the two tiers used across the toolkit:

* 16x16 RGBA for simple materials (dusts, ingots, nuggets, plates, simple tools);
* 32x32 RGBA for complex artifacts (ritual swords, compasses, 3/4 books, talismans, bags).

Checks per file: exact size, RGBA mode, binary alpha (0 or 255), a fully transparent
background margin, transparent corners (silhouette, not a full-bleed square), and a
minimum number of distinct opaque RGB shades. Across files: SHA-256 uniqueness.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image


def validate(
    path: Path,
    size: int,
    min_colors: int,
    max_colors: int | None,
    min_margin: int,
    min_transparent: int | None,
) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return ["file does not exist"]

    try:
        with Image.open(path) as source:
            source.verify()
        with Image.open(path) as source:
            if source.format != "PNG":
                return [f"expected PNG, found {source.format or 'unknown format'}"]
            if source.size != (size, size):
                errors.append(f"expected {size}x{size}, found {source.width}x{source.height}")
            if source.mode != "RGBA":
                errors.append(f"expected RGBA, found {source.mode}")
            image = source.convert("RGBA")
            color_counts = image.getcolors(maxcolors=size * size) or []
    except Exception as exc:  # Pillow raises several format-specific exceptions.
        return [f"cannot decode PNG: {exc}"]

    if image.size != (size, size):
        return errors

    alpha_values = {rgba[3] for _, rgba in color_counts}
    if 0 not in alpha_values:
        errors.append("no transparent pixels; icon background must be transparent")
    partial_alpha = sorted(value for value in alpha_values if value not in (0, 255))
    if partial_alpha:
        errors.append(f"partial alpha is not allowed (found {partial_alpha})")

    transparent_px = sum(count for count, rgba in color_counts if rgba[3] == 0)
    threshold = min_transparent if min_transparent is not None else max(24, size * size * 3 // 32)
    if transparent_px < threshold:
        errors.append(
            f"only {transparent_px} transparent pixels; need >= {threshold} (no-alpha-silhouette)"
        )

    opaque_colors = {rgba[:3] for _, rgba in color_counts if rgba[3] == 255}
    if not opaque_colors:
        errors.append("image has no fully opaque pixels")
    elif len(opaque_colors) < min_colors:
        errors.append(f"found {len(opaque_colors)} opaque colors; minimum is {min_colors}")
    elif max_colors is not None and len(opaque_colors) > max_colors:
        errors.append(f"found {len(opaque_colors)} opaque colors; maximum is {max_colors}")

    alpha_bbox = image.getchannel("A").getbbox()
    if alpha_bbox is None:
        errors.append("image is fully transparent")
    else:
        left, top, right, bottom = alpha_bbox
        margins = (left, top, size - right, size - bottom)
        if min(margins) < min_margin:
            errors.append(
                f"transparent edge margin is {min(margins)} px; minimum is {min_margin} px"
            )

    corners = (
        image.getpixel((0, 0))[3],
        image.getpixel((size - 1, 0))[3],
        image.getpixel((0, size - 1))[3],
        image.getpixel((size - 1, size - 1))[3],
    )
    if any(corner != 0 for corner in corners):
        errors.append(f"all four corners must be transparent, found alpha {corners}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate pixel item icons (size, binary alpha, silhouette, palette, SHA-256 uniqueness)."
    )
    parser.add_argument("images", nargs="+", type=Path, help="PNG files to validate")
    parser.add_argument(
        "--size",
        type=int,
        default=16,
        help="expected square icon size in pixels: 16 for simple materials, 32 for complex artifacts (default: 16)",
    )
    parser.add_argument(
        "--min-colors",
        type=int,
        default=12,
        help="minimum distinct opaque RGB shades; 12-18 matches the cold-shadow to warm-highlight ramp (default: 12)",
    )
    parser.add_argument(
        "--max-colors",
        type=int,
        default=None,
        help="optional maximum distinct opaque RGB shades (omit for no upper bound)",
    )
    parser.add_argument(
        "--min-margin",
        type=int,
        default=None,
        help="minimum transparent edge margin in pixels (default: 1 for 16x16, 2 for 32x32)",
    )
    parser.add_argument(
        "--min-transparent",
        type=int,
        default=None,
        help="minimum count of alpha=0 pixels (default: 24 for 16x16, 96 for 32x32)",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="skip the SHA-256 uniqueness gate across the supplied files",
    )
    args = parser.parse_args()

    if args.size < 1:
        parser.error("--size must be positive")
    if args.min_colors < 1:
        parser.error("--min-colors must be positive")
    if args.max_colors is not None and args.max_colors < args.min_colors:
        parser.error("--max-colors must be >= --min-colors")
    min_margin = args.min_margin if args.min_margin is not None else (2 if args.size >= 32 else 1)
    if min_margin < 0:
        parser.error("--min-margin must be non-negative")

    failed = False
    hashes: dict[str, list[Path]] = defaultdict(list)
    for path in args.images:
        errors = validate(
            path, args.size, args.min_colors, args.max_colors, min_margin, args.min_transparent
        )
        if path.is_file():
            hashes[hashlib.sha256(path.read_bytes()).hexdigest()].append(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(
                f"OK {path}: {args.size}x{args.size} RGBA, binary alpha, silhouette, "
                f">= {args.min_colors} opaque colors, >= {min_margin}px edge margin"
            )

    if not args.allow_duplicates:
        dups = {digest: paths for digest, paths in hashes.items() if len(paths) > 1}
        for digest, paths in dups.items():
            failed = True
            joined = ", ".join(str(p) for p in paths)
            print(f"FAIL duplicate SHA-256 {digest[:16]}...: {joined}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

