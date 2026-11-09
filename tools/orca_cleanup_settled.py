#!/usr/bin/env python3
"""一键清理 mc-agent 各子工作区已完成无后续任务的 Orca Worker、终端与左侧栏 agent-session 聊天标签页气泡。

用法：
    python tools/orca_cleanup_settled.py            # 释放已结束 Worker，并关闭所有非 working 的 agent-session 聊天标签页（保留右侧历史记录）
    python tools/orca_cleanup_settled.py --reset    # 全部 Worker 收口后重置 orchestration 计数列表
"""
import argparse
import json
import subprocess
import sys

ORCA_RUNTIME_CLIENT = "C:/Users/xxsx/AppData/Local/Programs/orca/resources/app.asar.unpacked/out/cli/runtime-client.js"
COORDINATOR_SESSION_ID = "codex_8c7f6553_47d7_4947_92a1_a4092637bbb4"

SUB_WORKTREES = [
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/earth_on_minecraft",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/xuanhuan_earth",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/fantasy_earth",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/earth_theology",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/earth_human",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/earth-series/earth_lore",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/automation/easy_autocrafting",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/automation/xxsx_builder",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/plantmagic/plantmagic_fixes_mod",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/plantmagic/plantmagic_translation_mod",
    "path:D:/AGENT/WORKSPACES/Projects/mc-agent/temple/mod-[虚无圣殿]Temple of Nihility",
]


def run_orca(args):
    try:
        res = subprocess.run(
            ["orca", *args, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
        data = json.loads(res.stdout)
        return data.get("result", data) if isinstance(data, dict) else data
    except Exception as e:
        return {"error": str(e)}


def close_settled_session_tabs():
    """通过 Orca 本地 RuntimeClient 调用 session.tabs.close 关闭所有已结束的 agent-session 标签页。"""
    node_script = f"""
const {{ RuntimeClient }} = require({json.dumps(ORCA_RUNTIME_CLIENT)});
(async () => {{
  const client = new RuntimeClient();
  const ps = await client.call('worktree.ps', {{}});
  let closedTabs = 0;
  const keptTabs = [];
  for (const w of (ps.result.worktrees || [])) {{
    const path = w.path || '';
    if (!path.includes('mc-agent') && !(w.worktreeId || '').includes('mc-agent')) continue;
    const wtSelector = 'id:' + w.worktreeId;
    const list = await client.call('session.tabs.list', {{ worktree: wtSelector }});
    const workingSids = new Set();
    for (const a of (w.agents || [])) {{
      if (a.state === 'working') {{
        const m = /^structured-agent-session-([^:]+)/.exec(a.paneKey || '');
        if (m) workingSids.add(m[1]);
      }}
    }}
    for (const t of (list.result.tabs || [])) {{
      if (t.type === 'agent-session') {{
        if (workingSids.has(t.sessionId) || t.sessionId === {json.dumps(COORDINATOR_SESSION_ID)}) {{
          keptTabs.push({{ repo: w.repo, tabId: t.id, title: t.title }});
          continue;
        }}
        await client.call('session.tabs.close', {{
          worktree: wtSelector,
          tabId: t.id,
          reason: 'user'
        }});
        closedTabs++;
      }}
    }}
  }}
  console.log(JSON.stringify({{ closedSessionTabs: closedTabs, keptActiveTabs: keptTabs }}));
}})().catch(e => {{
  console.log(JSON.stringify({{ error: String(e) }}));
  process.exit(0);
}});
"""
    try:
        res = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=25,
        )
        for line in reversed(res.stdout.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
        return {"raw": res.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset all orchestration workers when batch settles")
    args = parser.parse_args()

    wlist = run_orca(["orchestration", "worker-list"])
    workers = wlist.get("workers", []) if isinstance(wlist, dict) else []
    released = []
    active = []
    for w in workers:
        did = w.get("dispatchId") or w.get("workerId") or w.get("id")
        status = (w.get("state") or w.get("outcome") or w.get("status") or "").lower()
        tstate = (w.get("terminalState") or "").lower()
        if status in ("idle", "completed", "succeeded", "failed", "cancelled", "stopped", "done"):
            if tstate != "released":
                run_orca(["orchestration", "worker-release", "--dispatch", did])
                released.append(did)
        else:
            active.append((did, status))

    if args.reset and not active:
        run_orca(["orchestration", "reset", "--all"])

    closed_wt = 0
    for wt in SUB_WORKTREES:
        run_orca(["worktree", "set", "--worktree", wt, "--workspace-status", "completed", "--read", "--comment", ""])
        closed_wt += 1

    tab_result = close_settled_session_tabs()

    summary = {
        "releasedWorkers": released,
        "activeWorkersRemaining": active,
        "cleanedSubWorktrees": closed_wt,
        "sessionTabCleanup": tab_result,
        "resetAll": bool(args.reset and not active),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()