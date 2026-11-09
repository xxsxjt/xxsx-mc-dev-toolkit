"""生成在 CurseForge 项目设置里补填 Links 的控制台脚本。

用法：
    python scripts/cf/set_links.py --source https://github.com/Zershyan/ForgeAttachment
    python scripts/cf/set_links.py --source <地址> --issues <地址> --wiki <地址>

产物默认写到 curseforge/cf_set_links.js，用法同建项目脚本：
browsermcp 打开项目设置页，eval 整段脚本，console 看结果。
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / 'set_links_template.js'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='源码仓库地址')
    parser.add_argument('--issues', help='问题跟踪地址')
    parser.add_argument('--wiki', help='文档地址')
    parser.add_argument('--out', default='curseforge/cf_set_links.js')
    args = parser.parse_args()

    data = {key: value for key, value in
            (('source', args.source), ('issues', args.issues), ('wiki', args.wiki)) if value}
    if not data:
        raise SystemExit('至少给一个 --source / --issues / --wiki')

    script = (TEMPLATE.read_text(encoding='utf-8')
              .replace('__TITLE__', 'CurseForge 项目设置补填 Links')
              .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script, encoding='utf-8', newline='\n')
    print(f'已生成 {out}')
    print('在项目设置页执行后，手动点一次保存')


if __name__ == '__main__':
    main()
