"""把运行依赖装到 skill 目录，装一次所有工程共用。

用法：
    python scripts/setup.py           装缺失的依赖
    python scripts/setup.py --check   只检查，缺什么列什么
    python scripts/setup.py --force   全部重装

工程自己 `.narrafork/pylibs` 里有依赖时优先用工程的，这里装的是兜底。
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PYLIBS = SKILL_ROOT / '.narrafork' / 'pylibs'

# (import 名, pip 包名, 用途)
PACKAGES = [
    ('curl_cffi', 'curl_cffi', 'CurseForge 请求，伪装 TLS 指纹'),
    ('websocket', 'websocket-client', '从浏览器读 cookie'),
    ('PIL', 'Pillow', '生成占位图标、处理封面'),
]


def has(module: str) -> bool:
    """只看装没装在这个目录里；系统 site-packages 里有不算。"""
    return (PYLIBS / module).is_dir()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='只检查')
    parser.add_argument('--force', action='store_true', help='全部重装')
    args = parser.parse_args()

    missing = [(m, p, use) for m, p, use in PACKAGES if args.force or not has(m)]

    if not missing:
        print(f'依赖齐全：{PYLIBS}')
        return

    if args.check:
        for module, package, use in missing:
            print(f'缺 {package:18} {use}')
        print(f'\n装到 skill 目录：python scripts/setup.py')
        return

    print(f'装到 {PYLIBS}')
    for module, package, use in missing:
        print(f'  {package}（{use}）')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--target', str(PYLIBS),
                    *[p for _, p, _ in missing]], check=True)

    still = [p for m, p, _ in PACKAGES if not has(m)]
    if still:
        raise SystemExit(f'这些没装成功：{"、".join(still)}')
    print('装好了，所有工程共用这一份')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
