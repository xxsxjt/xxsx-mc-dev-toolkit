"""提交 MC百科模组条目。

用法：
    python submit.py <配置.json> --dry-run   # 只打印提交体
    python submit.py <配置.json>             # 真提交

配置里写页面上的中文文本，脚本按 assets/mcmod-enums.json 转成代码值。
cookie 由 cookies.py 生成，默认读 .narrafork/mcmod-cookie.txt。
"""
import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'cf'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cfhttp import requests
from author import find as find_author

API = 'https://event.mcmod.cn/action/edit/doEdit/'
ADD_PAGE = 'https://www.mcmod.cn/class/add/'
CAPTCHA_URL = 'https://www.mcmod.cn/frame/edit/EditCaptcha/?id={captcha_id}'
# 产物统一落在当前工程目录下；skill 目录里的旧文件只用于读
WORK_DIR = Path.cwd() / '.narrafork'
COOKIE_FILE = WORK_DIR / 'mcmod-cookie.txt'
VERSION_CACHE = WORK_DIR / 'mcmod-mcversions.json'
CAPTCHA_FILE = WORK_DIR / 'mcmod-captcha.png'
CAPTCHA_BIG = WORK_DIR / 'mcmod-captcha-4x.png'
ENUMS = json.loads((ROOT / 'assets' / 'mcmod-enums.json').read_text(encoding='utf-8'))
# 添加页内嵌全部 MC 版本：var arrMCVer = $.parseJSON('[{"id":"78","name":"26.1.2"},…]')
MC_VERSION_PATTERN = re.compile(r"arrMCVer\s*=\s*\$\.parseJSON\('(\[.*?\])'\)", re.S)
# 资料条目里直接取值的字段
ITEM_FIELDS = ('name', 'ename', 'remark', 'regname', 'damage', 'maxstack', 'oredict', 'metadata', 'content')


def cookie_path() -> Path:
    """工程目录优先；老版本把 cookie 存在 skill 目录，仍兼容读数。"""
    if COOKIE_FILE.exists():
        return COOKIE_FILE
    legacy = ROOT / '.narrafork' / 'mcmod-cookie.txt'
    if legacy.exists():
        print(f'用 skill 目录里的旧 cookie：{legacy}')
        return legacy
    return COOKIE_FILE


def make_session():
    path = cookie_path()
    if not path.exists():
        raise SystemExit(f'缺少 cookie 文件：{COOKIE_FILE}，先跑 cookies.py dump')
    session = requests.Session(impersonate='chrome')
    session.headers['Cookie'] = path.read_text(encoding='utf-8').strip()
    return session


def fetch_mc_versions(session) -> dict[str, str]:
    """版本号 -> 版本 ID；每次可能变，必须现取。"""
    html = session.get(ADD_PAGE, timeout=30).text
    match = MC_VERSION_PATTERN.search(html)
    if not match:
        raise SystemExit('添加页里没找到 MC 版本列表，登录态可能已失效')
    return {item['name']: item['id'] for item in json.loads(match.group(1))}


def cached_mc_versions(session, refresh: bool = False) -> dict[str, str]:
    """缓存版本映射：提交时不再请求添加页，否则会刷新验证码。"""
    if not refresh and VERSION_CACHE.exists():
        return json.loads(VERSION_CACHE.read_text(encoding='utf-8'))
    versions = fetch_mc_versions(session)
    VERSION_CACHE.parent.mkdir(parents=True, exist_ok=True)
    VERSION_CACHE.write_text(json.dumps(versions, ensure_ascii=False, indent=1), encoding='utf-8')
    return versions


def grab_captcha(session, captcha_id: str = 'class_add_0') -> Path:
    """取一张新的验证码图片。每次请求都会刷新，取完必须紧接着提交。"""
    session.get(ADD_PAGE, timeout=30)
    response = session.get(CAPTCHA_URL.format(captcha_id=captcha_id), timeout=30,
                           headers={'Referer': ADD_PAGE})
    if response.status_code >= 400 or not response.content:
        raise SystemExit(f'取验证码失败：HTTP {response.status_code}')
    CAPTCHA_FILE.parent.mkdir(parents=True, exist_ok=True)
    CAPTCHA_FILE.write_bytes(response.content)
    print(f'验证码已保存：{CAPTCHA_FILE}（{len(response.content)} 字节）')
    try:
        from PIL import Image
        with Image.open(CAPTCHA_FILE) as image:
            image.resize((image.width * 4, image.height * 4), Image.LANCZOS).save(CAPTCHA_BIG)
        print(f'放大 4 倍：{CAPTCHA_BIG}')
    except ImportError:
        print('装了 Pillow 可以另外输出 4 倍放大图')
    return CAPTCHA_FILE


