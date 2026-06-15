#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

VERSION = "0.1.2"
SURFACE = "ADMINISTRATUM_DATA_ATLAS_CARTOGRAPHIUM_V0_1_2"

HEAVY_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "test-results",
    "playwright-report",
    "dist",
    "build",
}

SCRIPT_EXTS = {".py", ".ps1", ".js", ".ts", ".sh", ".bat", ".cmd"}
TEXT_EXTS = {".md", ".txt", ".json", ".html", ".css", ".yml", ".yaml", ".toml", ".ini", ".cfg"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
ARCHIVE_EXTS = {".zip", ".7z", ".tar", ".gz", ".rar"}

KNOWN_ORGANS = {
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "CUSTODES",
    "DOCTRINARIUM",
    "IMPERIAL_IDE",
    "INQUISITION",
    "MECHANICUS",
    "OFFICIO_AGENTIS",
    "SCHOLA_IMPERIALIS",
    "SPECULUM",
    "STRATEGIUM",
    "_CORE_GOVERNANCE",
    "_POST_WORK_RING",
}


def configure_utf8_stdio() -> None:
    """Make JSON emission safe on Windows consoles using legacy code pages.

    Web Sanctum reads stdout as UTF-8. Some operator consoles still default to
    cp1251/cp866, which can fail on BOM and glyph characters discovered while
    scanning files. Scanner output must never fail because a scanned file
    contains an unrepresentable character.
    """
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def emit_json(raw: str) -> None:
    configure_utf8_stdio()
    try:
        sys.stdout.write(raw + "\n")
    except UnicodeEncodeError:
        # Last-resort path for embedded/redirected stdout wrappers that ignore
        # reconfigure(). Escaped JSON keeps RU/EN payload semantics intact after
        # parsing while remaining ASCII-safe for legacy terminals.
        escaped = raw.encode("unicode_escape").decode("ascii")
        sys.stdout.write(escaped + "\n")

PURPOSE_RU = {
    "organ_passport": "паспорт органа или смысловой контракт",
    "script": "исполняемый инструмент или скрипт системы",
    "ui_surface": "часть визуального интерфейса Web Sanctum",
    "protocol": "доктрина, протокол или owner-readable правило",
    "registry": "машинный реестр состояния, инструментов или адресов",
    "report": "отчёт, receipt или evidence bundle",
    "evidence": "визуальное/тестовое свидетельство работы",
    "test": "автотест или проверочный сценарий",
    "config": "конфигурация окружения или пакета",
    "archive": "архив/ZIP, обычно требует проверки жизненного цикла",
    "runtime_residue": "runtime-след внутри source-зоны, требует классификации",
    "legacy_quarantine": "исторический или учебный карантин, требует решения keep/archive",
    "directory": "директория-носитель структуры",
    "document": "документ или пояснительный текст",
    "unknown": "назначение не определено автоматически",
}

PURPOSE_EN = {
    "organ_passport": "organ passport or semantic contract",
    "script": "executable tool or system script",
    "ui_surface": "Web Sanctum visual surface component",
    "protocol": "doctrine, protocol or owner-readable rule",
    "registry": "machine registry for state, tools or addresses",
    "report": "report, receipt or evidence bundle",
    "evidence": "visual/test evidence of work",
    "test": "automated test or verification scenario",
    "config": "environment or package configuration",
    "archive": "archive/ZIP, lifecycle review recommended",
    "runtime_residue": "runtime trace inside source zone, needs classification",
    "legacy_quarantine": "historical or learning quarantine, needs keep/archive decision",
    "directory": "directory carrying structure",
    "document": "document or explanatory text",
    "unknown": "purpose was not inferred automatically",
}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def run_git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return ""


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "ORGANS").exists():
            return candidate
    return start


def git_maps(repo: Path) -> tuple[set[str], dict[str, str], set[str]]:
    tracked = {line.strip().replace("\\", "/") for line in run_git(repo, "ls-files").splitlines() if line.strip()}
    status: dict[str, str] = {}
    for line in run_git(repo, "status", "--porcelain=v1", "-uall").splitlines():
        if not line.strip():
            continue
        code = line[:2].strip() or "MODIFIED"
        rel = line[3:].strip().replace("\\", "/")
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[-1]
        status[rel] = code
    ignored = set()
    for line in run_git(repo, "status", "--short", "--ignored", "-uall").splitlines():
        if line.startswith("!! "):
            ignored.add(line[3:].strip().replace("\\", "/"))
    return tracked, status, ignored


