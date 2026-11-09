"""使用标准库生成工程模板的占位 PNG。"""

from __future__ import annotations

from pathlib import Path
import struct
import zlib


def write_png(path: Path, rgb: tuple[int, int, int], width: int = 16, height: int = 16) -> None:
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    print(f"已生成 {path}")


def main() -> None:
    resources = Path(__file__).resolve().parents[1] / "src/main/resources"
    textures = resources / "assets/examplemod/textures"
    placeholders = {
        "item/example_item.png": (0x8A, 0xB0, 0xD8),
        "item/example_custom_item.png": (0xD8, 0xA0, 0x8A),
        "block/example_block.png": (0x9C, 0x9C, 0x9C),
        "block/example_custom_block.png": (0xC0, 0xB0, 0x90),
    }
    for relative_path, color in placeholders.items():
        write_png(textures / relative_path, color)
    write_png(textures / "entity/example_layer.png", (0x8A, 0xB0, 0xD8), 64, 32)
    write_png(resources / "logo.png", (0x8A, 0xB0, 0xD8), 64, 64)


if __name__ == "__main__":
    main()
