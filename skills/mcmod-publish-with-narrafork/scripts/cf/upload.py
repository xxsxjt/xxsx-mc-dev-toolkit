"""CurseForge 版本发布。

用法：
    python upload.py query  <输出目录>
    python upload.py list   <输出目录> --project-id <ID>
    python upload.py upload <清单.json> --project-id <ID> --slug <slug>

令牌只从环境变量 CURSEFORGE_API_TOKEN 读。
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cfhttp import requests, system_env, system_proxy
from curl_cffi import CurlMime

BASE = 'https://minecraft.curseforge.com/api'
FILES_API = 'https://www.curseforge.com/api/v1/mods/{project_id}/files'


def make_session(token: str | None, proxy: str | None):
    session = requests.Session(impersonate='chrome')
    if proxy:
        session.proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
    if token:
        session.headers['X-Api-Token'] = token
    return session


def remote_display_names(session, project_id: str) -> dict[str, str]:
    """线上文件列表，按 displayName 索引；审核中的文件可能不在里面。"""
    try:
        response = session.get(
            FILES_API.format(project_id=project_id),
            params={'pageIndex': 0, 'pageSize': 50, 'sort': 'dateCreated', 'sortDescending': 'true'},
            timeout=40)
        if response.status_code >= 400:
            print('线上文件检查 HTTP', response.status_code, '- 仅依赖本地记录')
            return {}
        return {item.get('displayName', ''): item.get('id') for item in response.json().get('data') or []}
    except Exception as error:
        print('线上文件检查跳过：', error)
        return {}


def load_version_index(path: Path) -> tuple[dict, dict]:
    """把 game-versions.json 索引成「名称 → 候选」与「类型 → 成员」。"""
    if not path.exists():
        raise SystemExit(f'缺少 {path}，先跑 upload.py query')
    by_name, groups = {}, {}
    for item in json.loads(path.read_text(encoding='utf-8')):
        by_name.setdefault(item['name'], []).append(item)
        groups.setdefault(item['gameVersionTypeID'], []).append(item)
    return by_name, groups


def resolve_version_ids(names: list, by_name: dict, groups: dict) -> list:
    """名称转成 API 要的整数 ID。同名多条时，选成员都在同一版本线上的那组。"""
    ids = []
    for name in names:
        if isinstance(name, int):
            ids.append(name)
            continue
        candidates = by_name.get(name, [])
        if not candidates:
            raise SystemExit(f'gameVersions 里的「{name}」在 game-versions.json 里找不到')
        if len(candidates) > 1:
            major = '.'.join(name.split('.')[:2])
            candidates = [c for c in candidates
                          if all(v['name'].startswith(major) for v in groups[c['gameVersionTypeID']])]
            if len(candidates) != 1:
                listed = '、'.join(f'{c["id"]}(type {c["gameVersionTypeID"]})'
                                   for c in by_name[name])
                raise SystemExit(f'gameVersions 里的「{name}」无法唯一确定，候选：{listed}')
        ids.append(candidates[0]['id'])
    return ids


def find_project_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / 'build.gradle').exists():
            return parent
    return start


def strict_build_number(root: Path) -> bool:
    """只有符合 zershyan-mcmod-style 的工程才禁止带 +build.N 的产物。"""
    build = root / 'build.gradle'
    if not build.exists():
        return False
    text = build.read_text(encoding='utf-8', errors='replace')
    return 'buildAlpha' in text and 'finalizeArtifacts' in text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['query', 'list', 'upload'])
    parser.add_argument('path')
    parser.add_argument('--project-id')
    parser.add_argument('--slug')
    parser.add_argument('--proxy', help='覆盖系统代理，形如 127.0.0.1:端口')
    args = parser.parse_args()

    proxy = args.proxy or system_proxy()
    token = system_env('CURSEFORGE_API_TOKEN')

    if args.mode == 'list':
        if not args.project_id:
            raise SystemExit('list 需要 --project-id')
        out = Path(args.path)
        out.mkdir(parents=True, exist_ok=True)
        session = make_session(None, proxy)
        files, page = [], 0
        while True:
            response = session.get(
                FILES_API.format(project_id=args.project_id),
                params={'pageIndex': page, 'pageSize': 50, 'sort': 'dateCreated', 'sortDescending': 'true'},
                timeout=40)
            response.raise_for_status()
            payload = response.json()
            batch = payload.get('data') or []
            files.extend(batch)
            if not batch or len(files) >= (payload.get('pagination') or {}).get('totalCount', 0):
                break
            page += 1
        target = out / f'remote-files-{args.project_id}.json'
        target.write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding='utf-8')
        print(len(files), '个文件 ->', target)
        return

    if not token:
        raise SystemExit('缺少 CURSEFORGE_API_TOKEN，去 https://authors.curseforge.com/#/settings/api-tokens 取')
    session = make_session(token, proxy)

    if args.mode == 'query':
        out = Path(args.path)
        out.mkdir(parents=True, exist_ok=True)
        response = session.get(BASE + '/game/versions', timeout=40)
        print('Versions HTTP', response.status_code)
        response.raise_for_status()
        (out / 'game-versions.json').write_text(
            json.dumps(response.json(), ensure_ascii=False, indent=2), encoding='utf-8')
        return

    if not args.project_id or not args.slug:
        raise SystemExit('upload 需要 --project-id 和 --slug')

    manifest_path = Path(args.path)
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    strict = strict_build_number(find_project_root(manifest_path.parent))
    needs_lookup = any(isinstance(v, str)
                       for release in manifest['files']
                       for v in release['metadata'].get('gameVersions', []))
    by_name, groups = load_version_index(root / 'game-versions.json') if needs_lookup else ({}, {})
    remote = remote_display_names(session, args.project_id)
    if remote:
        print('线上已有文件：', len(remote))

    for release in manifest['files']:
        label = release['minecraft']
        metadata = dict(release['metadata'])
        if not (metadata.get('relations') or {}).get('projects'):
            metadata.pop('relations', None)
        metadata['gameVersions'] = resolve_version_ids(
            metadata.get('gameVersions', []), by_name, groups)
        display_name = metadata.get('displayName', '')
        result_path = root / f'upload-result-{label}.json'
        attempt_path = root / f'upload-attempt-{label}.json'

        if result_path.exists():
            existing = json.loads(result_path.read_text(encoding='utf-8'))
            if existing.get('id'):
                print(label, '已受理，文件 ID', existing['id'])
                continue
        if display_name and display_name in remote:
            print(label, '线上已存在，文件 ID', remote[display_name])
            continue
        if attempt_path.exists():
            raise SystemExit(f'{label} 有未完成的上传记录，先核对线上文件列表再重试')

        artifact = Path(release['artifact'])
        if strict and ('+build.' in artifact.name or '+build.' in display_name):
            raise SystemExit(
                f'{label} 带 +build.N：这个工程用 zershyan-mcmod-style，'
                f'jar 名与 displayName 都只能用正式构建产物')
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest != release['sha256']:
            raise SystemExit(f'{label} 的产物已变化，停止上传')
        attempt_path.write_text(json.dumps({
            'startedUtc': datetime.now(timezone.utc).isoformat(),
            'sha256': digest,
            'metadata': metadata,
        }, ensure_ascii=False, indent=2), encoding='utf-8')

        multipart = CurlMime()
        multipart.addpart(name='metadata', content_type='application/json',
                          data=json.dumps(metadata, ensure_ascii=False).encode('utf-8'))
        multipart.addpart(name='file', filename=artifact.name,
                          content_type='application/java-archive', local_path=str(artifact))
        response = session.post(
            f'{BASE}/projects/{args.project_id}/upload-file', multipart=multipart, timeout=100)
        print(label, '上传 HTTP', response.status_code)
        response_path = root / f'upload-response-{label}.txt'
        response_path.write_text(response.text, encoding='utf-8')
        if response.status_code >= 400:
            try:
                body = response.json()
                detail = body.get('errorMessage') or body.get('message') or ''
            except Exception:
                detail = response.text[:500]
            attempt_path.unlink(missing_ok=True)
            raise SystemExit(
                f'{label} 上传被拒（HTTP {response.status_code}）：{detail}\n'
                f'原始响应：{response_path}')
        response.raise_for_status()

        result = response.json()
        if not result.get('id'):
            raise SystemExit(f'{label} 没有返回文件 ID')
        result.update({
            'minecraft': label,
            'sha256': digest,
            'status': 'accepted; approval not checked',
            'url': f'https://www.curseforge.com/minecraft/mc-mods/{args.slug}/files/{result["id"]}',
            'filesUrl': f'https://www.curseforge.com/minecraft/mc-mods/{args.slug}/files',
            'consoleUrl': f'https://authors.curseforge.com/#/projects/{args.project_id}/files',
        })
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(label, '已受理', result['id'], result['url'])
        print('  文件列表', result['filesUrl'])
        print('  作者后台', result['consoleUrl'], '（审核中的文件只在这里可见）')


if __name__ == '__main__':
    main()