def split_rel(rel: str) -> list[str]:
    return [part for part in rel.replace("\\", "/").split("/") if part]


def organ_for(rel: str) -> str:
    parts = split_rel(rel)
    if len(parts) >= 2 and parts[0] == "ORGANS":
        return parts[1]
    if parts and parts[0] == "REPORTS":
        return "ADMINISTRATUM"
    if parts and parts[0] == "SUPPORT":
        return "SUPPORT"
    return "ROOT"


def root_zone_for(rel: str) -> str:
    parts = split_rel(rel)
    if not parts:
        return "ROOT"
    if parts[0] == "ORGANS" and len(parts) > 1:
        return f"ORGANS/{parts[1]}"
    return parts[0]


def artifact_type(rel: str, is_dir: bool = False) -> str:
    lower = rel.lower()
    suffix = Path(rel).suffix.lower()
    parts = split_rel(rel)
    name = parts[-1] if parts else rel
    upper = rel.upper()
    if is_dir:
        return "directory"
    if "PASSPORT" in upper:
        return "organ_passport"
    if "STATION/REPORTS" in upper or "FINAL_REPORT_BUNDLES" in upper:
        return "runtime_residue"
    if "QUESTIONABLE_OR_QUARANTINE" in upper or "LEARNING_ARCHIVE" in upper:
        return "legacy_quarantine"
    if parts and parts[0] == "REPORTS":
        return "report"
    if suffix in ARCHIVE_EXTS:
        return "archive"
    if suffix in IMAGE_EXTS or "screenshot" in lower:
        return "evidence"
    if name in {"package.json", "package-lock.json", "playwright.config.ts", ".gitignore"} or suffix in {".yml", ".yaml", ".toml", ".ini", ".cfg"}:
        return "config"
    if suffix in SCRIPT_EXTS:
        if "/tests/" in f"/{lower}/" or lower.endswith(".spec.ts"):
            return "test"
        if "/web_sanctum/app/" in f"/{lower}/" and suffix in {".js", ".html", ".css"}:
            return "ui_surface"
        return "script"
    if suffix == ".md":
        if "protocol" in lower or "contract" in lower or "continuity" in lower:
            return "protocol"
        return "document"
    if suffix == ".json":
        if "registry" in lower or "map" in lower or "snapshot" in lower:
            return "registry"
        return "config"
    if suffix in TEXT_EXTS:
        return "document"
    return "unknown"


def has_passport(repo: Path, rel: str, typ: str) -> bool:
    if typ == "organ_passport":
        return True
    p = repo / rel
    base = p.with_suffix("")
    candidates = [
        p.with_suffix(p.suffix + ".passport.json"),
        p.with_suffix(p.suffix + ".passport.md"),
        base.with_name(base.name + "_PASSPORT.md"),
        base.with_name(base.name + "_PASSPORT.json"),
        p.parent / "PASSPORT" / f"{p.stem}_PASSPORT.md",
        p.parent / "PASSPORT" / f"{p.stem}_PASSPORT.json",
    ]
    return any(candidate.exists() for candidate in candidates)


def read_header_summary(path: Path, typ: str) -> str:
    if typ not in {"script", "protocol", "document", "ui_surface", "config", "registry", "test"}:
        return ""
    if path.suffix.lower() not in TEXT_EXTS | SCRIPT_EXTS:
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:2500]
    except Exception:
        return ""
    for raw in text.splitlines()[:16]:
        line = raw.strip().strip("#/*- ")
        if not line:
            continue
        if line.lower().startswith(("doctype", "from ", "import ", "const ", "let ", "var ", "#!/")):
            continue
        if len(line) > 12:
            return line[:180]
    return ""


