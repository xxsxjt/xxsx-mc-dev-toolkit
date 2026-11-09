"""生成 16x16 占位 PNG（纯标准库，无外部依赖）。"""
import os
import struct
import zlib


def make_png(path, rgb, size=16):
    """写出一个纯色 size×size PNG。"""
    r, g, b = rgb
    raw = b"".join(b"\x00" + bytes([r, g, b]) * size for _ in range(size))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fp:
        fp.write(png)
    print("wrote", path, len(png), "bytes")


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(PROJECT_ROOT, "src", "main", "resources", "assets", "examplemod", "textures")

TEXTURES = {
    os.path.join("item", "example_item.png"): (0x8A, 0xB0, 0xD8),
    os.path.join("item", "example_custom_item.png"): (0xD8, 0xA0, 0x8A),
    os.path.join("block", "example_block.png"): (0x9C, 0x9C, 0x9C),
    os.path.join("block", "example_custom_block.png"): (0xC0, 0xB0, 0x90),
}

for rel, rgb in TEXTURES.items():
    make_png(os.path.join(ROOT, rel), rgb)