def code_of(group: str, label: str) -> str:
    table = ENUMS[group]
    for code, text in table.items():
        if text == label or text.split(' ')[0] == label:
            return code
    raise SystemExit(f'{group} 里没有「{label}」，可选：{", ".join(table.values())}')


def indexed(values) -> dict:
    """勾选类字段要求 {序号: 值}，序号只是遍历下标。"""
    return {str(i): v for i, v in enumerate(values)} if values else {}


def has_chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text or ''))


def secondary_name(name: str, ename: str) -> str:
    """主要名称没有中文时，次要名称必须留空，否则百科会弹重复警告。"""
    if not ename:
        return ''
    return ename if has_chinese(name) else ''


def clean_sname(name: str, ename: str, sname: str) -> str:
    """简写只能是社区通用缩写：字母数字符号，且不能与主/次名称重复。"""
    if not sname:
        return ''
    if not re.fullmatch(r'[A-Za-z0-9 ._+#&-]+', sname):
        print(f'简写名称「{sname}」含字母数字符号以外的字符，已跳过（百科只收 enstring）')
        return ''
    if sname in (name, ename):
        print(f'简写名称「{sname}」与主/次名称相同，已跳过')
        return ''
    if len(sname) > 16:
        print(f'简写名称「{sname}」有 {len(sname)} 个字符，不像缩写，已跳过')
        return ''
    return sname


def join_field(value) -> str:
    """标签与关键词在页面上是逗号分隔的文本框，不是多值对象。"""
    return value if isinstance(value, str) else ','.join(str(item) for item in value)


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