def entity_flags(repo: Path, rel: str, typ: str, size: int, status_code: str, ignored: bool, is_dir: bool) -> list[str]:
    flags: list[str] = []
    upper = rel.upper()
    if status_code:
        flags.append("GIT_DIRTY")
        if status_code == "??":
            flags.append("UNTRACKED")
    if ignored:
        flags.append("IGNORED")
    if "STATION/REPORTS" in upper or "FINAL_REPORT_BUNDLES" in upper:
        flags.append("SOURCE_RUNTIME_LEAK")
    if rel.startswith("REPORTS/") and (Path(rel).suffix.lower() in ARCHIVE_EXTS or size > 5_000_000):
        flags.append("SOURCE_REPORT_ARCHIVE")
    if Path(rel).suffix.lower() in ARCHIVE_EXTS:
        flags.append("ARCHIVE_REVIEW")
    if size > 5_000_000:
        flags.append("LARGE_FILE")
    if organ_for(rel) not in KNOWN_ORGANS | {"ROOT", "REPORTS", "SUPPORT"}:
        flags.append("UNKNOWN_OWNER")
    if typ in {"script", "ui_surface"} and not has_passport(repo, rel, typ):
        flags.append("NO_PASSPORT")
    if typ == "legacy_quarantine":
        flags.append("QUARANTINE_REVIEW")
    if typ == "unknown":
        flags.append("UNKNOWN_TYPE")
    if is_dir and not any((repo / rel).iterdir()):
        flags.append("EMPTY_DIR")
    return flags


def health_from_flags(flags: list[str]) -> str:
    critical = {"SOURCE_RUNTIME_LEAK"}
    warning = {"GIT_DIRTY", "UNTRACKED", "IGNORED", "SOURCE_REPORT_ARCHIVE", "ARCHIVE_REVIEW", "LARGE_FILE", "NO_PASSPORT", "UNKNOWN_OWNER", "UNKNOWN_TYPE", "EMPTY_DIR", "QUARANTINE_REVIEW", "DUPLICATE_HASH"}
    if any(flag in critical for flag in flags):
        return "CRITICAL"
    if any(flag in warning for flag in flags):
        return "WARNING"
    return "SAFE"


def cleanup_lane_for(rel: str, typ: str, flags: list[str]) -> str:
    if "SOURCE_RUNTIME_LEAK" in flags:
        return "source_runtime_leaks"
    if "GIT_DIRTY" in flags or "UNTRACKED" in flags:
        return "git_dirty_review"
    if "ARCHIVE_REVIEW" in flags or "SOURCE_REPORT_ARCHIVE" in flags:
        return "archive_lifecycle_review"
    if "DUPLICATE_HASH" in flags:
        return "duplicate_review"
    if "QUARANTINE_REVIEW" in flags or typ == "legacy_quarantine":
        return "legacy_quarantine_review"
    if "NO_PASSPORT" in flags:
        return "passport_needed"
    if "UNKNOWN_TYPE" in flags or "UNKNOWN_OWNER" in flags:
        return "unknown_semantics"
    if "LARGE_FILE" in flags:
        return "large_file_review"
    return "clean_source"


def recommendation_for(lane: str) -> tuple[str, str]:
    table = {
        "source_runtime_leaks": (
            "Вынести runtime/reports/evidence из source в LOCAL_HANDOFF или WARP_RUNS после owner review.",
            "Move runtime/reports/evidence out of source into LOCAL_HANDOFF or WARP_RUNS after owner review.",
        ),
        "git_dirty_review": (
            "Проверить untracked/dirty: принять, перенести в runtime или удалить только отдельным cleanup-gate.",
            "Review untracked/dirty items: accept, move to runtime, or delete only through a cleanup gate.",
        ),
        "archive_lifecycle_review": (
            "Проверить ZIP/archive: KEEP, ARCHIVE, or EXPIRE; не держать report bundles в source без причины.",
            "Review ZIP/archive lifecycle: KEEP, ARCHIVE, or EXPIRE; do not keep report bundles in source without a reason.",
        ),
        "duplicate_review": (
            "Сравнить дубли по владельцу и lifecycle; удалить/свести только после owner-confirmed replacement.",
            "Compare duplicates by owner and lifecycle; remove/merge only after owner-confirmed replacement.",
        ),
        "legacy_quarantine_review": (
            "Разобрать quarantine/learning archive: нужное паспортизировать, лишнее отправить в архивный контур.",
            "Review quarantine/learning archive: passport useful pieces, move obsolete pieces to archive contour.",
        ),
        "passport_needed": (
            "Добавить краткий паспорт для важных скриптов/UI или подтвердить, что паспорт не нужен.",
            "Add a compact passport for important scripts/UI or confirm that no passport is needed.",
        ),
        "unknown_semantics": (
            "Назначение не определено автоматически: owner/organ должен классифицировать смысл.",
            "Purpose was not inferred automatically: owner/organ should classify semantics.",
        ),
        "large_file_review": (
            "Проверить крупный файл: это source truth, evidence или случайный тяжёлый артефакт.",
            "Review large file: source truth, evidence, or accidental heavy artifact.",
        ),
        "clean_source": (
            "Нормальная source/semantic сущность; действий не требуется.",
            "Normal source/semantic entity; no action required.",
        ),
    }
    return table.get(lane, table["unknown_semantics"])


