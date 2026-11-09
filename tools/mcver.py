#!/usr/bin/env python3
"""mcver - Minecraft mod multi-version workspace auditor.

Subcommands:
    audit     Scan mod repositories and report build configuration.
    jars      Validate built JARs: split packages, modId consistency.
    matrix    Print MC version x loader x mod support matrix.
    doctor    Check a game instance: loader version, mod dependencies, conflicts.

Stdlib only. Read-only: this tool never modifies any file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

MOD_ROOTS = ("earth-series", "automation", "plantmagic", "temple", "temp")
SKIP_DIR_NAMES = {
    "build", ".gradle", ".git", "backups", "_backups", "tmp", "temp",
    "node_modules", "run", "runs", "release-assets", "_incoming-20261018",
}
SKIP_PREFIXES = ("_backup", "_tmp", "backup", "_old", "old-", "temp")

VERSION_RE = re.compile(r"(?m)^\s*version\s*=\s*'([^']+)'")
ARCHIVE_RE = re.compile(r"archiveBaseName\s*=\s*'([^']+)'")
ARCHIVE_NAME_RE = re.compile(r"base\.archivesName\s*=\s*'([^']+)'")
NEOFORGE_RE = re.compile(r"neoForge\s*\{.*?version\s*=\s*['\"]([^'\"]+)['\"]", re.S)
FORGE_RE = re.compile(r"minecraft(?:\.dependency)?\s*\(?\s*['\"]net\.minecraftforge:forge:([^'\"]+)['\"]")
FORGE_VAR_RE = re.compile(r"forgeVersion\s*=\s*project\.findProperty\('forgeVersion'\)\s*\?:\s*'([^']+)'")
MODDEV_RE = re.compile(r"moddev'\s*version\s*'([^']+)'")
JAVA_RE = re.compile(r"JavaLanguageVersion\.of\((\d+)\)")
WRAPPER_RE = re.compile(r"gradle-([0-9][^-]*(?:-[a-z0-9]+)?)-bin\.zip")

MODID_CONST_RE = re.compile(r'(?:MODID|MOD_ID)\s*=\s*"([^"]+)"')
MOD_LITERAL_RE = re.compile(r'@Mod\s*\(\s*(?:value\s*=\s*)?"([^"]+)"')

VERSION_TOKEN_RE = re.compile(r"^(\d+(?:\.\d+)*)(?:[-.]?([A-Za-z][\w.\-]*))?$")
QUALIFIER_RANK = (
    ("alpha", 1), ("beta", 2), ("milestone", 3), ("rc", 4), ("snapshot", 5),
)

METADATA_NAMES = ("META-INF/neoforge.mods.toml", "META-INF/mods.toml")


@dataclass
class Target:
    repo: str
    module: str
    path: Path
    mod_version: str = ""
    archive_name: str = ""
    loader: str = ""
    loader_version: str = ""
    moddev: str = ""
    java: str = ""
    gradle: str = ""


@dataclass
class JarInfo:
    path: Path
    mod_id: str = ""
    mod_version: str = ""
    loader_range: str = ""
    mc_range: str = ""
    packages: set[str] = field(default_factory=set)
    mods: list[tuple[str, str]] = field(default_factory=list)
    deps: list[tuple[str, str, bool, str]] = field(default_factory=list)
    bundled: dict[str, str] = field(default_factory=dict)
    error: str = ""


def say(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", "replace").decode("utf-8", "replace"))


# --------------------------------------------------------------------------
# version handling
# --------------------------------------------------------------------------

def parse_version(value: str) -> tuple[list[int], str]:
    text = (value or "").strip()
    # Build metadata ("+26.2") does not affect ordering; a trailing "-" is an open upper bound.
    text = text.split("+", 1)[0].rstrip("-")
    match = VERSION_TOKEN_RE.match(text)
    if not match:
        return [], text.lower()
    numbers = [int(part) for part in match.group(1).split(".")]
    return numbers, (match.group(2) or "").lower()


def qualifier_rank(qualifier: str) -> int:
    if not qualifier:
        return 99
    for name, rank in QUALIFIER_RANK:
        if qualifier.startswith(name):
            return rank
    return 6


def compare_versions(left: str, right: str) -> int:
    left_numbers, left_qualifier = parse_version(left)
    right_numbers, right_qualifier = parse_version(right)
    width = max(len(left_numbers), len(right_numbers))
    for index in range(width):
        a = left_numbers[index] if index < len(left_numbers) else 0
        b = right_numbers[index] if index < len(right_numbers) else 0
        if a != b:
            return -1 if a < b else 1
    left_rank = qualifier_rank(left_qualifier)
    right_rank = qualifier_rank(right_qualifier)
    if left_rank != right_rank:
        return -1 if left_rank < right_rank else 1
    if left_qualifier == right_qualifier:
        return 0
    return -1 if left_qualifier < right_qualifier else 1


def parse_range(spec: str) -> list[tuple[str | None, bool, str | None, bool]] | None:
    """Parse a Maven-style version range.

    NeoForge accepts comma-separated alternates such as "[26.1],[26.1.1]" and
    open-ended bounds such as "[26.1.2.10-beta,26.2-)". Returns one or more
    (low, low_inclusive, high, high_inclusive) tuples, or None for "any".
    """
    text = (spec or "").strip()
    if not text or text == "*":
        return None
    if not (text.startswith("[") or text.startswith("(")):
        return None

    alternates: list[str] = []
    depth = 0
    current = ""
    for char in text:
        if char in "[(":
            if depth == 0 and current.strip():
                alternates.append(current.strip())
                current = ""
            depth += 1
            current += char
        elif char in "])":
            depth -= 1
            current += char
            if depth == 0:
                alternates.append(current.strip())
                current = ""
        else:
            current += char
    if current.strip():
        alternates.append(current.strip())

    ranges: list[tuple[str | None, bool, str | None, bool]] = []
    for item in alternates:
        if len(item) < 2:
            continue
        low_inclusive = item[0] == "["
        high_inclusive = item[-1] == "]"
        body = item[1:-1]
        if "," not in body:
            exact = body.strip()
            ranges.append((exact, True, exact, True))
            continue
        low, high = body.split(",", 1)
        low = low.strip().rstrip("-")
        high = high.strip().rstrip("-")
        ranges.append((low or None, low_inclusive, high or None, high_inclusive))
    return ranges or None


def satisfies(version: str, spec: str) -> bool:
    ranges = parse_range(spec)
    if ranges is None:
        return True
    for low, low_inclusive, high, high_inclusive in ranges:
        ok = True
        if low:
            result = compare_versions(version, low)
            if result < 0 or (result == 0 and not low_inclusive):
                ok = False
        if ok and high:
            result = compare_versions(version, high)
            if result > 0 or (result == 0 and not high_inclusive):
                ok = False
        if ok:
            return True
    return False


# --------------------------------------------------------------------------
# gradle discovery
# --------------------------------------------------------------------------

def is_skipped(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIR_NAMES:
            return True
        low = part.lower()
        if any(low.startswith(prefix) for prefix in SKIP_PREFIXES):
            return True
    return False


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    for encoding in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return ""


def gradle_version(module_dir: Path) -> str:
    props = module_dir / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if not props.exists():
        return ""
    match = WRAPPER_RE.search(read_text(props))
    return match.group(1) if match else ""


def parse_target(build_file: Path, repo: str) -> Target:
    text = read_text(build_file)
    module_dir = build_file.parent
    target = Target(repo=repo, module=module_dir.name, path=module_dir)

    match = VERSION_RE.search(text)
    target.mod_version = match.group(1) if match else ""
    if not target.mod_version:
        parent_build = build_file.parent.parent / "build.gradle"
        if parent_build.exists():
            parent_match = re.search(r"version\s*=\s*'([^']+)'", read_text(parent_build))
            if parent_match:
                target.mod_version = parent_match.group(1) + " (inherited)"

    match = ARCHIVE_NAME_RE.search(text) or ARCHIVE_RE.search(text)
    target.archive_name = match.group(1) if match else ""

    match = NEOFORGE_RE.search(text)
    if match:
        target.loader = "neoforge"
        target.loader_version = match.group(1)
    else:
        match = FORGE_RE.search(text)
        if match:
            target.loader = "forge"
            target.loader_version = match.group(1).split("-", 1)[-1]
        else:
            match = FORGE_VAR_RE.search(text)
            if match:
                target.loader = "forge"
                target.loader_version = match.group(1) + " (default)"

    match = MODDEV_RE.search(text)
    target.moddev = match.group(1) if match else ""

    match = JAVA_RE.search(text)
    target.java = match.group(1) if match else ""

    target.gradle = gradle_version(module_dir)

    marker = module_dir / ".mcver-target.json"
    if marker.is_file():
        try:
            data = json.loads(read_text(marker))
            target.mod_version = target.mod_version or str(data.get("version", ""))
            target.loader = target.loader or str(data.get("loader", ""))
            target.loader_version = target.loader_version or str(data.get("loaderVersion", ""))
            target.java = target.java or str(data.get("java", ""))
        except (ValueError, OSError):
            pass

    return target


def discover_targets(root: Path) -> list[Target]:
    targets: list[Target] = []
    for root_name in MOD_ROOTS:
        base = root / root_name
        if not base.is_dir():
            continue
        for build_file in sorted(base.rglob("build.gradle")):
            rel = build_file.relative_to(root)
            if is_skipped(rel):
                continue
            repo = str(Path(*rel.parts[:2]))
            targets.append(parse_target(build_file, repo))
    return targets


def is_aggregate(target: Target) -> bool:
    return (
        target.module in ("common", "engine")
        or "common" in target.module
        or (target.path / "settings.gradle").exists()
        or (target.path / "settings.gradle.kts").exists()
    )


def cmd_audit(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    targets = discover_targets(root)
    if not targets:
        say("no build.gradle found")
        return 1

    if args.json:
        payload = []
        for target in targets:
            item = dict(target.__dict__)
            item["path"] = str(target.path)
            payload.append(item)
        say(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    say(f"{'repo':<44} {'module':<22} {'mod':<16} {'loader':<20} {'java':<4} {'gradle'}")
    say("-" * 130)
    for target in sorted(targets, key=lambda item: (item.repo, item.module)):
        loader = f"{target.loader} {target.loader_version}".strip()
        say(f"{target.repo:<44} {target.module:<22} {target.mod_version:<16} "
            f"{loader:<20} {target.java:<4} {target.gradle}")

    problems: list[str] = []
    seen: dict[str, set[str]] = {}
    for target in targets:
        aggregate = is_aggregate(target)
        if not aggregate:
            key = f"{target.repo}:{target.archive_name or target.module}"
            seen.setdefault(key, set()).add(target.loader_version)
            if not target.mod_version:
                problems.append(f"{target.repo}/{target.module}: missing version")
            if not target.loader:
                problems.append(f"{target.repo}/{target.module}: no loader block found")
        if not target.java and not aggregate:
            problems.append(f"{target.repo}/{target.module}: no java toolchain")
    for key, versions in seen.items():
        if len(versions) > 1:
            problems.append(f"{key}: multiple loader versions {sorted(versions)}")

    if problems:
        say("")
        say("problems:")
        for problem in problems:
            say(f"  - {problem}")
        return 1
    say("")
    say(f"ok: {len(targets)} targets")
    return 0


# --------------------------------------------------------------------------
# jar inspection
# --------------------------------------------------------------------------

def jar_metadata(zf: zipfile.ZipFile) -> tuple[str, str, str, str]:
    for name in METADATA_NAMES:
        try:
            raw = zf.read(name).decode("utf-8", "replace")
        except KeyError:
            continue
        mod_id = mod_version = loader_range = mc_range = ""
        if tomllib is not None:
            try:
                data = tomllib.loads(raw)
                mods = data.get("mods") or []
                if mods:
                    mod_id = str(mods[0].get("modId", ""))
                    mod_version = str(mods[0].get("version", ""))
                for entries in (data.get("dependencies") or {}).values():
                    for dep in entries or []:
                        if dep.get("modId") == "neoforge":
                            loader_range = str(dep.get("versionRange", ""))
                        elif dep.get("modId") == "minecraft":
                            mc_range = str(dep.get("versionRange", ""))
                return mod_id, mod_version, loader_range, mc_range
            except Exception:
                pass
        match = re.search(r'(?m)^\s*modId\s*=\s*"([^"]+)"', raw)
        mod_id = match.group(1) if match else ""
        match = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"', raw)
        mod_version = match.group(1) if match else ""
        match = re.search(r'(?m)^\s*versionRange\s*=\s*"(\[26\.[^"]*)"', raw)
        loader_range = match.group(1) if match else ""
        match = re.search(r'(?m)^\s*versionRange\s*=\s*"(\[26\.[0-9.]+\])"', raw)
        mc_range = match.group(1) if match else ""
        return mod_id, mod_version, loader_range, mc_range
    return "", "", "", ""


def jar_dependencies(zf: zipfile.ZipFile) -> tuple[list[tuple[str, str]], list[tuple[str, str, bool, str]]]:
    """Return (mods, deps) where mods = [(modId, version)] and deps = [(owner, modId, mandatory, range)]."""
    for name in METADATA_NAMES:
        try:
            raw = zf.read(name).decode("utf-8", "replace")
        except KeyError:
            continue
        mods: list[tuple[str, str]] = []
        deps: list[tuple[str, str, bool, str]] = []
        if tomllib is not None:
            try:
                data = tomllib.loads(raw)
                for entry in data.get("mods") or []:
                    mods.append((str(entry.get("modId", "")), str(entry.get("version", ""))))
                for owner, entries in (data.get("dependencies") or {}).items():
                    for dep in entries or []:
                        mandatory = dep.get("type", "required") in ("required", "mandatory")
                        if "mandatory" in dep:
                            mandatory = bool(dep.get("mandatory"))
                        deps.append((
                            str(owner),
                            str(dep.get("modId", "")),
                            mandatory,
                            str(dep.get("versionRange", "")),
                        ))
                return mods, deps
            except Exception:
                pass
        return mods, deps
    return [], []


def nested_mods(zf: zipfile.ZipFile) -> dict[str, str]:
    """Collect modId -> version for jar-in-jar dependencies bundled in this jar."""
    import io

    found: dict[str, str] = {}
    for name in zf.namelist():
        if not name.endswith(".jar"):
            continue
        if not (name.startswith("META-INF/jarjar/") or name.startswith("META-INF/jars/")):
            continue
        try:
            with zf.open(name) as raw:
                payload = raw.read()
        except (KeyError, OSError, zipfile.BadZipFile):
            continue
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as inner:
                mods, _deps = jar_dependencies(inner)
                for mod_id, version in mods:
                    if mod_id:
                        found.setdefault(mod_id, version)
        except zipfile.BadZipFile:
            continue
    return found


def inspect_jar(path: Path) -> JarInfo:
    info = JarInfo(path=path)
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            info.mod_id, info.mod_version, info.loader_range, info.mc_range = jar_metadata(zf)
            info.mods, info.deps = jar_dependencies(zf)
            for name in names:
                if not name.endswith(".class"):
                    continue
                if name.startswith("META-INF/") or name == "module-info.class":
                    continue
                package = name.rsplit("/", 1)[0] if "/" in name else ""
                if package:
                    info.packages.add(package)
            info.bundled = nested_mods(zf)
    except zipfile.BadZipFile:
        info.error = "not a valid zip"
    except OSError as exc:
        info.error = str(exc)
    return info


def source_mod_ids(module_dir: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    src = module_dir / "src"
    if not src.is_dir():
        return result
    for java in src.rglob("*.java"):
        text = read_text(java)
        if "@Mod" not in text:
            continue
        consts = set(MODID_CONST_RE.findall(text)) | set(MOD_LITERAL_RE.findall(text))
        if consts:
            result[str(java)] = consts
    return result


def find_lib_dirs(root: Path) -> list[Path]:
    lib_dirs: list[Path] = []
    for root_name in MOD_ROOTS:
        base = root / root_name
        if not base.is_dir():
            continue
        for libs in sorted(base.rglob("build/libs")):
            rel = libs.relative_to(root)
            if is_skipped(Path(*rel.parts[:-2])):
                continue
            lib_dirs.append(libs)
    return lib_dirs


def cmd_jars(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if args.paths:
        lib_dirs = [Path(item).resolve() for item in args.paths]
    else:
        lib_dirs = find_lib_dirs(root)

    if not lib_dirs:
        say("no build/libs directory found")
        return 1

    failures = 0
    for libs in lib_dirs:
        jars = sorted(path for path in libs.glob("*.jar") if path.is_file())
        if not jars:
            continue
        infos = [inspect_jar(path) for path in jars]
        label = libs.relative_to(root) if libs.is_relative_to(root) else libs
        say(f"== {label}")
        for info in infos:
            if info.error:
                say(f"  {info.path.name}: ERROR {info.error}")
                failures += 1
                continue
            say(f"  {info.path.name}")
            say(f"    modId={info.mod_id or '?'} version={info.mod_version or '?'} "
                f"loader={info.loader_range or '?'} mc={info.mc_range or '?'} "
                f"packages={len(info.packages)}")

        groups: dict[str, list[JarInfo]] = {}
        for info in infos:
            if info.error:
                continue
            groups.setdefault(info.mc_range or "unknown", []).append(info)

        for mc_range, group in sorted(groups.items()):
            if len(group) < 2:
                continue
            if len({item.mod_id for item in group if item.mod_id}) < 2:
                continue
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    left, right = group[i], group[j]
                    if left.mod_id and left.mod_id == right.mod_id:
                        continue
                    shared = left.packages & right.packages
                    if shared:
                        failures += 1
                        say(f"  SPLIT PACKAGE [{mc_range}]: {left.path.name} <-> {right.path.name}")
                        for package in sorted(shared)[:10]:
                            say(f"    {package}")
                        if len(shared) > 10:
                            say(f"    ... {len(shared) - 10} more")

        module_dir = libs.parent.parent
        src_ids = source_mod_ids(module_dir)
        all_consts: set[str] = set()
        for ids in src_ids.values():
            all_consts |= ids
        if not all_consts:
            say("  (no @Mod source in this module; skipping modId cross-check)")
            continue
        jar_ids = {item.mod_id for item in infos if item.mod_id and "${" not in item.mod_id}
        for mod_id in sorted(jar_ids - all_consts):
            failures += 1
            say(f"  MODID NOT IN SOURCE: jar declares '{mod_id}', "
                f"source constants: {sorted(all_consts)}")

    if failures:
        say("")
        say(f"FAILED: {failures} problem(s)")
        return 1
    say("")
    say("ok: no split packages, no duplicate modIds")
    return 0


# --------------------------------------------------------------------------
# instance doctor
# --------------------------------------------------------------------------

def find_instance_json(instance: Path) -> Path | None:
    preferred = instance / f"{instance.name}.json"
    if preferred.is_file():
        return preferred
    candidates = sorted(instance.glob("*.json"))
    return candidates[0] if candidates else None


def read_launch_args(data: dict) -> dict[str, str]:
    args = data.get("arguments") or {}
    game = args.get("game") or []
    flat: list[str] = []
    for item in game:
        if isinstance(item, str):
            flat.append(item)
    result: dict[str, str] = {}
    for index, token in enumerate(flat[:-1]):
        if token.startswith("--fml."):
            result[token] = flat[index + 1]
    return result


# NeoForge classes that were removed or renamed after 26.2.0.7-beta.
# Each entry: (removed binary name, replacement hint).
REMOVED_NEOFORGE_APIS: tuple[tuple[str, str], ...] = (
    ("net/neoforged/neoforge/client/event/ContainerScreenEvent$Render$Foreground",
     "ScreenEvent$Render$Foreground"),
    ("net/neoforged/neoforge/client/event/ContainerScreenEvent$Render$Background",
     "ScreenEvent$Render$Background"),
    ("net/neoforged/neoforge/client/event/ContainerScreenEvent",
     "ScreenEvent"),
    ("net/neoforged/neoforge/event/entity/player/PlayerInteractEvent$EntityInteractSpecific",
     "PlayerInteractEvent$EntityInteract"),
)


def removed_api_hits(
    infos: list[JarInfo], loader_version: str
) -> list[tuple[str, str, str]]:
    """Return [(jar name, removed class, replacement)] for jars referencing removed APIs.

    Only reported when the instance loader is newer than the last version that
    shipped the class. We approximate that boundary at 26.2.0.30: every 26.2
    build at or above it already dropped ContainerScreenEvent.
    """
    boundary = "26.2.0.30"
    if compare_versions(loader_version, boundary) < 0:
        return []

    hits: list[tuple[str, str, str]] = []
    for info in infos:
        if info.error:
            continue
        try:
            with zipfile.ZipFile(info.path) as zf:
                names = set(zf.namelist())
                class_payloads: dict[str, bytes] = {}
                reported: set[str] = set()
                for removed, replacement in REMOVED_NEOFORGE_APIS:
                    if removed + ".class" in names:
                        continue
                    needles = (
                        removed.encode("utf-8"),
                        removed.replace("/", ".").encode("utf-8"),
                    )
                    found = False
                    for entry in names:
                        if not entry.endswith(".class"):
                            continue
                        if entry not in class_payloads:
                            try:
                                class_payloads[entry] = zf.read(entry)
                            except (KeyError, OSError, zipfile.BadZipFile):
                                class_payloads[entry] = b""
                        payload = class_payloads[entry]
                        if payload and any(needle in payload for needle in needles):
                            found = True
                            break
                    if found:
                        dotted = removed.replace("/", ".")
                        # Report the outermost removed class once per jar.
                        root = dotted.split("$")[0]
                        if root in reported:
                            continue
                        reported.add(root)
                        hits.append((info.path.name, dotted, replacement))
        except (OSError, zipfile.BadZipFile):
            continue
    return hits


def cmd_doctor(args: argparse.Namespace) -> int:
    instance = Path(args.instance).resolve()
    if not instance.is_dir():
        say(f"instance not found: {instance}")
        return 1

    version_json = find_instance_json(instance)
    if version_json is None:
        say(f"no version json in {instance}")
        return 1

    try:
        data = json.loads(read_text(version_json))
    except ValueError as exc:
        say(f"invalid version json: {exc}")
        return 1

    fml = read_launch_args(data)
    neo_version = fml.get("--fml.neoForgeVersion", "")
    mc_version = fml.get("--fml.mcVersion", "") or str(data.get("clientVersion", ""))

    say(f"instance      : {instance.name}")
    say(f"version json  : {version_json.name}")
    say(f"minecraft     : {mc_version or '?'}")
    say(f"neoforge      : {neo_version or '?'}")
    say(f"java          : {(data.get('javaVersion') or {}).get('majorVersion', '?')}")
    say("")

    mods_dir = instance / "mods"
    if not mods_dir.is_dir():
        say("no mods directory")
        return 1

    jars = sorted(path for path in mods_dir.glob("*.jar") if path.is_file())
    if not jars:
        say("no jars in mods")
        return 0

    infos: list[JarInfo] = []
    for path in jars:
        info = inspect_jar(path)
        if info.error:
            say(f"  {path.name}: ERROR {info.error}")
            continue
        infos.append(info)

    registry: dict[str, str] = {}
    for info in infos:
        for mod_id, mod_version in info.mods or [(info.mod_id, info.mod_version)]:
            if not mod_id:
                continue
            if mod_id in registry and registry[mod_id] != mod_version:
                say(f"DUPLICATE MODID: {mod_id} ({registry[mod_id]} vs {mod_version})")
            registry[mod_id] = mod_version
        for mod_id, version in info.bundled.items():
            registry.setdefault(mod_id, version)
    if neo_version:
        registry["neoforge"] = neo_version
    if mc_version:
        registry["minecraft"] = mc_version
    registry.setdefault("forge", neo_version or mc_version)

    say(f"mods          : {len(infos)} jars, {len(registry)} mod ids")
    say("")

    failures: list[str] = []
    warnings: list[str] = []

    for info in infos:
        for owner, dep_id, mandatory, version_range in info.deps:
            if not dep_id or dep_id in ("minecraft", "neoforge", "forge", "java", "fml"):
                if dep_id in registry and version_range and "${" not in version_range:
                    if not satisfies(registry[dep_id], version_range):
                        text = (f"{info.path.name}: {owner} requires {dep_id} "
                                f"{version_range}, instance has {registry[dep_id]}")
                        (failures if mandatory else warnings).append(text)
                continue
            installed = registry.get(dep_id)
            if installed is None:
                if mandatory:
                    failures.append(f"{info.path.name}: {owner} requires missing mod '{dep_id}'")
                continue
            if version_range and "${" not in version_range and "${" not in installed:
                if not satisfies(installed, version_range):
                    text = (f"{info.path.name}: {owner} requires {dep_id} {version_range}, "
                            f"installed {installed}")
                    (failures if mandatory else warnings).append(text)

    for info in infos:
        if not info.mod_id or "${" in info.mod_id:
            continue
        for mod_id, mod_version in info.mods or [(info.mod_id, info.mod_version)]:
            if mod_id in ("minecraft", "neoforge", "forge") or "${" in mod_version:
                continue
            if mc_version and info.mc_range and "${" not in info.mc_range:
                if not satisfies(mc_version, info.mc_range):
                    failures.append(f"{info.path.name}: declares minecraft {info.mc_range}, "
                                    f"instance is {mc_version}")
            if neo_version and info.loader_range and "${" not in info.loader_range:
                if not satisfies(neo_version, info.loader_range):
                    failures.append(f"{info.path.name}: declares neoforge {info.loader_range}, "
                                    f"instance is {neo_version}")

    seen_packages: dict[str, str] = {}
    for info in infos:
        for package in info.packages:
            previous = seen_packages.get(package)
            if previous and previous != info.path.name:
                failures.append(f"SPLIT PACKAGE '{package}': {previous} and {info.path.name}")
            else:
                seen_packages[package] = info.path.name

    by_mod_id: dict[str, list[str]] = {}
    for info in infos:
        for mod_id, _version in info.mods or [(info.mod_id, info.mod_version)]:
            if mod_id and "${" not in mod_id:
                by_mod_id.setdefault(mod_id, []).append(info.path.name)
    for mod_id, names in sorted(by_mod_id.items()):
        if len(names) > 1:
            failures.append(f"DUPLICATE MOD JAR '{mod_id}': {', '.join(sorted(set(names)))}")

    # Removed/renamed NeoForge APIs: mods compiled against an older loader load
    # fine but crash on construction. Detect the references statically.
    if neo_version:
        missing_api = removed_api_hits(infos, neo_version)
        for mod_name, class_name, replacement in missing_api:
            failures.append(
                f"{mod_name}: references removed NeoForge API '{class_name}'"
                + (f" (use {replacement})" if replacement else "")
                + f"; loader {neo_version} no longer provides it"
            )

    if args.json:
        say(json.dumps({
            "instance": str(instance),
            "minecraft": mc_version,
            "neoforge": neo_version,
            "mods": len(infos),
            "failures": failures,
            "warnings": warnings,
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    if warnings:
        say("warnings:")
        for item in sorted(set(warnings)):
            say(f"  - {item}")
        say("")
    if failures:
        say("failures:")
        for item in sorted(set(failures)):
            say(f"  - {item}")
        say("")
        say(f"FAILED: {len(set(failures))} problem(s)")
        return 1
    say("ok: every mod requirement is satisfied")
    return 0


def jar_class_names(path: Path) -> set[str]:
    """Return the set of class entry names (without .class) inside a jar."""
    try:
        with zipfile.ZipFile(path) as zf:
            return {
                name[: -len(".class")]
                for name in zf.namelist()
                if name.endswith(".class") and not name.startswith("META-INF/")
            }
    except (OSError, zipfile.BadZipFile):
        return set()


def top_level(name: str) -> str:
    """Collapse inner classes so Foo$Bar is reported as Foo."""
    return name.split("$", 1)[0]


def cmd_diff(args: argparse.Namespace) -> int:
    """Compare two NeoForge universal jars and report added/removed API classes."""
    old_jar = Path(args.old).resolve()
    new_jar = Path(args.new).resolve()
    for path in (old_jar, new_jar):
        if not path.is_file():
            say(f"not found: {path}")
            return 1

    old_classes = jar_class_names(old_jar)
    new_classes = jar_class_names(new_jar)
    if not old_classes or not new_classes:
        say("could not read class entries from one of the jars")
        return 1

    removed = sorted({top_level(name) for name in old_classes - new_classes})
    added = sorted({top_level(name) for name in new_classes - old_classes})

    # Focus on public API packages; ignore internal implementation churn.
    def is_api(name: str) -> bool:
        return (
            name.startswith("net/neoforged/neoforge/")
            and "/mixin/" not in name
            and not name.endswith("/package-info")
        )

    removed_api = [name for name in removed if is_api(name)]
    added_api = [name for name in added if is_api(name)]

    if args.json:
        say(json.dumps({
            "old": old_jar.name,
            "new": new_jar.name,
            "old_classes": len(old_classes),
            "new_classes": len(new_classes),
            "removed": removed_api,
            "added": added_api,
        }, ensure_ascii=False, indent=2))
        return 0

    say(f"old: {old_jar.name} ({len(old_classes)} classes)")
    say(f"new: {new_jar.name} ({len(new_classes)} classes)")
    say("")

    say(f"removed classes: {len(removed)} ({len(removed_api)} in neoforge API)")
    for name in removed_api[: args.limit]:
        say(f"  - {name.replace('/', '.')}")
    if len(removed_api) > args.limit:
        say(f"  ... {len(removed_api) - args.limit} more")
    say("")
    say(f"added classes: {len(added)} ({len(added_api)} in neoforge API)")
    for name in added_api[: args.limit]:
        say(f"  + {name.replace('/', '.')}")
    if len(added_api) > args.limit:
        say(f"  ... {len(added_api) - args.limit} more")
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    targets = discover_targets(root)
    rows: dict[tuple[str, str], list[str]] = {}
    for target in targets:
        key = (target.loader_version or "unknown", target.loader or "unknown")
        rows.setdefault(key, []).append(f"{target.repo.split('/')[-1]} {target.mod_version}")
    say(f"{'loader':<24} {'loader type':<12} mods")
    say("-" * 110)
    for (version, loader), mods in sorted(rows.items()):
        say(f"{version:<24} {loader:<12} {', '.join(sorted(mods))}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcver", description=__doc__)
    parser.add_argument("--root", default=".", help="workspace root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="scan build configuration")
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(func=cmd_audit)

    jars = sub.add_parser("jars", help="validate built JARs")
    jars.add_argument("paths", nargs="*", help="build/libs directories")
    jars.set_defaults(func=cmd_jars)

    matrix = sub.add_parser("matrix", help="print version support matrix")
    matrix.set_defaults(func=cmd_matrix)

    doctor = sub.add_parser("doctor", help="check a game instance for mod conflicts")
    doctor.add_argument("instance", help="path to the version directory")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    diff = sub.add_parser("diff", help="compare two NeoForge universal jars")
    diff.add_argument("old", help="older neoforge-<ver>-universal.jar")
    diff.add_argument("new", help="newer neoforge-<ver>-universal.jar")
    diff.add_argument("--limit", type=int, default=60, help="max entries to print per side")
    diff.add_argument("--json", action="store_true")
    diff.set_defaults(func=cmd_diff)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