def cover_data_url(path: Path, width: int = 480, height: int = 300) -> str:
    """按 16:10 居中裁切后缩放，返回页面隐藏字段要的 data URL。"""
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit('需要 Pillow 处理封面：python -m pip install Pillow')

    image = Image.open(path).convert('RGB')
    ratio = width / height
    w, h = image.size
    if w / h > ratio:
        cropped = int(h * ratio)
        left = (w - cropped) // 2
        image = image.crop((left, 0, left + cropped, h))
    else:
        cropped = int(w / ratio)
        top = (h - cropped) // 2
        image = image.crop((0, top, w, top + cropped))
    image = image.resize((width, height), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()


def build(cfg: dict, mc_ids: dict[str, str]) -> dict:
    ename = secondary_name(cfg['name'], cfg.get('ename', ''))
    data = {
        'name': cfg['name'],
        'ename': ename,
        'sname': clean_sname(cfg['name'], ename, cfg.get('sname', '')),
        'intro': cfg.get('intro', ''),
        'modid': cfg['modid'],
        'cfprojectid': str(cfg.get('cfprojectid', '')),
        'mrprojectid': str(cfg.get('mrprojectid', '')),
        'activity': {},
        'category': indexed([
            code_of('categoryCore', c) if c in ENUMS['categoryCore'].values()
            else code_of('categoryExtra', c)
            for c in cfg.get('category', [])
        ]),
        'platform': indexed([code_of('platform', p) for p in cfg.get('platform', ['JAVA版 (JAVA Edition)'])]),
        'api': indexed([code_of('api', a) for a in cfg.get('api', [])]),
        'mode-1': indexed([code_of('mode', cfg.get('mode1', '需装'))]),
        'mode-2': indexed([code_of('mode', cfg.get('mode2', '需装'))]),
        'status': indexed([code_of('status', cfg.get('status', '活跃'))]),
        'source': indexed([code_of('source', cfg.get('source', '开源'))]),
        'content': cfg.get('content', ''),
    }

    if cfg.get('mcVersions'):
        # {"NeoForge": ["26.1.2"], "Forge": ["1.20.1"]}
        mc_map = {}
        for loader, versions in cfg['mcVersions'].items():
            api_code = loader if loader in ENUMS['api'] else code_of('api', loader)
            ids = []
            for version in versions:
                version_id = mc_ids.get(version)
                if not version_id:
                    raise SystemExit(f'页面里没有 MC 版本「{version}」')
                ids.append(version_id)
            mc_map[api_code] = indexed(ids)
        data['mcversion'] = mc_map

    if cfg.get('tags'):
        data['tags'] = join_field(cfg['tags'])
    if cfg.get('keys'):
        data['keys'] = clean_keys(cfg['keys'])
    if cfg.get('coverPath'):
        cover = Path(cfg['coverPath'])
        if not cover.exists():
            raise SystemExit(f'封面不存在：{cover}')
        data['cover-data'] = cover_data_url(cover)

    if cfg.get('links'):
        data['link'] = {
            str(i): {'title': link.get('title', ''), 'custom': link.get('custom', ''),
                     'href': link.get('href', ''), 'text': link.get('text', '')}
            for i, link in enumerate(cfg['links'])
        }

    if cfg.get('license'):
        lic = cfg['license']
        types = lic.get('types') or [lic.get('type', '源码')]
        data['license'] = {
            '0': {
                # 页面显示「通用」时提交空字符串
                'title': '' if lic.get('title', '通用') in ('通用', '') else lic['title'],
                'list': {'0': {
                    'type': [t if t in ENUMS['licenseType'] else code_of('licenseType', t) for t in types],
                    'name': lic['name'],
                    'link': lic.get('link', ''),
                    'text': lic.get('text', ''),
                }},
            }
        }

    if cfg.get('authors'):
        links = {}
        for i, author in enumerate(cfg['authors']):
            author_id = str(author.get('id') or '')
            if not author_id and author.get('name'):
                name = author['name']
                if '<' in name or '>' in name:
                    raise SystemExit(f'作者名还是占位符「{name}」，替换成真实作者名再试')
                hits = find_author(name)
                if not hits:
                    raise SystemExit(f'找不到作者「{name}」')
                author_id = hits[0]['id']
                print(f'作者 {author["name"]} -> ID {author_id}')
            if not author_id:
                continue
            roles = author.get('roles') or [author.get('role', '所有者')]
            codes = [r if r in ENUMS['role'] else code_of('role', r) for r in roles]
            links[str(i)] = {'select': codes, 'id': author_id}
        data['author'] = {'link': links, 'add': {}}

    return {
        'action': cfg.get('action', 'class_add'),
        'edit-id': '0',
        'class-id': str(cfg.get('classId', '0')),
        'redo-id': str(cfg.get('redoId', '0')),
        'class-data': data,
    }


def build_item(cfg: dict) -> dict:
    """资料条目：字段落在 item-data 下，edit-id 与 class-id 都是模组 ID。"""
    category = cfg.get('category', '物品/方块')
    code = category if category in ENUMS['itemCategory'] else code_of('itemCategory', category)
    module_id = str(cfg.get('classId') or cfg.get('moduleId') or '')
    if not module_id:
        raise SystemExit('资料条目需要 classId（模组 ID）')

    data = {key: str(cfg.get(key, '')) for key in ITEM_FIELDS}
    data['category'] = indexed([code])
    if cfg.get('type'):
        data['type'] = cfg['type']
    if cfg.get('icon32'):
        data['icon-32x-data'] = cfg['icon32']
    if cfg.get('icon128'):
        data['icon-128x-data'] = cfg['icon128']

    return {
        'action': cfg.get('action', 'item_add'),
        'edit-id': module_id,
        'class-id': module_id,
        'redo-id': str(cfg.get('redoId', '0')),
        'item-data': data,
    }


def submit(session, payload: dict) -> dict:
    response = session.post(
        API,
        data={'data': json.dumps(payload, ensure_ascii=False)},
        headers={'Referer': ADD_PAGE, 'X-Requested-With': 'XMLHttpRequest'},
        timeout=60)
    try:
        return response.json()
    except ValueError:
        raise SystemExit(f'返回了非 JSON：{response.text[:200]}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('--dry-run', action='store_true', help='只打印提交体，不发送')
    parser.add_argument('--captcha-url', action='store_true',
                        help='取一张验证码图片后退出，不提交')
    parser.add_argument('--captcha', help='提交时附带的验证码')
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    session = make_session()
    kind = cfg.get('kind', 'class')
    captcha_id = (f"item_add_{cfg.get('classId') or cfg.get('moduleId') or ''}"
                  if kind == 'item' else 'class_add_0')

    if args.captcha_url:
        if kind != 'item':
            # 取图时会重新加载添加页，版本映射一并刷新并缓存
            cached_mc_versions(session, refresh=True)
        grab_captcha(session, captcha_id)
        print('把图片给用户识别，拿到验证码后带 --captcha 重跑，中间不要再请求添加页')
        return

    if kind == 'item':
        payload = build_item(cfg)
    else:
        # 走缓存，避免提交前请求添加页把验证码刷掉
        payload = build(cfg, cached_mc_versions(session))
    if args.captcha:
        payload['captcha'] = args.captcha
    print(json.dumps(payload, ensure_ascii=False, indent=1))

    if args.dry_run:
        print('\n（dry-run，未提交）')
        return

    result = submit(session, payload)
    print('\n返回：', json.dumps(result, ensure_ascii=False))
    if result.get('state') == 0:
        print('提交成功：', result.get('url', '(无地址)'))
        print('记下条目 ID 并写进 docs/mcmod/entries.json；同一配置再跑一次会新建第二条，'
              '改已有条目要带 redo-id')
    elif result.get('state') == 117 and 'captcha' not in payload:
        raise SystemExit('state=117 且没有带验证码，可能是缺验证码；先跑 --captcha-url 取图')
    else:
        raise SystemExit(f'提交失败：state={result.get("state")}')


if __name__ == '__main__':
    main()