def owner_summary_for(entity: dict[str, Any]) -> str:
    flags = entity.get("flags") or []
    lane = entity.get("cleanup_lane") or cleanup_lane_for(entity.get("path", ""), entity.get("type", "unknown"), flags)
    if lane == "source_runtime_leaks":
        return "runtime/report residue is sitting inside source and must be relocated or explicitly kept"
    if lane == "legacy_quarantine_review":
        return "legacy/quarantine item: useful for history, but should not pollute active source perception"
    if lane == "passport_needed":
        return "important executable/UI entity without a human-readable passport"
    if lane == "duplicate_review":
        return "content hash appears in more than one place; ownership/lifecycle review needed"
    if lane == "archive_lifecycle_review":
        return "archive or report bundle needs KEEP/ARCHIVE/EXPIRE lifecycle decision"
    if lane == "git_dirty_review":
        return "git sees this as untracked/dirty; classify before promotion"
    if lane == "unknown_semantics":
        return "automatic classifier could not determine purpose/owner confidently"
    return "classified source entity"


def count_skipped_heavy_dirs(repo: Path) -> Counter:
    skipped = Counter()
    for root, dirs, _files in os.walk(repo):
        kept = []
        for d in dirs:
            if d in HEAVY_DIRS:
                skipped[d] += 1
            else:
                kept.append(d)
        dirs[:] = kept
    return skipped


def priority_rank(entity: dict[str, Any]) -> tuple[int, str]:
    flags = set(entity.get("flags") or [])
    lane = entity.get("cleanup_lane") or "clean_source"
    health = entity.get("health") or "SAFE"
    if "SOURCE_RUNTIME_LEAK" in flags:
        return (0, entity.get("path", ""))
    if health == "CRITICAL":
        return (1, entity.get("path", ""))
    if "GIT_DIRTY" in flags or "UNTRACKED" in flags:
        return (2, entity.get("path", ""))
    if "ARCHIVE_REVIEW" in flags or "SOURCE_REPORT_ARCHIVE" in flags:
        return (3, entity.get("path", ""))
    if "DUPLICATE_HASH" in flags:
        return (4, entity.get("path", ""))
    if lane == "legacy_quarantine_review":
        return (5, entity.get("path", ""))
    if "NO_PASSPORT" in flags:
        return (6, entity.get("path", ""))
    if "UNKNOWN_TYPE" in flags or "UNKNOWN_OWNER" in flags:
        return (7, entity.get("path", ""))
    return (9, entity.get("path", ""))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def iter_paths(repo: Path, include_heavy: bool = False):
    skipped = Counter()
    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        rel_root = root_path.relative_to(repo).as_posix() if root_path != repo else ""
        kept_dirs = []
        for d in dirs:
            if not include_heavy and d in HEAVY_DIRS:
                skipped[d] += 1
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs
        if rel_root:
            yield root_path, rel_root, True, 0, skipped
        for name in files:
            p = root_path / name
            try:
                size = p.stat().st_size
            except Exception:
                size = 0
            rel = p.relative_to(repo).as_posix()
            yield p, rel, False, size, skipped


