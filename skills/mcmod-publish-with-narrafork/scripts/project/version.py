"""把版本号写进各分支的 gradle.properties。

用法：
    python version.py master=0.0.1
    python version.py main=0.0.1 1.20.1=0.0.1 --commit

单分支只改文件不提交。多分支必须加 --commit：git 不允许带着未提交的
gradle.properties 切分支，只有逐分支提交才能走下去。
版本已经是目标值的分支会跳过，不产生空提交，也不会中断后面的分支。
gradle.properties 自身必须干净，其他文件的改动用 --allow-dirty 放行。
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

PROPERTIES = Path('gradle.properties')


def git(*args, check: bool = True) -> str:
    result = subprocess.run(['git', *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise SystemExit(f'git {" ".join(args)} 失败：{result.stderr.strip()}')
    return result.stdout


def current_branch() -> str:
    return git('rev-parse', '--abbrev-ref', 'HEAD').strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pairs', nargs='+', help='branch=version，可写多个')
    parser.add_argument('--allow-dirty', action='store_true',
                        help='工作区有其他改动也继续；gradle.properties 自身仍须干净')
    parser.add_argument('--commit', action='store_true',
                        help='每改完一个分支就提交 gradle.properties；多分支时必须加')
    args = parser.parse_args()

    pairs = []
    for item in args.pairs:
        branch, sep, version = item.partition('=')
        if not sep or not branch.strip() or not version.strip():
            raise SystemExit(f'格式应为 branch=version：{item}')
        pairs.append((branch.strip(), version.strip()))

    props_dirty = git('status', '--porcelain', '--', 'gradle.properties').strip()
    if props_dirty:
        raise SystemExit('gradle.properties 有未提交改动，先处理再回填：\n' + props_dirty)

    dirty = git('status', '--porcelain').strip()
    if dirty and not args.allow_dirty:
        raise SystemExit('工作区有其他未提交改动。确认不影响切分支就加 --allow-dirty：\n' + dirty)

    if len(pairs) > 1 and not args.commit:
        raise SystemExit(
            '多分支回填写完一个分支就切不走——git 不会带着未提交的 gradle.properties 切换。\n'
            '确认要逐分支自动提交就加 --commit（只提交 gradle.properties）。')

    original = current_branch()
    changed = []
    skipped = []
    try:
        for branch, version in pairs:
            print(f'切到 {branch}')
            git('checkout', branch)
            if not PROPERTIES.exists():
                raise SystemExit(f'{branch} 上没有 gradle.properties')
            text = PROPERTIES.read_text(encoding='utf-8')
            updated, count = re.subn(r'(?m)^mod_version=.*$', f'mod_version={version}', text)
            if count != 1:
                raise SystemExit(f'{branch} 的 gradle.properties 里没有唯一的 mod_version 行')
            if updated == text:
                # 内容没变就别写、更别提交：空提交会让 git 报错并中断后面的分支
                print(f'  已经是 {version}，跳过')
                skipped.append(branch)
                continue
            PROPERTIES.write_text(updated, encoding='utf-8')
            changed.append((branch, version))
            print(f'  mod_version={version}')
            if args.commit:
                git('add', 'gradle.properties')
                git('commit', '-m', f'发布 {version}')
                print('  已提交 gradle.properties')
    finally:
        if current_branch() != original:
            print(f'回到 {original}')
            git('checkout', original, check=False)

    summary = []
    if changed:
        summary.append(f'回填 {len(changed)} 个分支' + ('并提交' if args.commit else '（未提交，确认后自行 commit）'))
    if skipped:
        summary.append(f'跳过 {len(skipped)} 个（版本已是目标值：{"、".join(skipped)}）')
    print('，'.join(summary) or '没有需要改动的分支')


if __name__ == '__main__':
    main()
