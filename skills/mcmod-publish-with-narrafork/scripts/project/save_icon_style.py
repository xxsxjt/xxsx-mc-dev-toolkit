"""保存占位图标的样式，供 make_icon.py 复用。

用法：
    python scripts/project/save_icon_style.py '{"font":"georgiab.ttf","fontSize":56,...}'
    python scripts/project/save_icon_style.py --file style.json
    python scripts/project/save_icon_style.py --reset

样式统一存在 skill 目录的 .narrafork/icon-style.json，跨工程复用。
表单里点「保存为默认」会把 JSON 发过来，直接喂给这个脚本即可。
"""
import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
STYLE_FILE = SKILL_ROOT / '.narrafork' / 'icon-style.json'

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


def parse(raw: str) -> dict:
    """表单发来的是「保存图标样式：{…}」，允许整段带前缀的文本。"""
    start = raw.find('{')
    end = raw.rfind('}')
    if start < 0 or end <= start:
        raise SystemExit('没找到 JSON，传完整对象或 --file')
    return json.loads(raw[start:end + 1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', nargs='?', help='样式 JSON，可直接粘表单发来的整段文本')
    parser.add_argument('--file', help='从文件读样式 JSON')
    parser.add_argument('--reset', action='store_true', help='恢复默认样式')
    args = parser.parse_args()

    if args.reset:
        style = dict(DEFAULT_STYLE)
    elif args.file:
        style = parse(Path(args.file).read_text(encoding='utf-8'))
    elif args.json:
        style = parse(args.json)
    else:
        raise SystemExit('给一个 JSON、--file 或 --reset')

    merged = {**DEFAULT_STYLE, **style}
    STYLE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STYLE_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'样式已保存：{STYLE_FILE}')
    for key in ('font', 'fontSize', 'lineGap', 'letterSpacing', 'align', 'fg', 'bg', 'canvas'):
        print(f'  {key}: {merged[key]}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