def scan(repo: Path, ui_limit: int = 5000, include_heavy: bool = False, hash_limit: int = 8_000_000) -> dict[str, Any]:
    repo = find_repo_root(repo)
    tracked, status_map, ignored_set = git_maps(repo)
    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip() or "unknown"
    head = run_git(repo, "rev-parse", "HEAD").strip() or "unknown"

    entities: list[dict[str, Any]] = []
    size_groups: defaultdict[int, list[tuple[str, Path]]] = defaultdict(list)
    skipped_total = count_skipped_heavy_dirs(repo)

    for path, rel, is_dir, size, skipped in iter_paths(repo, include_heavy=include_heavy):
        _ = skipped  # iterator keeps compatibility; totals are counted once by count_skipped_heavy_dirs().
        typ = artifact_type(rel, is_dir=is_dir)
        status_code = status_map.get(rel, "")
        git_state = "tracked" if rel in tracked else "untracked" if status_code == "??" else "dirty" if status_code else "untracked_or_generated"
        ignored = rel in ignored_set or any(item.rstrip("/") in rel for item in ignored_set if item.endswith("/"))
        flags = entity_flags(repo, rel, typ, size, status_code, ignored, is_dir)
        health = health_from_flags(flags)
        organ = organ_for(rel)
        summary = read_header_summary(path, typ) if not is_dir else ""
        passport_state = "present" if has_passport(repo, rel, typ) else "required" if "NO_PASSPORT" in flags else "not_required"
        cleanup_lane = cleanup_lane_for(rel, typ, flags)
        recommendation_ru, recommendation_en = recommendation_for(cleanup_lane)
        lifecycle = "runtime_or_generated" if typ in {"runtime_residue", "report", "evidence", "archive"} else "legacy_quarantine" if typ == "legacy_quarantine" else "source_or_semantic"
        entity = {
            "id": hashlib.sha1(rel.encode("utf-8", errors="replace")).hexdigest()[:12],
            "path": rel,
            "name": Path(rel).name,
            "kind": "directory" if is_dir else "file",
            "type": typ,
            "organ": organ,
            "root_zone": root_zone_for(rel),
            "size_bytes": size,
            "git_state": git_state,
            "git_code": status_code,
            "health": health,
            "flags": flags,
            "passport": passport_state,
            "purpose_ru": PURPOSE_RU.get(typ, PURPOSE_RU["unknown"]),
            "purpose_en": PURPOSE_EN.get(typ, PURPOSE_EN["unknown"]),
            "summary": summary,
            "lifecycle": lifecycle,
            "cleanup_lane": cleanup_lane,
            "recommendation_ru": recommendation_ru,
            "recommendation_en": recommendation_en,
        }
        entity["owner_summary"] = owner_summary_for(entity)
        entities.append(entity)
        if not is_dir and size > 0 and size <= hash_limit:
            size_groups[size].append((rel, path))

    duplicate_groups = []
    for size, group in size_groups.items():
        if len(group) < 2:
            continue
        by_hash: defaultdict[str, list[str]] = defaultdict(list)
        for rel, path in group:
            try:
                by_hash[sha256(path)].append(rel)
            except Exception:
                continue
        for digest, paths in by_hash.items():
            if len(paths) > 1:
                duplicate_groups.append({"sha256": digest, "size_bytes": size, "count": len(paths), "paths": sorted(paths)})
    duplicate_groups.sort(key=lambda item: (-item["count"], -item["size_bytes"]))

    duplicate_paths = {p for group in duplicate_groups for p in group["paths"]}
    for entity in entities:
        if entity["path"] in duplicate_paths:
            entity["flags"].append("DUPLICATE_HASH")
            if entity["health"] == "SAFE":
                entity["health"] = "WARNING"
        entity["cleanup_lane"] = cleanup_lane_for(entity["path"], entity["type"], entity["flags"])
        entity["recommendation_ru"], entity["recommendation_en"] = recommendation_for(entity["cleanup_lane"])
        entity["owner_summary"] = owner_summary_for(entity)

    by_organ = defaultdict(lambda: Counter(total=0, safe=0, warning=0, critical=0, files=0, dirs=0, no_passport=0))
    by_type = Counter()
    by_health = Counter()
    by_lifecycle = Counter()
    by_cleanup_lane = Counter()
    flags = Counter()
    for entity in entities:
        org = by_organ[entity["organ"]]
        org["total"] += 1
        org[entity["health"].lower()] += 1
        org["files" if entity["kind"] == "file" else "dirs"] += 1
        if entity["passport"] == "required":
            org["no_passport"] += 1
        by_type[entity["type"]] += 1
        by_health[entity["health"]] += 1
        by_lifecycle[entity["lifecycle"]] += 1
        by_cleanup_lane[entity["cleanup_lane"]] += 1
        flags.update(entity["flags"])

    cleanup_lanes: dict[str, dict[str, Any]] = {}
    for lane, count in sorted(by_cleanup_lane.items(), key=lambda item: (-item[1], item[0])):
        sample = [entity for entity in entities if entity["cleanup_lane"] == lane][:8]
        rec_ru, rec_en = recommendation_for(lane)
        cleanup_lanes[lane] = {
            "count": count,
            "critical": sum(1 for entity in entities if entity["cleanup_lane"] == lane and entity["health"] == "CRITICAL"),
            "warning": sum(1 for entity in entities if entity["cleanup_lane"] == lane and entity["health"] == "WARNING"),
            "recommendation_ru": rec_ru,
            "recommendation_en": rec_en,
            "sample": sample,
        }

    largest = sorted((entity for entity in entities if entity["kind"] == "file"), key=lambda item: item["size_bytes"], reverse=True)[:80]
    dirty = [entity for entity in entities if entity["health"] != "SAFE" or entity["git_code"]]
    dirty.sort(key=priority_rank)
    priority_entities = sorted(entities, key=lambda item: (*priority_rank(item), item["organ"], item["path"]))

    important_total = sum(1 for item in entities if item["type"] in {"script", "ui_surface", "organ_passport"})
    missing_passports = sum(1 for item in entities if item["passport"] == "required")
    coverage = 100 if important_total == 0 else round(100 * (important_total - missing_passports) / important_total, 1)

    return {
        "status": "PASS_WITH_WARNINGS" if by_health["CRITICAL"] or by_health["WARNING"] else "PASS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": now_utc(),
        "repo_root": norm(repo),
        "branch": branch,
        "head": head,
        "doctrine": {
            "ru": "Read-only Атлас данных: показывает файлы, владельцев, паспорта, грязь, дубли и lifecycle без удаления и без shell-доступа.",
            "en": "Read-only Data Atlas: shows files, owners, passports, dirt, duplicates and lifecycle without deletion or shell access.",
        },
        "summary": {
            "entities_total": len(entities),
            "files_total": sum(1 for item in entities if item["kind"] == "file"),
            "directories_total": sum(1 for item in entities if item["kind"] == "directory"),
            "safe_total": by_health["SAFE"],
            "warning_total": by_health["WARNING"],
            "critical_total": by_health["CRITICAL"],
            "dirty_total": len(dirty),
            "duplicate_groups_total": len(duplicate_groups),
            "duplicate_files_total": len(duplicate_paths),
            "missing_passports_total": missing_passports,
            "passport_coverage_percent": coverage,
            "source_runtime_leaks_total": flags["SOURCE_RUNTIME_LEAK"],
            "large_files_total": flags["LARGE_FILE"],
            "archive_review_total": flags["ARCHIVE_REVIEW"],
            "skipped_heavy_dirs": dict(skipped_total),
        },
        "by_organ": {organ: dict(counter) for organ, counter in sorted(by_organ.items())},
        "by_type": dict(by_type),
        "by_health": dict(by_health),
        "by_lifecycle": dict(by_lifecycle),
        "by_cleanup_lane": dict(by_cleanup_lane),
        "cleanup_lanes": cleanup_lanes,
        "flags": dict(flags),
        "dirty_priority": dirty[:120],
        "largest_files": largest,
        "duplicate_groups": duplicate_groups[:80],
        "entities": priority_entities[:ui_limit] if ui_limit and ui_limit > 0 else priority_entities,
        "entities_returned": min(len(priority_entities), ui_limit) if ui_limit and ui_limit > 0 else len(priority_entities),
        "entities_total": len(priority_entities),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Imperium Data Atlas read-only scanner")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ui-limit", type=int, default=5000)
    parser.add_argument("--include-heavy", action="store_true")
    parser.add_argument("--hash-limit", type=int, default=8_000_000)
    parser.add_argument("--out")
    args = parser.parse_args()
    data = scan(Path(args.repo_root), ui_limit=args.ui_limit, include_heavy=args.include_heavy, hash_limit=args.hash_limit)
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
    emit_json(raw)


if __name__ == "__main__":
    main()
