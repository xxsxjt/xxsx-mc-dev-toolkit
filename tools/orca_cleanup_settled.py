#!/usr/bin/env python3
"""Release settled Orca workers and close stale agent-session tabs for a worktree set.

Portable: no machine-specific paths. Supply the Orca RuntimeClient module path and
the worktree selectors explicitly, or via environment variables.

Usage:
    python tools/orca_cleanup_settled.py \
        --runtime-client <path/to/orca/runtime-client.js> \
        --worktree path:<repo-a> --worktree path:<repo-b>

    # or set them in the environment
    ORCA_RUNTIME_CLIENT=<path> ORCA_WORKTREES="<repo-a>;<repo-b>" \
        python tools/orca_cleanup_settled.py

    python tools/orca_cleanup_settled.py --reset     # also reset counts once all workers settle
"""
import argparse
import json
import os
import subprocess
import sys

DEFAULT_RUNTIME_CLIENT = os.environ.get("ORCA_RUNTIME_CLIENT", "")
DEFAULT_WORKTREES = [
    item.strip()
    for item in os.environ.get("ORCA_WORKTREES", "").split(";")
    if item.strip()
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


def close_settled_session_tabs(runtime_client, coordinator_session, worktree_needle):
    """Close every non-working agent-session tab via Orca's local RuntimeClient."""
    node_script = f"""
const {{ RuntimeClient }} = require({json.dumps(runtime_client)});
(async () => {{
  const client = new RuntimeClient();
  const ps = await client.call('worktree.ps', {{}});
  let closedTabs = 0;
  const keptTabs = [];
  for (const w of (ps.result.worktrees || [])) {{
    const path = w.path || '';
    if ({json.dumps(worktree_needle)} && !path.includes({json.dumps(worktree_needle)}) && !(w.worktreeId || '').includes({json.dumps(worktree_needle)})) continue;
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
        if (workingSids.has(t.sessionId) || t.sessionId === {json.dumps(coordinator_session)}) {{
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
    parser = argparse.ArgumentParser(description="Release settled Orca workers and stale session tabs.")
    parser.add_argument(
        "--runtime-client",
        default=DEFAULT_RUNTIME_CLIENT,
        help="path to Orca's runtime-client.js (or set ORCA_RUNTIME_CLIENT)",
    )
    parser.add_argument(
        "--worktree",
        action="append",
        default=None,
        help="worktree selector or repo path substring, repeatable (or set ORCA_WORKTREES='a;b')",
    )
    parser.add_argument(
        "--coordinator-session",
        default=os.environ.get("ORCA_COORDINATOR_SESSION", ""),
        help="session id whose chat tab must be kept open (or set ORCA_COORDINATOR_SESSION)",
    )
    parser.add_argument("--reset", action="store_true", help="reset all orchestration workers once settled")
    args = parser.parse_args()

    worktrees = args.worktree if args.worktree else DEFAULT_WORKTREES

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

    cleaned = 0
    for wt in worktrees:
        selector = wt if wt.startswith(("path:", "id:")) else f"path:{wt}"
        run_orca(["worktree", "set", "--worktree", selector, "--workspace-status", "completed",
                  "--read", "--comment", ""])
        cleaned += 1

    if args.runtime_client:
        needle = worktrees[0].split("path:", 1)[-1] if worktrees else ""
        tab_result = close_settled_session_tabs(args.runtime_client, args.coordinator_session, needle)
    else:
        tab_result = {"skipped": "no --runtime-client / ORCA_RUNTIME_CLIENT provided"}

    summary = {
        "releasedWorkers": released,
        "activeWorkersRemaining": active,
        "cleanedWorktrees": cleaned,
        "sessionTabCleanup": tab_result,
        "resetAll": bool(args.reset and not active),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

