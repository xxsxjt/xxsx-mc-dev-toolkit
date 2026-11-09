"""生成 CurseForge 建项目的控制台脚本。

用法：
    python create_project.py <项目资料.json> [输出.js]

资料格式见同目录的 project.example.json。相对路径以 JSON 所在目录为基准。
"""
import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_SCRIPTS = HERE.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from deps import ensure_deps

ensure_deps()

TEMPLATE = HERE / 'create_project_template.js'


def is_bilingual(text: str) -> bool:
    """CurseForge 要求项目描述同时给英文和中文。"""
    return bool(re.search(r'[\u4e00-\u9fff]', text)) and bool(re.search(r'[A-Za-z]{3,}', text))


def load_icon(path: Path) -> str:
    """图标转 base64；超过 400px 缩到 400×400 控制脚本体积。"""
    try:
        from PIL import Image
        image = Image.open(path).convert('RGBA')
        if max(image.size) > 400:
            image = image.resize((400, 400), Image.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, 'PNG', optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        return base64.b64encode(path.read_bytes()).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('output', nargs='?')
    parser.add_argument('--no-icon', action='store_true',
                        help='不把图标塞进脚本，体积小很多，图标另行上传')
    parser.add_argument('--step', action='store_true',
                        help='单步模式：每次只推进一个页面，适合会被超时打断的自动化工具')
    parser.add_argument('--pause-at', metavar='STEP',
                        help='填完该步骤后暂停（如 general），留给外部操作，再次执行继续')
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    base = config_path.parent
    config = json.loads(config_path.read_text(encoding='utf-8'))
    resolve = lambda p: Path(p) if Path(p).is_absolute() else base / p

    description_path = resolve(config['description'])
    if not description_path.exists():
        raise SystemExit(f'描述文件不存在：{description_path}')
    description = description_path.read_text(encoding='utf-8')
    if not is_bilingual(description):
        raise SystemExit('项目描述必须中英双语：英文块 + 空行 + --- + 空行 + 中文块')
    icon = ''
    if config.get('icon') and not args.no_icon:
        icon_path = resolve(config['icon'])
        if not icon_path.exists():
            raise SystemExit(
                f'图标不存在：{icon_path}。没有图标就加 --no-icon，'
                f'或先跑 scripts/project/make_icon.py 生成一张')
        icon = load_icon(icon_path)

    data = {
        'name': config['name'],
        'summary': config['summary'],
        'license': config.get('license', ''),
        'dropdowns': config.get('dropdowns', []),
        'distribution': config.get('distribution', 'Allow distribution to 3rd party'),
        'allowComments': config.get('allowComments', True),
        'projectPages': bool(config.get('projectPages', True)),
        'description': description,
        'iconBase64': icon,
        # 默认自动点创建按钮；启用前必须先用交互式提问向用户确认
        'autoCreate': bool(config.get('autoCreate', True)),
        'singleStep': bool(config.get('singleStep', False)) or args.step,
        'pauseAt': config.get('pauseAt') or args.pause_at or '',
    }
    if not 1 <= len(data['summary']) <= 256:
        raise SystemExit(f'简介长度 {len(data["summary"])}，CurseForge 限制 256 字符')

    script = (TEMPLATE.read_text(encoding='utf-8')
              .replace('__TITLE__', data['name'])
              .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    output = Path(args.output) if args.output else base / 'cf_create_project_fill.js'
    output.write_text(script, encoding='utf-8', newline='\n')
    print(f'已生成 {output}（{len(script) // 1024} KB），node --check 后再投入浏览器')
    print('建完后马上把 projectId / slug 写进 curseforge/project.json，否则下次会当成「待建」再走一遍')


if __name__ == '__main__':
    main()
