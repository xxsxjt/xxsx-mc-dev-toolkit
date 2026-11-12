#!/usr/bin/env python3
"""Sub-agent model telemetry, playtest feedback ledger, and task-category model recommender.

Portable: uses the current working directory (or --root <workspace>) and stores
append-only JSONL records under runtime/model-telemetry.jsonl by default.
Contains zero hard-coded machine paths, API keys, or credentials.

Subcommands:
  python tools/model_telemetry.py harvest [--run <run_id>]
  python tools/model_telemetry.py record --dispatch ctx_xxx --model 247-gpt/gpt-6.1-sol --outcome succeeded
  python tools/model_telemetry.py feedback --score 4 --category pixel_art --repo xuanhuan_earth --note "..."
  python tools/model_telemetry.py recommend [--category pixel_art] [--json]
  python tools/model_telemetry.py stats [--category <cat>] [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

CATEGORIES: dict[str, tuple[str, tuple[str, ...]]] = {
    "pixel_art": (
        "2D 像素贴图/图标重绘/色阶与微饰层",
        ("pixel", "texture", "sprite", "icon", "palette", "tint", "贴图", "像素", "图标", "重绘", "色阶", "微饰"),
    ),
    "model_3d": (
        "3D 方块建模/分材质通道/UV 修复/多方块外观",
        ("3d", "uv", "block model", "models/block", "ber", "multiblock", "建模", "模型", "祭坛", "多方块"),
    ),
    "gui_screen": (
        "GUI 面板/Screen 布局/槽位与动态导轨",
        ("gui", "screen", "menu", "hud", "button", "tooltip", "界面", "面板", "公告板", "导轨"),
    ),
    "worldgen_gameplay": (
        "世界生成/聚落村民/核心玩法与状态机制",
        ("worldgen", "feature", "lode", "pebble", "villager", "settlement", "sanctum", "矿", "聚落", "村民", "牧师", "玩法"),
    ),
    "compat_arch": (
        "模组联动兼容/包架构规范化/双端隔离",
        ("compat", "curios", "occultism", "create", "ae2", "jei", "apothic", "架构", "兼容", "联动", "分包"),
    ),
    "docs_tooling": (
        "开发工具库/门禁脚本/共享规范与文档整理",
        ("toolkit", "playbook", "readme", "gate", "sync", "script", "doc", "工具", "手册", "门禁", "文档", "索引"),
    ),
}

# Default model pool with cost tier (1=low, 2=medium, 3=high, 99=banned) and prior suitability per category.
DEFAULT_MODEL_POOL: dict[str, dict[str, Any]] = {
    "AIGCPro-Gemini/gemini-4-carbon": {
        "costTier": 2,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 4.2,
            "model_3d": 4.4,
            "gui_screen": 4.4,
            "worldgen_gameplay": 4.3,
            "compat_arch": 4.2,
            "docs_tooling": 3.9,
        },
    },
    "247-gpt/gpt-6.1-sol": {
        "costTier": 1,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 4.1,
            "model_3d": 4.0,
            "gui_screen": 4.1,
            "worldgen_gameplay": 4.2,
            "compat_arch": 4.3,
            "docs_tooling": 4.3,
        },
    },
    "workbuddy-ai/deepseek-v4.1-flash-sg": {
        "costTier": 1,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 3.3,
            "model_3d": 3.4,
            "gui_screen": 3.5,
            "worldgen_gameplay": 3.7,
            "compat_arch": 4.0,
            "docs_tooling": 4.5,
        },
    },
    "247-kiro/claude-opus-5-5": {
        "costTier": 2,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 3.8,
            "model_3d": 3.9,
            "gui_screen": 4.0,
            "worldgen_gameplay": 4.1,
            "compat_arch": 4.2,
            "docs_tooling": 4.1,
        },
    },
    "hubway-claude/claude-sonnet-5-5": {
        "costTier": 2,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 3.9,
            "model_3d": 4.0,
            "gui_screen": 4.1,
            "worldgen_gameplay": 4.1,
            "compat_arch": 4.2,
            "docs_tooling": 4.1,
        },
    },
    "hubway-claude/claude-opus-5-5": {
        "costTier": 3,
        "defaultEffort": "high",
        "banned": False,
        "priors": {
            "pixel_art": 4.1,
            "model_3d": 4.3,
            "gui_screen": 4.3,
            "worldgen_gameplay": 4.5,
            "compat_arch": 4.5,
            "docs_tooling": 4.0,
        },
    },
    "AIGCPro-DeepSeek/kimi-k3.1-pro": {
        "costTier": 99,
        "defaultEffort": "high",
        "banned": True,
        "banReason": "retired_expensive",
        "priors": {},
    },
}


def utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_model_id(raw: str) -> str:
    val = (raw or "").strip()
    for prefix in ("codex/", "claude/", "opencode/", "opencode2/", "opencodex/"):
        if val.startswith(prefix):
            val = val[len(prefix):]
    return val or "unknown"


def infer_category(text: str) -> str:
    hay = (text or "").lower()
    best_cat = "worldgen_gameplay"
    best_hits = 0
    for cat, (_, keywords) in CATEGORIES.items():
        hits = sum(1 for kw in keywords if kw.lower() in hay)
        if hits > best_hits:
            best_hits = hits
            best_cat = cat
    return best_cat


def sanitize_repo_label(workspace_or_repo: str) -> str:
    raw = (workspace_or_repo or "").strip()
    if "::" in raw:
        raw = raw.split("::", 1)[-1]
    raw = raw.replace("\\", "/").rstrip("/")
    if not raw:
        return "unknown"
    parts = [p for p in raw.split("/") if p and ":" not in p]
    if len(parts) >= 2 and parts[-2] in ("earth-series", "automation", "plantmagic", "temple"):
        return f"{parts[-2]}/{parts[-1]}"
    return parts[-1] if parts else raw


def resolve_ledger_path(root: Path, explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit)
    env_override = os.environ.get("MC_MODEL_TELEMETRY_FILE", "").strip()
    if env_override:
        return Path(env_override)
    return root / "runtime" / "model-telemetry.jsonl"


def load_events(ledger: Path) -> list[dict[str, Any]]:
    if not ledger.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except json.JSONDecodeError:
            continue
    return events


def append_events(ledger: Path, new_events: list[dict[str, Any]]) -> None:
    if not new_events:
        return
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8", newline="\n") as fh:
        for ev in new_events:
            fh.write(json.dumps(ev, ensure_ascii=False) + "\n")


def run_orca_json(args: list[str]) -> Any:
    cmd = ["orca", *args, "--json"]
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if res.returncode != 0 and not res.stdout.strip():
            return None
        data = json.loads(res.stdout)
        return data.get("result", data) if isinstance(data, dict) else data
    except Exception:
        return None


def classify_error_kind(text: str) -> str | None:
    low = (text or "").lower()
    if not low:
        return None
    if "insufficient_user_quota" in low or "预扣费额度失败" in low or "403 forbidden" in low:
        return "quota_403"
    if "at capacity" in low or "429" in low or "rate limit" in low:
        return "capacity_429"
    if "stream disconnected" in low or "upstream_reset" in low or "connection closed" in low or "transport channel closed" in low:
        return "stream_disconnect"
    return "runtime_error"


def harvest_from_orca(ledger: Path, run_filter: str | None = None) -> dict[str, Any]:
    existing = load_events(ledger)
    recorded_keys: set[tuple[str, str]] = set()
    for ev in existing:
        if ev.get("event") == "dispatch":
            did = str(ev.get("dispatchId") or "")
            out = str(ev.get("outcome") or "")
            if did:
                recorded_keys.add((did, out))

    w_args = ["orchestration", "worker-list"]
    if run_filter:
        w_args.extend(["--run", run_filter])
    w_res = run_orca_json(w_args) or {}
    workers = w_res.get("workers", []) if isinstance(w_res, dict) else []

    t_res = run_orca_json(["orchestration", "task-list"]) or {}
    tasks_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(t_res, dict):
        for t in t_res.get("tasks", []) or []:
            if isinstance(t, dict) and t.get("id"):
                tasks_by_id[str(t["id"])] = t

    inbox_res = run_orca_json(["orchestration", "inbox"]) or {}
    done_by_dispatch: dict[str, dict[str, Any]] = {}
    err_by_dispatch: dict[str, str] = {}
    if isinstance(inbox_res, dict):
        for m in inbox_res.get("messages", []) or []:
            if not isinstance(m, dict):
                continue
            payload = m.get("payload") if isinstance(m.get("payload"), dict) else {}
            did = str(payload.get("dispatchId") or "")
            if not did:
                continue
            mtype = str(m.get("type") or "")
            subj_body = f"{m.get('subject', '')} {m.get('body', '')}"
            if mtype == "worker_done" and did not in done_by_dispatch:
                done_by_dispatch[did] = m
            elif mtype == "escalation" and did not in err_by_dispatch:
                err_by_dispatch[did] = subj_body

    new_events: list[dict[str, Any]] = []
    for w in workers:
        if not isinstance(w, dict):
            continue
        did = str(w.get("dispatchId") or "")
        if not did:
            continue
        state = str(w.get("state") or "").lower()
        raw_outcome = str(w.get("outcome") or "").lower()
        if state in ("ready", "starting", "running") or raw_outcome == "in_progress":
            continue
        outcome = "succeeded" if state == "succeeded" or raw_outcome == "succeeded" else (raw_outcome or state or "unknown")
        if (did, outcome) in recorded_keys:
            continue

        raw_agent_model = str(w.get("agent") or "")
        agent_name = raw_agent_model.split("/", 1)[0] if "/" in raw_agent_model else (raw_agent_model or "codex")
        model_id = normalize_model_id(raw_agent_model) if "/" in raw_agent_model else normalize_model_id(str(w.get("model") or ""))
        task_id = str(w.get("taskId") or "")
        task_info = tasks_by_id.get(task_id, {})
        done_msg = done_by_dispatch.get(did, {})
        title = str(task_info.get("title") or done_msg.get("subject") or "")
        repo_label = sanitize_repo_label(str(w.get("workspace") or ""))
        cat = infer_category(f"{title} {done_msg.get('body', '')} {repo_label}")
        err_kind = classify_error_kind(err_by_dispatch.get(did, "")) if outcome != "succeeded" else None

        ev: dict[str, Any] = {
            "ts": utc_iso(),
            "event": "dispatch",
            "runId": str(w.get("runId") or run_filter or t_res.get("runId") or ""),
            "dispatchId": did,
            "taskId": task_id,
            "repo": repo_label,
            "category": cat,
            "title": title[:160],
            "agent": agent_name,
            "model": model_id,
            "effort": str(w.get("effort") or "high"),
            "outcome": outcome,
            "gatePassed": True if outcome == "succeeded" else None,
            "errorKind": err_kind,
            "source": "orca_auto_harvest",
        }
        new_events.append(ev)
        recorded_keys.add((did, outcome))

    append_events(ledger, new_events)
    return {"harvested": len(new_events), "ledger": ledger.name, "events": new_events}


def merge_dispatch_stats(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Collapse duplicate dispatch entries (latest wins) and pair with feedback entries."""
    by_dispatch: dict[str, dict[str, Any]] = {}
    anon_dispatches: list[dict[str, Any]] = []
    feedbacks: list[dict[str, Any]] = []

    for ev in events:
        etype = ev.get("event")
        if etype == "dispatch":
            did = str(ev.get("dispatchId") or "").strip()
            if did:
                prev = by_dispatch.get(did, {})
                merged = {**prev, **ev}
                if prev.get("model") and prev.get("model") != "unknown" and merged.get("model") == "unknown":
                    merged["model"] = prev["model"]
                by_dispatch[did] = merged
            else:
                anon_dispatches.append(ev)
        elif etype == "feedback":
            feedbacks.append(ev)

    dispatches = list(by_dispatch.values()) + anon_dispatches
    return dispatches, feedbacks


