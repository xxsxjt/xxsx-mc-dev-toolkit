"""把表单提交的 payload 变成 CurseForge 上传清单。

用法：
    python scripts/cf/make_manifest.py payload.json [--out curseforge/release-manifest.json]

payload 是 GenUI 表单返回的 `JSON.parse(values.payload)` 结果，含 versions 数组。
约定当前目录是模组工程根目录，jar 在 build/libs 下。
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

SIDES = {'双端': ['Client', 'Server'], '客户端': ['Client'], '服务端': ['Server']}


def read_properties() -> dict:
    path = Path('gradle.properties')
    values = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip()
    return values


def jar_prefix() -> str:
    """archivesName 可能带引号、引用属性，也可能根本没配。"""
    build = Path('build.gradle')
    if build.exists():
        text = build.read_text(encoding='utf-8', errors='replace')
        found = re.search(r'archivesName\s*=\s*([^\s;/]+)', text)
        if found:
            value = found.group(1).strip('"\'')
            reference = re.fullmatch(r'\$\{?(\w+)\}?', value)
            if reference:
                value = reference.group(1)
            return read_properties().get(value, value)
    return Path.cwd().name


def check_version(version: str) -> None:
    if not re.fullmatch(r'\d+(\.\d+)*', version):
        raise SystemExit(
            f'modVersion「{version}」不是纯版本号。这里只填 gradle.properties 的 mod_version，'
            f'不带 MC 版本和 +build.N')


def is_bilingual(text: str) -> bool:
    """CurseForge 要求描述与更新日志都同时给英文和中文。"""
    return bool(re.search(r'[\u4e00-\u9fff]', text)) and bool(re.search(r'[A-Za-z]{3,}', text))


def check_changelog(version: str, changelog: str) -> None:
    if changelog and not is_bilingual(changelog):
        raise SystemExit(
            f'{version} 的更新日志必须中英双语：英文块 + 空行 + --- + 空行 + 中文块')


def collect_relations(dependencies: list) -> dict:
    projects = []
    for dep in dependencies or []:
        if not dep.get('projectId'):
            continue
        projects.append({'projectId': int(dep['projectId']),
                         'type': dep.get('type') or 'requiredDependency'})
    return {'projects': projects} if projects else {}


def detect_style() -> bool:
    """工程是否符合 zershyan-mcmod-style 的构建约定。"""
    build = Path('build.gradle')
    if not build.exists():
        return False
    text = build.read_text(encoding='utf-8', errors='replace')
    return 'buildAlpha' in text and 'finalizeArtifacts' in text


def resolve_artifact(prefix: str, version: str, minecraft: str, style: bool) -> Path | None:
    """在 build/libs 里定位这个版本要上传的主包。"""
    libs = Path('build/libs')
    if style:
        candidate = libs / f'{prefix}-{version}-{minecraft}.jar'
        return candidate if candidate.exists() else None
    candidates = [p for p in libs.glob('*.jar')
                  if version in p.name
                  and not re.search(r'-(sources|javadoc|dev|shaded)\.jar$', p.name)]
    return candidates[0] if len(candidates) == 1 else None


def build_files(versions: list, dependencies: list) -> tuple[list, list]:
    prefix = jar_prefix()
    style = detect_style()
    relations = collect_relations(dependencies)
    libs = Path('build/libs')
    available = sorted(p.name for p in libs.glob('*.jar')) if libs.is_dir() else []
    files, problems = [], []

    for version in versions:
        check_version(version['modVersion'])
        changelog = version.get('changelog') or ''
        check_changelog(version['modVersion'], changelog)
        for minecraft in version.get('mcVersions') or []:
            for loader in version.get('loaders') or []:
                artifact = resolve_artifact(prefix, version['modVersion'], minecraft, style)
                if not artifact:
                    problems.append((f"{version['modVersion']} / {minecraft}", available))
                    continue
                game_versions = [minecraft, loader, version.get('javaVersion')]
                game_versions += SIDES.get(version.get('env', '双端'), ['Client', 'Server'])
                metadata = {
                    'changelog': changelog,
                    'changelogType': 'markdown',
                    'displayName': artifact.stem,
                    'releaseType': version.get('releaseType') or 'release',
                    'gameVersions': [v for v in game_versions if v],
                }
                if relations:
                    metadata['relations'] = relations
                files.append({
                    'minecraft': minecraft,
                    'artifact': str(artifact).replace('\\', '/'),
                    'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                    'metadata': metadata,
                })
    return files, problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('payload')
    parser.add_argument('--out', default='curseforge/release-manifest.json')
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding='utf-8'))
    versions = payload.get('versions') or []
    if not versions:
        raise SystemExit('payload 里没有 versions，确认用的是 FormFull / FormRelease 表单')

    files, problems = build_files(versions, payload.get('dependencies') or [])
    if problems:
        lines = [f'找不到 {desc} 对应的主包' for desc, _ in problems]
        available = problems[0][1]
        if available:
            lines.append('build/libs 里现有：' + '、'.join(available))
        else:
            lines.append('build/libs 是空的，先在对应分支跑 ./gradlew build')
        raise SystemExit('\n'.join(lines))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'files': files}, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'已生成 {out}（{len(files)} 个文件）')
    for item in files:
        print(f"  {item['minecraft']:<10} {item['metadata']['releaseType']:<8} "
              f"{item['metadata']['displayName']}")
    if payload.get('wiki'):
        print('这份配置要发 MC百科，百科配置另存 docs/mcmod/mod-config.json')


if __name__ == '__main__':
    main()
