#!/usr/bin/env python3
"""Direct HTTP client for Blockbench MCP (http://localhost:3000/bb-mcp).
Works even when OpenCode's built-in MCP client disconnects after a Blockbench restart.
NOTE: Never call Blockbench.import(...) inside eval_js — it opens a native modal dialog and hangs!
Use load_bbmodel(path) and save_bbmodel(path) instead.
"""
import base64
import json
import os
import urllib.request
from typing import Any, Dict, Optional, Tuple

BB_MCP_URL = "http://localhost:3000/bb-mcp"
_SESSION_ID: Optional[str] = None


def _post(payload: Dict[str, Any], sid: Optional[str] = None, timeout: int = 30) -> Tuple[Dict[str, Any], Optional[str]]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if sid:
        headers["Mcp-Session-Id"] = sid
    req = urllib.request.Request(
        BB_MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body), resp.headers.get("Mcp-Session-Id")


def get_session(force_new: bool = False) -> str:
    global _SESSION_ID
    if _SESSION_ID and not force_new:
        return _SESSION_ID
    _, sid = _post({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "bb_mcp_client", "version": "1.0"},
        },
    })
    _SESSION_ID = sid
    return _SESSION_ID


def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None, timeout: int = 30) -> Dict[str, Any]:
    sid = get_session()
    try:
        res, _ = _post({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }, sid=sid, timeout=timeout)
    except Exception:
        sid = get_session(force_new=True)
        res, _ = _post({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }, sid=sid, timeout=timeout)
    return res


def eval_js(code: str, timeout: int = 30) -> Any:
    res = call_tool("risky_eval", {"code": code}, timeout=timeout)
    if "error" in res:
        raise RuntimeError(f"MCP error: {res['error']}")
    content = res.get("result", {}).get("content", [])
    if content and content[0].get("type") == "text":
        return content[0].get("text")
    return res


def load_bbmodel(path: str) -> Dict[str, Any]:
    """Safely load a .bbmodel file into Blockbench without opening a file dialog."""
    norm_path = os.path.abspath(path).replace("\\", "/")
    code = (
        "(() => {"
        "  const fs = requireNativeModule('fs');"
        f"  const p = {json.dumps(norm_path)};"
        "  const model = JSON.parse(fs.readFileSync(p, 'utf8'));"
        "  Codecs.project.load(model, {path: p});"
        "  return JSON.stringify({name: Project.name, cubes: Cube.all.length, groups: Group.all.length, textures: Texture.all.length, res: [Project.texture_width, Project.texture_height]});"
        "})()"
    )
    raw = eval_js(code)
    return json.loads(json.loads(raw)) if isinstance(raw, str) and raw.startswith('"') else json.loads(raw)


def save_bbmodel(path: str) -> str:
    """Safely compile and save the active Blockbench project to a .bbmodel path."""
    norm_path = os.path.abspath(path).replace("\\", "/")
    os.makedirs(os.path.dirname(norm_path), exist_ok=True)
    code = (
        "(() => {"
        "  const fs = requireNativeModule('fs');"
        f"  const p = {json.dumps(norm_path)};"
        "  const compiled = Codecs.project.compile();"
        "  fs.writeFileSync(p, compiled, 'utf8');"
        "  return p;"
        "})()"
    )
    return eval_js(code)


def save_screenshot(out_png_path: str, camera_angle: Optional[Dict[str, Any]] = None) -> str:
    """Optionally set camera angle and save a viewport screenshot PNG to disk."""
    if camera_angle:
        call_tool("set_camera_angle", camera_angle)
    res = call_tool("capture_screenshot", {})
    for item in res.get("result", {}).get("content", []):
        if item.get("type") == "image" and item.get("data"):
            os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
            with open(out_png_path, "wb") as f:
                f.write(base64.b64decode(item["data"]))
            return os.path.abspath(out_png_path)
    raise RuntimeError(f"Failed to capture screenshot: {res}")


def close_all_projects() -> Any:
    """Close all open projects in Blockbench cleanly without saving prompts."""
    code = (
        "(() => {"
        "  while (ModelProject.all.length > 0) {"
        "    const p = ModelProject.all[0];"
        "    p.saved = true;"
        "    p.close(true);"
        "  }"
        "  return ModelProject.all.length;"
        "})()"
    )
    return eval_js(code)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        print(eval_js(sys.argv[2]))
    elif len(sys.argv) > 1 and sys.argv[1] == "close":
        print(close_all_projects())
    else:
        print(call_tool("get_capabilities", {"include_tools": False}))
