"""CurseForge 请求封装：用 curl_cffi 模拟 Chrome 指纹，避开 Cloudflare 挑战页。

用法：
    from http import requests, BrowserOpener, system_env
    requests.get(url, impersonate='chrome')
"""
import io
import os
import sys
import urllib.error
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from deps import ensure_deps

# 依赖目录：CF_HTTP_RUNTIME 优先，其次工程本地，最后 skill 目录
_RUNTIME = os.environ.get('CF_HTTP_RUNTIME')
if _RUNTIME:
    if _RUNTIME not in sys.path:
        sys.path.insert(0, _RUNTIME)
else:
    ensure_deps()

try:
    from curl_cffi import requests
except ImportError as error:
    raise SystemExit(
        '缺少 curl_cffi。装到 skill 目录（所有工程共用）：python scripts/setup.py'
    ) from error


def system_env(name: str) -> str | None:
    """读环境变量；Windows 上进程里没有时回退到用户环境变量，避免 setx 后新进程读不到。"""
    value = os.environ.get(name)
    if value:
        return value
    if sys.platform != 'win32':
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as handle:
            return winreg.QueryValueEx(handle, name)[0]
    except OSError:
        return None


def system_proxy() -> str | None:
    """读系统代理，返回 `host:port` 形式。"""
    for name in ('HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy'):
        value = os.environ.get(name)
        if value:
            return value.split('://', 1)[-1].rstrip('/')
    if sys.platform != 'win32':
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as handle:
            enabled = winreg.QueryValueEx(handle, 'ProxyEnable')[0]
            proxy = winreg.QueryValueEx(handle, 'ProxyServer')[0] if enabled else None
    except OSError:
        return None
    if proxy and '=' in proxy:
        entries = dict(item.split('=', 1) for item in proxy.split(';') if '=' in item)
        proxy = entries.get('https') or entries.get('http')
    return proxy or None


class _Response(io.BytesIO):
    """BytesIO 不能挂自定义属性，用来承载 status。"""
    status: int


class BrowserOpener:
    """与 urllib 的 opener 兼容，>=400 抛 HTTPError。"""

    def __init__(self, proxy: str | None = None):
        self.proxy = proxy or system_proxy()

    def open(self, req, timeout: int = 55):
        response = requests.request(
            req.get_method(), req.full_url,
            headers=dict(req.header_items()), data=req.data,
            proxy=('http://' + self.proxy) if self.proxy else None,
            impersonate='chrome', timeout=timeout, allow_redirects=False)
        if response.status_code >= 400:
            raise urllib.error.HTTPError(
                req.full_url, response.status_code, 'HTTP failure', {},
                io.BytesIO(response.content))
        result = _Response(response.content)
        result.status = response.status_code
        return result
