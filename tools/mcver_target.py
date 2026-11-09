#!/usr/bin/env python3
"""Add or refresh a multi-version target for a mod repository.

Usage:
    python tools/mcver_target.py <repo> --name neoforge-26.3 \
        --mc 26.3 --loader neoforge --loader-version 26.3.0.1 \
        --java 25 --moddev 2.0.148 --modid example_mod

Copies the closest existing target as a template, rewrites the version
strings, and leaves the source tree untouched. The new target is written
with a `.mcver-target.json` marker so `mcver audit` can report it.

This tool never edits an existing target's source; it only creates a new
target directory or refreshes the marker.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

TARGET_DIR_RE = re.compile(r"^(neoforge|forge)-(.+)$")


def read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return ""


def detect_loader(build: Path) -> tuple[str, str]:
    text = read_text(build)
    m = re.search(r"neoForge\s*\{.*?version\s*=\s*['\"]([^'\"]+)['\"]", text, re.S)
    if m:
        return "neoforge", m.group(1)
    m = re.search(r"minecraft(?:\.dependency)?\s*\(?\s*['\"]net\.minecraftforge:forge:([^'\"]+)['\"]", text)
    if m:
        return "forge", m.group(1)
    m = re.search(r"forgeVersion\s*=\s*project\.findProperty\('forgeVersion'\)\s*\?:\s*'([^']+)'", text)
    if m:
        return "forge", m.group(1)
    return "", ""


def find_template(repo: Path, loader: str) -> Path | None:
    candidates: list[tuple[str, Path]] = []
    for child in repo.iterdir():
        if not child.is_dir():
            continue
        m = TARGET_DIR_RE.match(child.name)
        if not m or m.group(1) != loader:
            continue
        build = child / "build.gradle"
        if not build.exists():
            continue
        _, ver = detect_loader(build)
        if ver:
            candidates.append((ver, child))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]


def rewrite(text: str, mapping: dict[str, str]) -> str:
    # Longest keys first so "26.2.0.7-beta" is replaced before "26.2".
    for old in sorted(mapping, key=len, reverse=True):
        new = mapping[old]
        if old and new and old != new:
            text = text.replace(old, new)
    return text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mcver_target", description=__doc__)
    p.add_argument("repo", help="mod repository root")
    p.add_argument("--name", required=True, help="new target directory name, e.g. neoforge-26.3")
    p.add_argument("--mc", required=True, help="Minecraft version, e.g. 26.3")
    p.add_argument("--loader", choices=("neoforge", "forge"), required=True)
    p.add_argument("--loader-version", required=True)
    p.add_argument("--java", default="25")
    p.add_argument("--moddev", default="")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"repo not found: {repo}")
        return 1

    dest = repo / args.name
    if dest.exists():
        print(f"target already exists: {dest}")
        return 1

    template = find_template(repo, args.loader)
    if template is None:
        print(f"no {args.loader} target to use as template")
        return 1

    _, old_loader_ver = detect_loader(template / "build.gradle")
    old_mc = ""
    m = TARGET_DIR_RE.match(template.name)
    if m:
        old_mc = m.group(2)

    mapping: dict[str, str] = {template.name: args.name}
    if old_loader_ver and old_loader_ver != args.loader_version:
        mapping[old_loader_ver] = args.loader_version
    if old_mc and old_mc != args.mc:
        mapping[old_mc] = args.mc
    if args.moddev:
        for old in re.findall(r"moddev'\s*version\s*'([^']+)'", read_text(template / "build.gradle")):
            if old != args.moddev:
                mapping[old] = args.moddev

    print(f"template: {template.name} ({old_loader_ver})")
    print(f"new:      {args.name} (mc {args.mc}, {args.loader} {args.loader_version}, java {args.java})")

    if args.dry_run:
        for old, new in mapping.items():
            if old and old != new:
                print(f"  replace {old!r} -> {new!r}")
        return 0

    shutil.copytree(
        template,
        dest,
        ignore=shutil.ignore_patterns("build", ".gradle", "run", "runs", "*.log"),
    )

    build = dest / "build.gradle"
    text = rewrite(read_text(build), mapping)
    text = re.sub(r"JavaLanguageVersion\.of\(\d+\)", f"JavaLanguageVersion.of({args.java})", text)
    build.write_text(text, encoding="utf-8")

    # Keep mod metadata in sync with the new target.
    for toml in dest.rglob("META-INF/*mods.toml"):
        raw = read_text(toml)
        updated = rewrite(raw, mapping)
        if args.loader == "neoforge":
            updated = re.sub(
                r'(modId\s*=\s*"neoforge"\s*\n\s*type\s*=\s*"[^"]*"\s*\n\s*versionRange\s*=\s*)"[^"]*"',
                rf'\g<1>"[{args.loader_version},)"',
                updated,
            )
            updated = re.sub(
                r'(modId\s*=\s*"minecraft"\s*\n\s*type\s*=\s*"[^"]*"\s*\n\s*versionRange\s*=\s*)"[^"]*"',
                rf'\g<1>"[{args.mc}]"',
                updated,
            )
        if updated != raw:
            toml.write_text(updated, encoding="utf-8")

    marker = {
        "mc": args.mc,
        "loader": args.loader,
        "loaderVersion": args.loader_version,
        "java": args.java,
        "template": template.name,
    }
    (dest / ".mcver-target.json").write_text(
        json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"created {dest}")
    print("next: review build.gradle, update neoforge.mods.toml versionRange, then build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
