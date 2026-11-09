"""生成百科控制台提交脚本。

没有 cookie 文件、或者不想在本地存登录态时用它：脚本在百科页面里运行，
浏览器自带登录态和验证码，不经过本地。

用法：
    python console.py <配置.json> [输出.js]

配置里用 "kind" 区分：
    "module"（默认）  模组条目，字段同 docs/mcmod/mod-config.json
    "item"            资料条目，需要 classId 与 entries 数组

生成后在目标页面按 F12，粘贴运行。运行前先在页面上把验证码填好。
"""
import argparse
import base64
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATES = {
    'module': HERE / 'console' / 'module.js',
    'item': HERE / 'console' / 'item.js',
}


def cover_base64(cfg: dict) -> str:
    """有封面文件就转成 base64，页面里注入文件输入框后由页面自己裁剪上传。"""
    path = cfg.get('coverPath')
    if not path:
        return ''
    file = Path(path)
    if not file.exists():
        print(f'封面不存在，跳过注入：{file}')
        return ''
    return base64.b64encode(file.read_bytes()).decode()


def clean_keys(value, limit: int = 10, max_width: int = 24) -> str:
    """搜索关键词只该放别名、外号、分词——百科明文禁止滥用。"""
    if not value:
        return ''
    items = value if isinstance(value, list) else str(value).split(',')
    kept = []
    for item in items:
        item = str(item).strip()
        if not item:
            continue
        width = sum(2 if ord(ch) > 127 else 1 for ch in item)
        if width > max_width:
            print(f'关键词「{item}」太长了，不像别名，已跳过')
            continue
        kept.append(item)
    if len(kept) > limit:
        print(f'关键词有 {len(kept)} 条，只保留前 {limit} 条')
    return ','.join(kept[:limit])


def secondary_name(name: str, ename: str) -> str:
    """主要名称没有中文时，次要名称必须留空，否则百科会弹重复警告。"""
    if not ename:
        return ''
    return ename if re.search(r'[\u4e00-\u9fff]', name or '') else ''


def clean_sname(name: str, ename: str, sname: str) -> str:
    """简写只能是社区通用缩写：字母数字符号，且不能与主/次名称重复。"""
    if not sname:
        return ''
    if not re.fullmatch(r'[A-Za-z0-9 ._+#&-]+', sname):
        print(f'简写名称「{sname}」含字母数字符号以外的字符，已跳过')
        return ''
    if sname in (name, ename):
        print(f'简写名称「{sname}」与主/次名称相同，已跳过')
        return ''
    if len(sname) > 16:
        print(f'简写名称「{sname}」有 {len(sname)} 个字符，不像缩写，已跳过')
        return ''
    return sname


def to_module_data(cfg: dict) -> dict:
    """把 mod-config 的写法转成控制台模板期待的字段。"""
    categories = cfg.get('category') or []
    core = next((c for c in categories if c in ('实用', '科技', '魔法', '冒险', '农业', '装饰', 'LIB', '魔改', '辅助')), '实用')
    cover = cover_base64(cfg)
    ename = secondary_name(cfg['name'], cfg.get('ename', ''))
    return {
        'name': cfg['name'],
        'ename': ename,
        'sname': clean_sname(cfg['name'], ename, cfg.get('sname', '')),
        'intro': cfg.get('intro', ''),
        'modid': cfg['modid'],
        'cfprojectid': str(cfg.get('cfprojectid', '')),
        'mrprojectid': str(cfg.get('mrprojectid', '')),
        'core': core,
        'elements': [c for c in categories if c != core],
        'platforms': ['JAVA版 (JAVA Edition)'],
        'versions': cfg.get('mcVersions') or {},
        'client': cfg.get('mode1', '需装'),
        'server': cfg.get('mode2', '需装'),
        'status': cfg.get('status', '活跃'),
        'source': cfg.get('source', '开源'),
        'tags': ','.join(cfg.get('tags') or []),
        'keys': clean_keys(cfg.get('keys')),
        'authors': cfg.get('authors') or [],
        'links': [[l.get('title', ''), l.get('href', ''), l.get('text', '')]
                  for l in cfg.get('links') or []],
        'content': cfg.get('content', ''),
        'images': {},
        'cover': cover,
        'injectCover': bool(cover),
        'coverPath': cfg.get('coverPath', ''),
    }


def build_module(cfg: dict) -> str:
    template = TEMPLATES['module'].read_text(encoding='utf-8')
    return template.replace('__DATA__', json.dumps(to_module_data(cfg), ensure_ascii=False))


def build_item(cfg: dict) -> str:
    entries = cfg.get('entries') or []
    if not entries:
        raise SystemExit('item 配置里需要 entries 数组')
    template = TEMPLATES['item'].read_text(encoding='utf-8')
    return (template
            .replace('__DRY_RUN__', 'true' if cfg.get('dryRun') else 'false')
            .replace('__ENTRIES__', json.dumps(entries, ensure_ascii=False))
            .replace('__REMARK__', json.dumps(cfg.get('remark', ''), ensure_ascii=False)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('output', nargs='?')
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    kind = cfg.get('kind', 'module')
    if kind not in TEMPLATES:
        raise SystemExit(f'未知 kind：{kind}')

    script = build_module(cfg) if kind == 'module' else build_item(cfg)
    output = Path(args.output) if args.output else config_path.with_suffix('.console.js')
    output.write_text(script, encoding='utf-8', newline='\n')

    target = ('物品资料添加页 /item/add/<模组ID>/' if kind == 'item'
              else '模组添加页 /class/add/')
    print(f'已生成 {output}（{len(script) // 1024} KB）')
    print(f'用法：打开{target}，填好验证码，F12 粘贴运行')


if __name__ == '__main__':
    main()