def compute_scores(events: list[dict[str, Any]], category_filter: str | None = None) -> dict[str, Any]:
    dispatches, feedbacks = merge_dispatch_stats(events)
    by_did = {str(d.get("dispatchId")): d for d in dispatches if d.get("dispatchId")}
    stats: dict[str, dict[str, Any]] = {}

    def ensure_model(mid: str) -> dict[str, Any]:
        mid = normalize_model_id(mid)
        if mid not in stats:
            pool_meta = DEFAULT_MODEL_POOL.get(mid, {})
            stats[mid] = {
                "model": mid,
                "costTier": pool_meta.get("costTier", 2),
                "defaultEffort": pool_meta.get("defaultEffort", "high"),
                "banned": bool(pool_meta.get("banned", False)),
                "banReason": pool_meta.get("banReason"),
                "attempts": 0,
                "succeeded": 0,
                "failed": 0,
                "infraTransient": 0,
                "streamDisconnects": 0,
                "gatePassed": 0,
                "feedbackScores": [],
                "feedbackNotes": [],
                "byCategory": {},
            }
        return stats[mid]

    for mid in DEFAULT_MODEL_POOL:
        ensure_model(mid)

    for d in dispatches:
        cat = str(d.get("category") or "worldgen_gameplay")
        if category_filter and cat != category_filter:
            continue
        mid = normalize_model_id(str(d.get("model") or "unknown"))
        if mid == "unknown":
            continue
        row = ensure_model(mid)
        cat_row = row["byCategory"].setdefault(
            cat, {"attempts": 0, "succeeded": 0, "failed": 0, "streamDisconnects": 0, "feedbackScores": []}
        )

        outcome = str(d.get("outcome") or "").lower()
        err_kind = str(d.get("errorKind") or "")

        if err_kind in ("quota_403", "capacity_429"):
            row["infraTransient"] += 1
            continue

        row["attempts"] += 1
        cat_row["attempts"] += 1
        if outcome == "succeeded":
            row["succeeded"] += 1
            cat_row["succeeded"] += 1
            if d.get("gatePassed") is not False:
                row["gatePassed"] += 1
        else:
            row["failed"] += 1
            cat_row["failed"] += 1
            if err_kind == "stream_disconnect":
                row["streamDisconnects"] += 1
                cat_row["streamDisconnects"] += 1

    for fb in feedbacks:
        score_val = fb.get("score")
        if not isinstance(score_val, (int, float)):
            continue
        score_f = max(1.0, min(5.0, float(score_val)))
        did = str(fb.get("dispatchId") or "")
        linked = by_did.get(did) if did else None

        cat = str(fb.get("category") or (linked.get("category") if linked else "") or "worldgen_gameplay")
        if category_filter and cat != category_filter:
            continue

        mid = normalize_model_id(str(fb.get("model") or (linked.get("model") if linked else "")))
        if mid == "unknown" and fb.get("repo"):
            target_repo = sanitize_repo_label(str(fb["repo"]))
            candidates = [
                d for d in reversed(dispatches)
                if sanitize_repo_label(str(d.get("repo") or "")) == target_repo
                and d.get("outcome") == "succeeded"
                and (not fb.get("category") or d.get("category") == cat)
            ]
            if candidates:
                mid = normalize_model_id(str(candidates[0].get("model") or "unknown"))
        if mid == "unknown":
            continue

        row = ensure_model(mid)
        row["feedbackScores"].append(score_f)
        if fb.get("note"):
            row["feedbackNotes"].append({"score": score_f, "category": cat, "note": str(fb["note"])[:120]})
        cat_row = row["byCategory"].setdefault(
            cat, {"attempts": 0, "succeeded": 0, "failed": 0, "streamDisconnects": 0, "feedbackScores": []}
        )
        cat_row["feedbackScores"].append(score_f)

    rankings: list[dict[str, Any]] = []
    target_cat = category_filter or "worldgen_gameplay"
    for mid, row in stats.items():
        pool_meta = DEFAULT_MODEL_POOL.get(mid, {})
        prior = float((pool_meta.get("priors") or {}).get(target_cat, 3.8))

        att = row["attempts"]
        succ = row["succeeded"]
        pass_rate = (succ / att) if att > 0 else None
        fb_list = row["feedbackScores"]
        avg_fb = (sum(fb_list) / len(fb_list)) if fb_list else None

        num = prior * 2.0
        den = 2.0
        if pass_rate is not None:
            num += (1.0 + 4.0 * pass_rate) * min(att, 6)
            den += min(att, 6)
        if avg_fb is not None:
            w_fb = 2.5 * min(len(fb_list), 6)
            num += avg_fb * w_fb
            den += w_fb

        raw_score = num / den
        cost_penalty = max(0, int(row["costTier"]) - 1) * 0.12
        disconnect_penalty = min(0.45, row["streamDisconnects"] * 0.15)
        composite = round(raw_score - cost_penalty - disconnect_penalty, 3)

        rankings.append(
            {
                "model": mid,
                "banned": row["banned"],
                "banReason": row["banReason"],
                "costTier": row["costTier"],
                "defaultEffort": row["defaultEffort"],
                "attempts": att,
                "succeeded": succ,
                "failed": row["failed"],
                "infraTransient": row["infraTransient"],
                "streamDisconnects": row["streamDisconnects"],
                "passRate": round(pass_rate, 3) if pass_rate is not None else None,
                "feedbackCount": len(fb_list),
                "avgFeedback": round(avg_fb, 2) if avg_fb is not None else None,
                "compositeScore": -99.0 if row["banned"] else composite,
                "recentNotes": row["feedbackNotes"][-3:],
            }
        )

    rankings.sort(key=lambda r: (not r["banned"], r["compositeScore"], r["feedbackCount"], r["succeeded"]), reverse=True)
    eligible = [r for r in rankings if not r["banned"]]
    return {
        "category": category_filter,
        "categoryLabel": CATEGORIES.get(category_filter or "", ("全类别综合", ()))[0],
        "primary": eligible[0] if eligible else None,
        "fallback": eligible[1] if len(eligible) > 1 else None,
        "rankings": rankings,
        "totalDispatches": len(dispatches),
        "totalFeedbacks": len(feedbacks),
    }


