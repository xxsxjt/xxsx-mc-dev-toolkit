"""开局体检：一条命令给出工程事实、构建规范、凭据与项目状态。

用法：
    python scripts/preflight.py           人读摘要 + 下一步建议
    python scripts/preflight.py --json    机器可读

约定当前目录是模组工程根目录。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

STYLE_SKILL = Path.home() / '.agents' / 'skills' / 'zershyan-mcmod-style'

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from deps import active as active_deps


def read_properties(path: Path) -> dict:
    values = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def git(*args: str) -> str:
    try:
        result = subprocess.run(['git', *args], capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception:
        return ''


def detect_build(text: str) -> dict:
    style_version = re.search(
        r'version\s*=\s*["\']?\$\{?baseVersion\}?\s*\+build', text) or \
        re.search(r'\$\{?mod_version\}?-?\$\{?minecraft_version\}?\+build', text)
    toolchain = re.search(r'JavaLanguageVersion\.of\((\d+)\)', text)
    archives = re.search(r'archivesName\s*=\s*["\']([^"\']+)["\']', text)
    return {
        'hasBuildAlpha': 'buildAlpha' in text,
        'hasFinalizeArtifacts': 'finalizeArtifacts' in text,
        'versionUsesBuildNumber': bool(style_version),
        'archivesName': archives.group(1) if archives else None,
        'javaVersion': int(toolchain.group(1)) if toolchain else None,
    }


def find_lang(modid: str) -> dict:
    return find_lang_in(Path('.'), modid)


def find_lang_in(module_dir: Path, modid: str) -> dict:
    found = {}
    for base in (module_dir / 'src/main/resources/assets', module_dir / 'src/generated/resources/assets'):
        folder = base / modid / 'lang'
        if not folder.is_dir():
            continue
        for file in sorted(folder.glob('*.json')):
            found[file.stem] = str(file)
    return found


def parse_mods_toml(module_dir: Path) -> dict:
    for rel in ('src/main/resources/META-INF/neoforge.mods.toml',
                'src/main/templates/META-INF/neoforge.mods.toml',
                'src/main/resources/META-INF/mods.toml',
                'src/main/templates/META-INF/mods.toml'):
        p = module_dir / rel
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        info = {}
        for key in ('modId', 'version', 'displayName', 'license', 'authors', 'logoFile'):
            m = re.search(rf'^\s*{key}\s*=\s*["\']([^"\'$]+?)["\']', text, re.M)
            if m:
                info[key] = m.group(1).strip()
        desc_m = re.search(r'description\s*=\s*\'\'\'(.*?)\'\'\'', text, re.S) or \
                 re.search(r'description\s*=\s*"""(.*?)"""', text, re.S) or \
                 re.search(r'^\s*description\s*=\s*["\']([^"\'$]+?)["\']', text, re.M)
        if desc_m:
            info['description'] = ' '.join(desc_m.group(1).strip().split())
        return info
    return {}


def resolve_module_dir() -> Path:
    cwd = Path('.')
    if (cwd / 'src/main').is_dir():
        return cwd
    candidates = sorted(
        [d for d in cwd.iterdir() if d.is_dir() and (d / 'build.gradle').exists() and (d / 'src/main').is_dir()],
        key=lambda d: (0 if d.name.startswith('neoforge-26') else 1 if d.name.startswith('neoforge') else 2, d.name)
    )
    return candidates[0] if candidates else cwd


def classify_jars(paths, strict_build_number: bool) -> tuple[list, list]:
    """挑出能上传的主包。只有符合 style 规范的工程才按 +build.N 排除。"""
    usable, excluded = [], []
    for path in sorted(paths):
        name = path.name
        is_attachment = re.search(r'-(sources|javadoc|dev|shaded)\.jar$', name)
        has_build_number = strict_build_number and '+build.' in name
        if is_attachment or has_build_number:
            excluded.append(name)
        else:
            usable.append(name)
    return usable, excluded


def collect() -> dict:
    module_dir = resolve_module_dir()
    root_props_path = Path('gradle.properties')
    mod_props_path = module_dir / 'gradle.properties'
    build_path = (module_dir / 'build.gradle') if (module_dir / 'build.gradle').exists() else Path('build.gradle')
    if not root_props_path.exists() and not mod_props_path.exists() and not build_path.exists():
        return {'isModProject': False,
                'reason': '当前目录没有 gradle.properties 与 build.gradle'}

    props = {}
    if root_props_path.exists():
        props.update(read_properties(root_props_path))
    if mod_props_path.exists() and mod_props_path != root_props_path:
        props.update(read_properties(mod_props_path))
    build_text = build_path.read_text(encoding='utf-8', errors='replace') if build_path.exists() else ''
    build = detect_build(build_text)
    toml_info = parse_mods_toml(module_dir)
    ver_m = re.search(r'^\s*version\s*=\s*["\']([^"\'$]+?)["\']', build_text, re.M)
    neo_m = re.search(r'neoForge\s*\{[\s\S]*?version\s*=\s*["\']([^"\'$]+?)["\']', build_text)

    modid = props.get('mod_id') or toml_info.get('modId', '')
    loader = ('NeoForge' if ('neo_version' in props or 'net.neoforged.moddev' in build_text or module_dir.name.startswith('neoforge')) else
              'Forge' if ('forge_version' in props or 'legacyforge' in build_text or module_dir.name.startswith('forge')) else
              'Fabric' if 'fabric_version' in props or 'loader_version' in props else None)
    branches = [b.strip().lstrip('* ') for b in git('branch', '-a').replace('remotes/origin/', '').splitlines()]
    branches = sorted({b for b in branches if b and 'HEAD' not in b})

    style_ok = build['hasBuildAlpha'] and build['hasFinalizeArtifacts'] and build['versionUsesBuildNumber']
    libs_dir = (module_dir / 'build/libs') if (module_dir / 'build/libs').is_dir() else Path('build/libs')
    all_jars = sorted(libs_dir.glob('*.jar')) if libs_dir.is_dir() else []
    usable, excluded = classify_jars(all_jars, style_ok)
    mc_ver = props.get('minecraft_version', '')
    if not mc_ver and '-' in module_dir.name:
        mc_ver = module_dir.name.split('-', 1)[1]

    return {
        'isModProject': True,
        'root': str(Path.cwd()),
        'moduleDir': str(module_dir),
        'modid': modid,
        'modName': props.get('mod_name') or toml_info.get('displayName', ''),
        'modVersion': props.get('mod_version') or toml_info.get('version') or (ver_m.group(1) if ver_m else ''),
        'minecraftVersion': mc_ver,
        'loader': loader,
        'loaderVersion': props.get('neo_version') or props.get('forge_version') or (neo_m.group(1) if neo_m else ''),
        'javaVersion': build['javaVersion'],
        'license': props.get('mod_license') or toml_info.get('license', ''),
        'authors': props.get('mod_authors') or toml_info.get('authors', ''),
        'description': props.get('mod_description') or toml_info.get('description', ''),
        'jarPrefix': build['archivesName'] or Path.cwd().name,
        'branches': branches,
        'dirty': bool(git('status', '--porcelain')),
        'remote': git('remote', 'get-url', 'origin'),
        'hasLogo': any((module_dir / p).exists() for p in
                       ('src/main/resources/logo.png', 'src/main/resources/icon.png', f'src/main/resources/assets/{modid}/icon.png')),
        'lang': find_lang_in(module_dir, modid) if modid else {},
        'build': build,
        'styleSkillInstalled': STYLE_SKILL.is_dir(),
        'matchesStyleSkill': style_ok,
        'uploadableJars': usable,
        'excludedJars': excluded,
    }


def collect_env() -> dict:
    deps = active_deps()
    cookie = Path('.narrafork/mcmod-cookie.txt')
    return {
        'token': bool(os.environ.get('CURSEFORGE_API_TOKEN')),
        'pylibs': deps is not None,
        'pylibsPath': str(deps) if deps else '',
        'cookie': cookie.exists(),
        'projectJson': Path('curseforge/project.json').exists(),
        'gameVersions': Path('curseforge/game-versions.json').exists(),
    }


def next_steps(project: dict, env: dict) -> list:
    steps = []
    if not project['isModProject']:
        return ['当前目录不是模组工程，先切到工程根目录再跑一次']
    if project['matchesStyleSkill']:
        steps.append('用 FormBuild 表单问分支与 mod_version，勾了回填就跑 version.py')
    if not env['token']:
        steps.append('提醒用户设置 CURSEFORGE_API_TOKEN')
    if not env['pylibs']:
        steps.append('python scripts/setup.py  # 依赖装到 skill 目录，所有工程共用')
    if not env['gameVersions']:
        steps.append('python scripts/cf/upload.py query curseforge')
    if not env['projectJson']:
        steps.append('确认 CF 上有没有现成项目；没有就按 references/curseforge.md#项目创建 建一个')
    else:
        steps.append('读 curseforge/project.json 拿 projectId / slug')
    steps.append('出配置表单收集信息，图标定稿后再逐分支跑 ./gradlew build')
    if not env['cookie']:
        steps.append('发百科前先取 cookie，见 references/mcmod.md')
    return steps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', action='store_true', help='只输出 JSON')
    args = parser.parse_args()

    project = collect()
    env = collect_env()
    report = {'project': project, 'env': env, 'next': next_steps(project, env)}

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if not project['isModProject']:
        print('✗', project['reason'])
        return

    build = project['build']
    style = '符合' if project['matchesStyleSkill'] else '不符合'
    print(f"工程      {project['root']}")
    print(f"模组      {project['modName']} ({project['modid']})")
    print(f"版本      {project['modVersion']}  ·  {project['minecraftVersion']}  ·  "
          f"{project['loader']}  ·  Java {project['javaVersion']}")
    print(f"许可      {project['license']}  ·  {project['authors']}")
    print(f"分支      {', '.join(project['branches']) or '（无）'}"
          f"{'  · 工作区有改动' if project['dirty'] else ''}")
    print(f"JAR 前缀  {project['jarPrefix']}")
    print(f"图标      {'有' if project['hasLogo'] else '缺'}"
          f"  ·  语言文件 {', '.join(project['lang']) or '未找到'}")
    print()
    print(f"构建规范  {style} zershyan-mcmod-style"
          f"（buildAlpha {'✓' if build['hasBuildAlpha'] else '✗'}  "
          f"finalizeArtifacts {'✓' if build['hasFinalizeArtifacts'] else '✗'}  "
          f"版本号拼法 {'✓' if build['versionUsesBuildNumber'] else '✗'}）")
    if project['matchesStyleSkill']:
        print('          只上传不带 +build.N 的 jar')
    if project['uploadableJars']:
        print(f"可上传    {', '.join(project['uploadableJars'])}")
    elif project['excludedJars']:
        print('可上传    没有：现存 jar 都带 +build.N 或是附属包，等图标定稿再跑 ./gradlew build')
    else:
        print('可上传    没有：还没构建，等图标定稿再跑 ./gradlew build')
    if project['excludedJars']:
        print(f"不上传    {len(project['excludedJars'])} 个（带编号或附属包）")
    print()
    print(f"凭据      令牌 {'✓' if env['token'] else '✗'}   "
          f"依赖 {'✓' if env['pylibs'] else '✗'}   "
          f"百科 cookie {'✓' if env['cookie'] else '✗'}")
    if env['pylibs']:
        print(f"          {env['pylibsPath']}")
    print(f"记录      CF 项目 {'✓' if env['projectJson'] else '✗'}   "
          f"版本标签 {'✓' if env['gameVersions'] else '✗'}")
    print()
    print('下一步')
    for index, step in enumerate(report['next'], 1):
        print(f'  {index}. {step}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
