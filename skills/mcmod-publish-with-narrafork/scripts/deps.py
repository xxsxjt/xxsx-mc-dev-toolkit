"""第三方库的查找路径：工程本地优先，其次 skill 目录。

依赖装在 skill 的 `.narrafork/pylibs` 后所有工程共用一份；
某个工程自己装过的话优先用工程的，互不影响。
"""
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def candidates() -> list[Path]:
    return [Path.cwd() / '.narrafork' / 'pylibs', SKILL_ROOT / '.narrafork' / 'pylibs']


def ensure_deps() -> Path | None:
    """把第一个存在的依赖目录加进 sys.path，返回加的是哪个。"""
    for path in candidates():
        if path.is_dir():
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
            return path
    return None


def active() -> Path | None:
    """当前实际生效的依赖目录（以 curl_cffi 是否存在为准）。"""
    for path in candidates():
        if (path / 'curl_cffi').is_dir():
            return path
    return None
