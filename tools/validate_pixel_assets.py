"""Check small RGBA PNGs against the Earth-series pixel-icon constraints."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def validate(path: Path, max_colors: int, min_margin: int) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return ["file does not exist"]

    try:
        with Image.open(path) as source:
            source.verify()
        with Image.open(path) as source:
            if source.format != "PNG":
                return [f"expected PNG, found {source.format or 'unknown format'}"]
            if source.size != (16, 16):
                errors.append(f"expected 16x16, found {source.width}x{source.height}")
            if source.mode != "RGBA":
                errors.append(f"expected RGBA, found {source.mode}")
            image = source.convert("RGBA")
            color_counts = image.getcolors(maxcolors=256) or []
    except Exception as exc:  # Pillow raises several format-specific exceptions.
        return [f"cannot decode PNG: {exc}"]

    if image.size != (16, 16):
        return errors

    alpha_values = {rgba[3] for _, rgba in color_counts}
    if 0 not in alpha_values:
        errors.append("no transparent pixels; icon background must be transparent")
    partial_alpha = sorted(value for value in alpha_values if value not in (0, 255))
    if partial_alpha:
        errors.append(f"partial alpha is not allowed (found {partial_alpha})")

    opaque_colors = {rgba[:3] for _, rgba in color_counts if rgba[3] == 255}
    if not opaque_colors:
        errors.append("image has no fully opaque pixels")
    elif len(opaque_colors) > max_colors:
        errors.append(f"found {len(opaque_colors)} opaque colors; maximum is {max_colors}")

    alpha_bbox = image.getchannel("A").getbbox()
    if alpha_bbox is None:
        errors.append("image is fully transparent")
    else:
        left, top, right, bottom = alpha_bbox
        margins = (left, top, 16 - right, 16 - bottom)
        if min(margins) < min_margin:
            errors.append(
                f"transparent edge margin is {min(margins)} px; minimum is {min_margin} px"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate 16x16 RGBA pixel icons (size, transparency, palette and margins)."
    )
    parser.add_argument("images", nargs="+", type=Path, help="PNG files to validate")
    parser.add_argument("--max-colors", type=int, default=5, help="maximum opaque RGB colors (default: 5)")
    parser.add_argument("--min-margin", type=int, default=1, help="minimum transparent edge margin in pixels (default: 1)")
    args = parser.parse_args()

    if args.max_colors < 1 or args.min_margin < 0:
        parser.error("--max-colors must be positive and --min-margin must be non-negative")

    failed = False
    for path in args.images:
        errors = validate(path, args.max_colors, args.min_margin)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {path}: 16x16 RGBA, binary alpha, <= {args.max_colors} opaque colors, >= {args.min_margin}px edge margin")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