def cmd_record(args: argparse.Namespace, ledger: Path) -> int:
    cat = args.category or infer_category(f"{args.title or ''} {args.repo or ''}")
    ev: dict[str, Any] = {
        "ts": utc_iso(),
        "event": "dispatch",
        "runId": args.run_id or "",
        "dispatchId": args.dispatch or "",
        "taskId": args.task_id or "",
        "repo": sanitize_repo_label(args.repo or ""),
        "category": cat,
        "title": (args.title or "")[:160],
        "agent": args.agent,
        "model": normalize_model_id(args.model),
        "effort": args.effort,
        "outcome": args.outcome,
        "gatePassed": None if args.gate_passed is None else (args.gate_passed == "true"),
        "errorKind": args.error_kind or None,
        "durationSec": args.duration_sec,
        "note": (args.note or "")[:200] or None,
        "source": "manual_or_hook",
    }
    append_events(ledger, [ev])
    print(json.dumps({"recorded": ev, "ledger": str(ledger.name)}, ensure_ascii=False))
    return 0


def cmd_feedback(args: argparse.Namespace, ledger: Path) -> int:
    ev: dict[str, Any] = {
        "ts": utc_iso(),
        "event": "feedback",
        "dispatchId": args.dispatch or None,
        "repo": sanitize_repo_label(args.repo) if args.repo else None,
        "category": args.category or (infer_category(args.note or "") if args.note else None),
        "model": normalize_model_id(args.model) if args.model else None,
        "score": float(args.score),
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "note": (args.note or "").strip()[:240],
    }
    append_events(ledger, [ev])
    rec = compute_scores(load_events(ledger), category_filter=ev.get("category"))
    print(
        json.dumps(
            {
                "recordedFeedback": ev,
                "updatedRecommendation": {
                    "category": ev.get("category"),
                    "primary": rec["primary"]["model"] if rec["primary"] else None,
                    "fallback": rec["fallback"]["model"] if rec["fallback"] else None,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_recommend(args: argparse.Namespace, ledger: Path) -> int:
    events = load_events(ledger)
    categories_to_show = [args.category] if args.category else list(CATEGORIES.keys())
    results = {cat: compute_scores(events, category_filter=cat) for cat in categories_to_show}
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    print(f"=== 子会话模型自动推荐表 (样本: {len(events)} 条记录) ===")
    for cat in categories_to_show:
        res = results[cat]
        pri = res["primary"]
        fb = res["fallback"]
        if not pri:
            continue
        p_fb_str = f", 实测均分={pri['avgFeedback']}/5({pri['feedbackCount']})" if pri["avgFeedback"] is not None else ""
        p_pr_str = f", 通过率={int(pri['passRate']*100)}%({pri['succeeded']}/{pri['attempts']})" if pri["passRate"] is not None else ""
        fb_str = f"{fb['model']} (score={fb['compositeScore']})" if fb else "none"
        print(
            f"  [{cat:17s}] {res['categoryLabel']}\n"
            f"    -> 首选: {pri['model']} --effort {pri['defaultEffort']} "
            f"[综合={pri['compositeScore']}, 成本T{pri['costTier']}{p_pr_str}{p_fb_str}]\n"
            f"    -> 备选: {fb_str}"
        )
    return 0


def cmd_stats(args: argparse.Namespace, ledger: Path) -> int:
    events = load_events(ledger)
    res = compute_scores(events, category_filter=args.category)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    scope_title = f"{args.category} ({res['categoryLabel']})" if args.category else "全类别汇总"
    print(
        f"=== 子会话模型表现与反馈看板 [{scope_title}] "
        f"(派发记录={res['totalDispatches']}, 玩家反馈={res['totalFeedbacks']}) ==="
    )
    for r in res["rankings"]:
        status_tag = "BANNED" if r["banned"] else f"T{r['costTier']}    "
        pr = f"{int(r['passRate']*100):3d}% ({r['succeeded']}/{r['attempts']})" if r["passRate"] is not None else "  -  (0/0)"
        fb = f"{r['avgFeedback']:.2f}/5 (n={r['feedbackCount']})" if r["avgFeedback"] is not None else "   -   (n=0)"
        disc = f" disc={r['streamDisconnects']}" if r["streamDisconnects"] else ""
        infra = f" 403/429={r['infraTransient']}" if r["infraTransient"] else ""
        print(
            f"  [{status_tag}] {r['model']:38s} | 综合={r['compositeScore']:6.3f} | "
            f"成功率={pr} | 反馈={fb}{disc}{infra}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sub-agent model telemetry & playtest-feedback recommender.")
    p.add_argument("--root", default=".", help="workspace root directory (default: current directory)")
    p.add_argument("--ledger", default=None, help="override path to model-telemetry.jsonl")
    sub = p.add_subparsers(dest="cmd")

    p_harv = sub.add_parser("harvest", help="auto-harvest settled Orca worker dispatches into ledger")
    p_harv.add_argument("--run", dest="run_id", default=None, help="optional Orca Run ID")

    p_rec = sub.add_parser("record", help="record a worker dispatch result explicitly")
    p_rec.add_argument("--dispatch", default="", help="Orca dispatchId (e.g. ctx_xxx)")
    p_rec.add_argument("--run", dest="run_id", default="", help="Orca runId")
    p_rec.add_argument("--task", dest="task_id", default="", help="Orca taskId")
    p_rec.add_argument("--repo", default="", help="target sub-repository name")
    p_rec.add_argument("--category", choices=list(CATEGORIES.keys()), default=None)
    p_rec.add_argument("--title", default="", help="short task summary")
    p_rec.add_argument("--agent", default="codex")
    p_rec.add_argument("--model", required=True, help="provider/model identifier")
    p_rec.add_argument("--effort", default="high")
    p_rec.add_argument("--outcome", choices=["succeeded", "failed", "stopped", "interrupted"], required=True)
    p_rec.add_argument("--gate-passed", choices=["true", "false"], default=None)
    p_rec.add_argument("--error-kind", default="", help="quota_403 | capacity_429 | stream_disconnect | gate_fail | runtime_error")
    p_rec.add_argument("--duration-sec", type=int, default=None)
    p_rec.add_argument("--note", default="")

    p_fb = sub.add_parser("feedback", help="record user playtest/review score (1..5) to tune future model selection")
    p_fb.add_argument("--score", type=float, required=True, help="user rating from 1 (bad/redo) to 5 (great)")
    p_fb.add_argument("--dispatch", default=None, help="specific dispatchId if known")
    p_fb.add_argument("--repo", default=None, help="repo whose latest succeeded dispatch receives this feedback")
    p_fb.add_argument("--category", choices=list(CATEGORIES.keys()), default=None, help="task category")
    p_fb.add_argument("--model", default=None, help="explicit model id if not linked via dispatch/repo")
    p_fb.add_argument("--tags", default="", help="comma-separated tags, e.g. palette,uv,ui_clean")
    p_fb.add_argument("--note", default="", help="concise summary of user feedback")

    p_recom = sub.add_parser("recommend", help="recommend primary + fallback model for a task category")
    p_recom.add_argument("--category", choices=list(CATEGORIES.keys()), default=None)
    p_recom.add_argument("--json", action="store_true")

    p_st = sub.add_parser("stats", help="display model telemetry & feedback leaderboard")
    p_st.add_argument("--category", choices=list(CATEGORIES.keys()), default=None)
    p_st.add_argument("--json", action="store_true")
    return p


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()
    ledger = resolve_ledger_path(root, args.ledger)
    cmd = args.cmd or "recommend"

    if cmd == "harvest":
        out = harvest_from_orca(ledger, run_filter=args.run_id)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if cmd == "record":
        return cmd_record(args, ledger)
    if cmd == "feedback":
        return cmd_feedback(args, ledger)
    if cmd == "recommend":
        return cmd_recommend(args, ledger)
    if cmd == "stats":
        return cmd_stats(args, ledger)
    return 1


if __name__ == "__main__":
    sys.exit(main())
