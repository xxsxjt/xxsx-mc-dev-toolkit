"""按样式生成占位图标。

用法：
    python scripts/project/make_icon.py ForgeAttachment
    python scripts/project/make_icon.py ForgeAttachment --style icon-style.json
    python scripts/project/make_icon.py ForgeAttachment --out src/main/resources/logo.png \
        --font georgiab.ttf --lines "Forge|Attachment" --font-size 64 --fg "#3b1f0e"

样式默认读 SKILL 目录的 .narrafork/icon-style.json，跨工程复用。
需要 Pillow。
"""
import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from deps import ensure_deps

ensure_deps()

SKILL_ROOT = Path(__file__).resolve().parents[2]
STYLE_FILE = SKILL_ROOT / '.narrafork' / 'icon-style.json'

# 字体文件 → 各平台候选路径。canvas 预览用同名字体族近似。
FONTS = {
    'segoeuib.ttf': ('C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    'arialbd.ttf': ('C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
    'calibrib.ttf': ('C:/Windows/Fonts/calibrib.ttf', 'C:/Windows/Fonts/arialbd.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    'impact.ttf': ('C:/Windows/Fonts/impact.ttf', 'C:/Windows/Fonts/arialbd.ttf',
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    'bahnschrift.ttf': ('C:/Windows/Fonts/bahnschrift.ttf', 'C:/Windows/Fonts/arialbd.ttf',
                        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    'georgiab.ttf': ('C:/Windows/Fonts/georgiab.ttf', 'C:/Windows/Fonts/timesbd.ttf',
                     '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'),
    'consolab.ttf': ('C:/Windows/Fonts/consolab.ttf', 'C:/Windows/Fonts/courbd.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'),
}

DEFAULT_STYLE = {
    'font': 'segoeuib.ttf',
    'lines': ['auto'],
    'stacked': True,
    'fontSize': 56,
    'lineGap': 1.12,
    'letterSpacing': 0,
    'align': 'center',
    'uppercase': False,
    'border': 0,
    'padding': 0.04,
    'fg': '#111111',
    'bg': '#ffffff',
    'canvas': 400,
}


def split_words(name: str) -> list[str]:
    """ForgeAttachment → Forge / Attachment，ADCore → AD / Core。"""
    return re.findall(r'[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+|\d+', name) or [name]


def auto_lines(name: str) -> list[str]:
    words = split_words(name)
    if len(words) < 2:
        return [name]
    mid = (len(words) + 1) // 2
    return [' '.join(words[:mid]), ' '.join(words[mid:])]


def resolve_lines(style: dict, name: str) -> list[str]:
    lines = style.get('lines') or ['auto']
    if lines == ['auto'] or lines == ['']:
        lines = auto_lines(name)
    if not style.get('stacked'):
        lines = [' '.join(lines)]
    lines = [line.upper() if style.get('uppercase') else line for line in lines]
    return [line for line in lines if line]


def load_style(path: Path | None) -> dict:
    style = dict(DEFAULT_STYLE)
    target = path or STYLE_FILE
    if target and target.exists():
        loaded = json.loads(target.read_text(encoding='utf-8'))
        style.update({key: value for key, value in loaded.items() if key in DEFAULT_STYLE})
        if style['font'] not in FONTS:
            style['font'] = DEFAULT_STYLE['font']
    return style


def load_font(name: str, size: int):
    from PIL import ImageFont
    for candidate in FONTS.get(name, FONTS['segoeuib.ttf']):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size)


def advance(draw, char: str, font, spacing: float) -> float:
    left, _, right, _ = draw.textbbox((0, 0), char, font=font)
    return right - left + spacing


def line_width(draw, text: str, font, spacing: float) -> float:
    if not text:
        return 0
    return sum(advance(draw, ch, font, spacing) for ch in text) - spacing


def fit_size(draw, lines: list, limit_w: float, limit_h: float, style: dict) -> int:
    """从大到小试，直到所有行放得进宽高。"""
    spacing = float(style['letterSpacing'])
    gap = float(style['lineGap'])
    size = int(limit_h)
    while size > 10:
        font = load_font(style['font'], size)
        widest = max(line_width(draw, line, font, spacing) for line in lines)
        height = len(lines) * size * gap
        if widest <= limit_w and height <= limit_h:
            return size
        size -= 2
    return 10


def draw_lines(draw, lines: list, style: dict, size: int, px: int) -> None:
    spacing = float(style['letterSpacing'])
    gap = float(style['lineGap'])
    font = load_font(style['font'], px)
    padding = float(style.get('padding', 0.04))
    ascent, descent = font.getmetrics()

    line_height = px * gap
    block = len(lines) * line_height
    top = (size - block) / 2

    for index, line in enumerate(lines):
        width = line_width(draw, line, font, spacing)
        align = style['align']
        if align == 'left':
            cursor = size * padding
        elif align == 'right':
            cursor = size - size * padding - width
        else:
            cursor = (size - width) / 2
        # 每行在自己的行框里垂直居中：基线 = 行顶 + (行高 + 上伸 - 下伸) / 2
        baseline = top + index * line_height + (line_height + ascent - descent) / 2
        for char in line:
            left, _, _, _ = draw.textbbox((0, 0), char, font=font)
            draw.text((cursor - left, baseline), char, fill=style['fg'], font=font, anchor='ls')
            cursor += advance(draw, char, font, spacing)


def make(name: str, out: Path, style: dict) -> Path:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit('需要 Pillow：python -m pip install Pillow')

    size = int(style['canvas'])
    padding = float(style.get('padding', 0.04))
    lines = resolve_lines(style, name)
    image = Image.new('RGB', (size, size), style['bg'])
    draw = ImageDraw.Draw(image)

    limit = size * (1 - 2 * padding)
    px = int(style['fontSize']) or fit_size(draw, lines, limit, limit, style)
    draw_lines(draw, lines, {**style, 'padding': padding}, size, px)

    if int(style.get('border') or 0):
        width = int(style['border'])
        draw.rectangle([width / 2, width / 2, size - 1 - width / 2, size - 1 - width / 2],
                       outline=style['fg'], width=width)

    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, 'PNG', optimize=True)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='模组英文名')
    parser.add_argument('--out', default='src/main/resources/logo.png')
    parser.add_argument('--style', help='样式 JSON，默认读 skill 的 .narrafork/icon-style.json')
    parser.add_argument('--save-style', action='store_true',
                        help='把命令行给的样式写回 skill 的 .narrafork/icon-style.json')
    parser.add_argument('--font', choices=sorted(FONTS))
    parser.add_argument('--lines', help='竖线分隔的多行文本，例如 "Forge|Attachment"')
    parser.add_argument('--no-stack', action='store_true', help='合成一行')
    parser.add_argument('--font-size', type=int)
    parser.add_argument('--line-gap', type=float)
    parser.add_argument('--letter-spacing', type=float)
    parser.add_argument('--align', choices=['center', 'left', 'right'])
    parser.add_argument('--uppercase', action='store_true')
    parser.add_argument('--border', type=int)
    parser.add_argument('--fg')
    parser.add_argument('--bg')
    parser.add_argument('--canvas', type=int)
    parser.add_argument('--force', action='store_true',
                        help='目标已存在时也覆盖；工程本来就有图标时不要加')
    args = parser.parse_args()

    style = load_style(Path(args.style) if args.style else None)
    overrides = {
        'font': args.font,
        'lines': args.lines.split('|') if args.lines else None,
        'stacked': False if args.no_stack else None,
        'fontSize': args.font_size,
        'lineGap': args.line_gap,
        'letterSpacing': args.letter_spacing,
        'align': args.align,
        'uppercase': True if args.uppercase else None,
        'border': args.border,
        'fg': args.fg,
        'bg': args.bg,
        'canvas': args.canvas,
    }
    for key, value in overrides.items():
        if value is not None:
            style[key] = value

    if args.save_style:
        STYLE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STYLE_FILE.write_text(json.dumps(style, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'样式已保存：{STYLE_FILE}')

    out = Path(args.out)
    if out.exists() and not args.force:
        raise SystemExit(
            f'{out} 已存在。工程已有图标就不要再跑这个脚本；'
            f'确认要用占位图覆盖它，加 --force')

    path = make(args.name, out, style)
    lines = resolve_lines(style, args.name)
    print(f'已生成图标：{path}（{style["canvas"]}×{style["canvas"]}，{style["font"]}，'
          f'{len(lines)} 行：{" / ".join(lines)}）')


if __name__ == '__main__':
    main()
