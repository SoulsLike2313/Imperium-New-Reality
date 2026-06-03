#!/usr/bin/env python3
"""Administratum-Agent hardening core (reference-grade trajectory, stdlib-only)."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

AGENT_ROOT = Path(__file__).resolve().parents[1]
NEW_GENERATION_ROOT = AGENT_ROOT.parents[1]
REPO_ROOT = AGENT_ROOT.parents[2]
RUNS_ROOT = NEW_GENERATION_ROOT / "RUNS" / "ADMINISTRATUM_AGENT"
RULES_ROOT = AGENT_ROOT / "brain_node" / "rules"
STATE_ROOT = AGENT_ROOT / "state"

DEFAULT_CONTEXT_LOCAL = Path("E:/IMPERIUM_CONTEXT/LOCAL")
DEFAULT_CONTEXT_PRIVATE = Path("E:/IMPERIUM_CONTEXT/PRIVATE")

SKILL_IDS = [
    "build_repo_inventory",
    "classify_repo_zone",
    "build_provenance_index",
    "find_useful_candidates",
    "detect_dirty_runtime_outputs",
    "build_merge_preparation_summary",
    "route_to_organs",
    "scan_imperium_context",
    "classify_local_context",
    "detect_private_export_risk",
    "collect_continuity_pack",
    "collect_reality_snapshot",
    "build_agent_handoff_context",
    "verify_pack_against_reality",
    "metrics_summary",
    "explain_decision",
    "show_kpd",
    "cu_summary",
]

CU_TAXONOMY = [
    "rule",
    "case",
    "route_pattern",
    "scoring_weight",
    "metric_definition",
    "output_template",
    "correction_memory_item",
    "gate",
    "path_recognizer",
    "vocabulary_item",
    "policy_snippet",
    "skill_definition",
    "provenance_signature",
    "redaction_pattern",
    "receipt_pattern",
    "cli_ux_pattern",
]

METRIC_FIELDS = [
    "wall_clock_ms",
    "process_cpu_seconds",
    "peak_memory_kb",
    "peak_memory_unavailable_reason",
    "memory_metric_source",
    "files_scanned",
    "files_classified",
    "objects_considered",
    "outputs_written_count",
    "output_bytes_total",
    "warnings_count",
    "errors_count",
    "rejected_count",
    "routes_made",
    "receipts_written",
    "dirty_before",
    "dirty_after",
    "gpu_used",
    "gpu_reason",
    "touched_paths_read_count",
    "touched_paths_written_count",
    "run_cost_class",
    "owner_wait_seconds",
    "maintenance_cost_note",
    "output_bytes",
    "cost_class",
    "dirty_tree_before",
    "dirty_tree_after",
]

REJECTION_KEYWORDS = {"delete", "remove", "merge into canon", "promote to canon", "rewrite canon", "reset --hard"}
PRIVATE_NAME_MARKERS = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "token",
    "secret",
    "credential",
    "passwd",
    "password",
    "wallet",
    ".pem",
    ".key",
}


@dataclass
class SkillRunResult:
    skill_id: str
    report: Dict[str, Any]
    report_path: str
    receipt: Dict[str, Any]
    receipt_path: str
    run_dir: str


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return f"{prefix}_{hashlib.sha1(payload).hexdigest()[:12]}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def append_jsonl(path: Path, item: Dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            buf = fh.read(65536)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def run_git(args: Sequence[str], cwd: Optional[Path] = None) -> Tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip()


def git_head(repo_root: Path) -> str:
    _, out = run_git(["rev-parse", "HEAD"], cwd=repo_root)
    return out


def git_status_porcelain(repo_root: Path) -> List[str]:
    rc, out = run_git(["status", "--porcelain"], cwd=repo_root)
    if rc != 0 or not out:
        return []
    return [line for line in out.splitlines() if line.strip()]


def git_is_dirty(repo_root: Path) -> bool:
    return bool(git_status_porcelain(repo_root))


def git_branch(repo_root: Path) -> str:
    _, out = run_git(["branch", "--show-current"], cwd=repo_root)
    return out


def tracked_set(repo_root: Path) -> set[str]:
    rc, out = run_git(["ls-files"], cwd=repo_root)
    return set(out.splitlines()) if rc == 0 and out else set()


def ensure_runs_root() -> None:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    gitignore = RUNS_ROOT / ".gitignore"
    gitkeep = RUNS_ROOT / ".gitkeep"
    if not gitignore.exists():
        gitignore.write_text(
            "\n".join(
                [
                    "# Administratum runtime output",
                    "RUN-*/",
                    "*.tmp",
                    "!.gitignore",
                    "!.gitkeep",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")


def create_run_dir(out_dir: Optional[str] = None) -> Tuple[str, Path]:
    ensure_runs_root()
    if out_dir:
        out_path = Path(out_dir)
        if not out_path.is_absolute():
            out_path = (REPO_ROOT / out_path).resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        base_name = f"RUN-ADMINISTRATUM-{stamp}-{stable_id('r', now_utc())[-6:]}"
        out_path = RUNS_ROOT / base_name
        suffix = 1
        while out_path.exists():
            out_path = RUNS_ROOT / f"{base_name}-{suffix:02d}"
            suffix += 1

    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "receipts").mkdir(parents=True, exist_ok=True)
    (out_path / "reports").mkdir(parents=True, exist_ok=True)
    return out_path.name, out_path


def rule_json(name: str) -> Dict[str, Any]:
    return read_json(RULES_ROOT / name)


def new_metrics(command: str, dirty_before: bool) -> Dict[str, Any]:
    return {
        "command": command,
        "wall_clock_ms": 0,
        "process_cpu_seconds": 0.0,
        "peak_memory_kb": None,
        "peak_memory_unavailable_reason": "not_measured_yet",
        "memory_metric_source": "unavailable",
        "files_scanned": 0,
        "files_classified": 0,
        "objects_considered": 0,
        "outputs_written_count": 0,
        "output_bytes_total": 0,
        "warnings_count": 0,
        "errors_count": 0,
        "rejected_count": 0,
        "routes_made": 0,
        "receipts_written": 0,
        "gpu_used": False,
        "gpu_reason": "No GPU API/dependency invoked; Python stdlib/script-first execution.",
        "touched_paths_read_count": 0,
        "touched_paths_written_count": 0,
        "owner_wait_seconds": 0.0,
        "maintenance_cost_note": "Low ongoing maintenance in stdlib-first mode.",
        "run_cost_class": "UNSET",
        "output_bytes": 0,
        "cost_class": "UNSET",
        "dirty_before": dirty_before,
        "dirty_after": dirty_before,
        "dirty_tree_before": dirty_before,
        "dirty_tree_after": dirty_before,
    }


def _cost_class(metrics: Dict[str, Any]) -> str:
    wall = int(metrics.get("wall_clock_ms", 0))
    objects = int(metrics.get("objects_considered", 0))
    if wall > 180000 or objects > 15000:
        return "HEAVY"
    if wall > 60000 or objects > 6000:
        return "MEDIUM"
    return "LIGHT"


def finalize_metrics(
    metrics: Dict[str, Any],
    start_ns: int,
    output_paths: Sequence[Path],
    dirty_after: bool,
    process_cpu_seconds: Optional[float] = None,
    peak_memory_kb: Optional[int] = None,
    peak_memory_source: str = "unavailable",
    peak_memory_reason: str = "",
    touched_paths_read_count: Optional[int] = None,
    touched_paths_written_count: Optional[int] = None,
) -> Dict[str, Any]:
    metrics["wall_clock_ms"] = int((time.perf_counter_ns() - start_ns) / 1_000_000)
    metrics["owner_wait_seconds"] = round(metrics["wall_clock_ms"] / 1000.0, 3)
    if process_cpu_seconds is not None:
        metrics["process_cpu_seconds"] = round(float(process_cpu_seconds), 6)
    if peak_memory_kb is not None:
        metrics["peak_memory_kb"] = int(peak_memory_kb)
        metrics["peak_memory_unavailable_reason"] = ""
        metrics["memory_metric_source"] = peak_memory_source or "tracemalloc"
    else:
        metrics["peak_memory_kb"] = None
        metrics["peak_memory_unavailable_reason"] = peak_memory_reason or "unavailable_in_current_runtime"
        metrics["memory_metric_source"] = peak_memory_source or "unavailable"
    total_bytes = 0
    for p in output_paths:
        if p.exists() and p.is_file():
            total_bytes += p.stat().st_size
    metrics["outputs_written_count"] = len([p for p in output_paths if p.exists() and p.is_file()])
    metrics["output_bytes_total"] = total_bytes
    metrics["output_bytes"] = total_bytes
    if touched_paths_read_count is not None:
        metrics["touched_paths_read_count"] = int(touched_paths_read_count)
    if touched_paths_written_count is not None:
        metrics["touched_paths_written_count"] = int(touched_paths_written_count)
    metrics["dirty_after"] = dirty_after
    metrics["dirty_tree_after"] = dirty_after
    metrics["cost_class"] = _cost_class(metrics)
    metrics["run_cost_class"] = metrics["cost_class"]
    return metrics


def record_run_event(run_dir: Path, event_type: str, payload: Dict[str, Any]) -> None:
    event = {
        "event_id": stable_id("evt", event_type, now_utc()),
        "event_type": event_type,
        "agent_id": "ADMINISTRATUM_AGENT",
        "timestamp_utc": now_utc(),
        "payload": payload,
    }
    append_jsonl(run_dir / "events.jsonl", event)


def normalize_rel_path(path: str, repo_root: Path) -> Tuple[str, bool]:
    raw = Path(path)
    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        resolved = (repo_root / raw).resolve()
    try:
        rel = resolved.relative_to(repo_root.resolve()).as_posix()
        return rel, True
    except ValueError:
        return str(resolved).replace("\\", "/"), False


def _context_scope(rel_or_abs: str) -> Optional[str]:
    path_norm = rel_or_abs.replace("\\", "/").upper()
    if "/IMPERIUM_CONTEXT/LOCAL/" in path_norm:
        return "LOCAL_CONTEXT"
    if "/IMPERIUM_CONTEXT/PRIVATE/" in path_norm:
        return "PRIVATE_CONTEXT"
    return None


def classify_zone(rel_path: str, is_inside_repo: bool) -> str:
    context_scope = _context_scope(rel_path)
    if context_scope:
        return context_scope

    if not is_inside_repo:
        return "FORBIDDEN"

    path_norm = rel_path.replace("\\", "/")
    if path_norm.startswith("IMPERIUM_NEW_GENERATION/RUNS/") or path_norm.startswith("IMPERIUM_NEW_GENERATION/RUNTIME/"):
        return "RUNTIME_OUTPUT"

    rules = rule_json("repo_zone_classification_rules.json")
    for row in rules.get("zone_patterns", []):
        zone = str(row.get("zone", ""))
        for prefix in row.get("prefixes", []):
            if path_norm.startswith(prefix):
                return zone

    if path_norm.startswith("IMPERIUM_NEW_GENERATION/"):
        return "NEW_GENERATION_SANDBOX"
    return "DIRTY_UNKNOWN"


def classify_artifact_type(rel_path: str) -> str:
    p = rel_path.lower()
    ext = Path(rel_path).suffix.lower()
    if ext in {".py", ".ps1", ".sh", ".bat", ".cmd"}:
        return "SCRIPT"
    if ext == ".json" and "schema" in p:
        return "SCHEMA"
    if ext == ".json" and "receipt" in p:
        return "RECEIPT_JSON"
    if ext == ".json" and "report" in p:
        return "REPORT_JSON"
    if ext == ".jsonl":
        return "RUNTIME_STATE"
    if ext in {".md", ".txt"} and "policy" in p:
        return "POLICY_DOC"
    if ext in {".md", ".txt"} and ("doctrine" in p or "doctrinarium" in p):
        return "DOCTRINE_DOC"
    if ext in {".pdf"} and ("advisory" in p or "review" in p):
        return "ADVISORY_DOC"
    if ext in {".html", ".css", ".js", ".tsx", ".ts"}:
        return "UI_FILE"
    if ext == ".json":
        return "JSON_DATA"
    return "UNKNOWN"


def _has_private_name_risk(path: str) -> bool:
    low = path.lower()
    return any(marker in low for marker in PRIVATE_NAME_MARKERS)


def risk_level(zone_class: str, artifact_type: str, rel_path: str) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    level = "LOW"
    low = rel_path.lower()
    if zone_class == "PRIVATE_CONTEXT":
        level = "CRITICAL"
        reasons.append("private context path")
    elif zone_class in {"FORBIDDEN", "LOCAL_CONTEXT"}:
        level = "HIGH"
        reasons.append("outside repository sandbox")
    elif zone_class == "DIRTY_UNKNOWN":
        level = "MEDIUM"
        reasons.append("unknown repository zone")

    if _has_private_name_risk(rel_path):
        level = "CRITICAL"
        reasons.append("sensitive filename marker")
    if artifact_type == "UNKNOWN":
        if level == "LOW":
            level = "MEDIUM"
        reasons.append("unknown artifact type")
    if "runtime" in low and "imperium_new_generation/runs/" not in low:
        if level in {"LOW", "MEDIUM"}:
            level = "HIGH"
        reasons.append("runtime marker outside admitted runs layer")
    return level, reasons


def classification_confidence(zone_class: str, tracked: bool, risk_level_value: str) -> float:
    base = 0.85 if tracked else 0.62
    if zone_class in {"PRIVATE_CONTEXT", "FORBIDDEN"}:
        base = 0.9
    if risk_level_value == "CRITICAL":
        base += 0.05
    if risk_level_value == "MEDIUM":
        base -= 0.07
    return round(max(0.05, min(0.99, base)), 3)


def classify_path(path: str, repo_root: Path, tracked_hint: Optional[bool] = None) -> Dict[str, Any]:
    rel, inside = normalize_rel_path(path, repo_root)
    zone = classify_zone(rel, inside)
    art = classify_artifact_type(rel)
    risk, risk_reasons = risk_level(zone, art, rel)
    if inside:
        tracked = tracked_hint if tracked_hint is not None else is_git_tracked(rel, repo_root)
    else:
        tracked = False

    provenance_status = "KNOWN_COMMITTED" if tracked else "UNKNOWN_UNTRACKED"
    trust = "UNKNOWN"
    if zone == "RUNTIME_OUTPUT":
        trust = "RUNTIME_NOT_CANON"
    elif zone == "NEW_GENERATION_SANDBOX" and tracked:
        trust = "SANDBOX_TRUSTED_IF_CLEAN"
    elif zone == "PRIVATE_CONTEXT":
        trust = "PRIVATE_RESTRICTED"
    elif zone == "LOCAL_CONTEXT":
        trust = "LOCAL_REVIEW_REQUIRED"
    elif zone in {"FORBIDDEN", "DIRTY_UNKNOWN"}:
        trust = "UNSAFE"

    return {
        "artifact_id": stable_id("artifact", rel),
        "path": rel,
        "zone_class": zone,
        "artifact_type": art,
        "provenance_status": provenance_status,
        "trust_level": trust,
        "risk_level": risk,
        "risk_reasons": risk_reasons,
        "git_tracked": tracked,
        "classification_confidence": classification_confidence(zone, tracked, risk),
    }


def is_git_tracked(rel_path: str, repo_root: Path) -> bool:
    rc, _ = run_git(["ls-files", "--error-unmatch", rel_path], cwd=repo_root)
    return rc == 0


def _contains_mutation_request(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in REJECTION_KEYWORDS)


def route_for_object(obj: Dict[str, Any], requested_action: str = "") -> Dict[str, Any]:
    zone = obj.get("zone_class", "UNKNOWN")
    artifact = obj.get("artifact_type", "UNKNOWN")
    risk = obj.get("risk_level", "LOW")
    reason: List[str] = []
    routes: List[str] = []
    confidence = 0.65
    escalation: Optional[str] = None
    verdict = "PASS"

    if requested_action and _contains_mutation_request(requested_action):
        routes = ["CUSTODES_AGENT", "INQUISITION_AGENT", "THRONE_AGENT"]
        reason.append("mutation/deletion request detected")
        confidence = 0.95
        escalation = "REQUEST_MUTATION_REJECT"
        verdict = "BLOCKED_SCOPE_OR_MUTATION_REQUEST"
    else:
        if zone == "PRIVATE_CONTEXT":
            routes.extend(["CUSTODES_AGENT", "INQUISITION_AGENT", "THRONE_AGENT"])
            reason.append("private context export risk")
            confidence = 0.93
            escalation = "PRIVATE_EXPORT_RISK"
        elif zone == "LOCAL_CONTEXT":
            routes.extend(["ADMINISTRATUM_AGENT", "CUSTODES_AGENT"])
            reason.append("local machine context intake")
            confidence = 0.82
        elif zone == "RUNTIME_OUTPUT":
            routes.extend(["ADMINISTRATUM_AGENT", "INQUISITION_AGENT"])
            reason.append("runtime output classification")
            confidence = 0.8

        if risk in {"HIGH", "CRITICAL"}:
            routes.extend(["CUSTODES_AGENT", "INQUISITION_AGENT"])
            reason.append("high-risk evidence")
            confidence = max(confidence, 0.85)
            if escalation is None:
                escalation = "HIGH_RISK_REVIEW"

        if artifact in {"POLICY_DOC", "DOCTRINE_DOC"}:
            routes.append("DOCTRINARIUM_AGENT")
            reason.append("policy/doctrine review")
        if artifact == "SCRIPT":
            routes.append("MECHANICUS_AGENT")
            reason.append("script/tool review")
        if zone == "ADVISORY":
            routes.append("ASTRONOMICON_AGENT")
            reason.append("advisory alignment review")

        if not routes:
            routes = ["ADMINISTRATUM_AGENT", "MECHANICUS_AGENT"]
            reason.append("default sandbox analysis route")
            confidence = 0.7

    ordered: List[str] = []
    seen = set()
    for route in routes:
        if route not in seen:
            ordered.append(route)
            seen.add(route)

    primary_owner = ordered[0] if ordered else "ADMINISTRATUM_AGENT"
    co_reviewers = ordered[1:] if len(ordered) > 1 else []
    if escalation is None and risk in {"HIGH", "CRITICAL"}:
        escalation = "RISK_ESCALATION_REQUIRED"

    return {
        "verdict": verdict,
        "route_to": ordered,
        "routing_reason": "; ".join(reason),
        "route_confidence": round(min(0.99, max(0.05, confidence)), 3),
        "escalation_reason": escalation,
        "primary_owner": primary_owner,
        "co_reviewers": co_reviewers,
    }


def get_last_commit(path: str, repo_root: Path) -> Dict[str, Optional[str]]:
    rc, out = run_git(["log", "-1", "--format=%H|%aI", "--", path], cwd=repo_root)
    if rc != 0 or not out:
        return {"last_commit": None, "last_commit_at": None}
    commit, when = out.split("|", 1)
    return {"last_commit": commit, "last_commit_at": when}


def get_first_seen(path: str, repo_root: Path) -> Dict[str, Optional[str]]:
    rc, out = run_git(["log", "--diff-filter=A", "--format=%H|%aI", "--", path], cwd=repo_root)
    if rc != 0 or not out:
        return {"first_seen_commit": None, "first_seen_at": None}
    line = out.splitlines()[-1]
    commit, when = line.split("|", 1)
    return {"first_seen_commit": commit, "first_seen_at": when}


def build_inventory(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    metrics: Optional[Dict[str, Any]] = None,
    max_objects_preview: int = 300,
    max_files: Optional[int] = None,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> SkillRunResult:
    objects_jsonl = run_dir / "reports" / "inventory_objects.jsonl"
    if objects_jsonl.exists():
        objects_jsonl.unlink()

    tracked = tracked_set(repo_root)
    zone_counts: Counter[str] = Counter()
    artifact_counts: Counter[str] = Counter()
    top_level_dirs: Counter[str] = Counter()
    objects_preview: List[Dict[str, Any]] = []
    total_files = 0
    warnings: List[str] = []
    rejected = 0

    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}
    stop_scan = False
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            if max_files is not None and total_files >= max_files:
                warnings.append(f"inventory file limit applied: {max_files}")
                stop_scan = True
                break
            total_files += 1
            abs_path = Path(root) / name
            rel = abs_path.resolve().relative_to(repo_root.resolve()).as_posix()
            obj = classify_path(rel, repo_root, tracked_hint=(rel in tracked))
            route = route_for_object(obj)
            obj.update(
                {
                    "recommended_next_route": route["route_to"],
                    "routing_reason": route["routing_reason"],
                    "route_confidence": route["route_confidence"],
                }
            )
            if route["verdict"].startswith("REJECT") or "BLOCK" in route["verdict"]:
                rejected += 1
            zone_counts[obj["zone_class"]] += 1
            artifact_counts[obj["artifact_type"]] += 1
            top_level_dirs[rel.split("/", 1)[0]] += 1
            append_jsonl(objects_jsonl, obj)
            if len(objects_preview) < max_objects_preview:
                objects_preview.append(obj)
            if progress_hook and total_files % 200 == 0:
                progress_hook(
                    {
                        "files_scanned": total_files,
                        "warnings_count": len(warnings),
                        "rejected_count": rejected,
                    }
                )
        if stop_scan:
            break

    if total_files > max_objects_preview:
        warnings.append("objects preview truncated; use inventory_objects.jsonl for full map")

    report = {
        "report_type": "REPO_INVENTORY_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo_root),
        "git_head": git_head(repo_root),
        "total_files": total_files,
        "zone_counts": dict(zone_counts),
        "artifact_counts": dict(artifact_counts),
        "top_level_dirs": dict(top_level_dirs),
        "objects_preview": objects_preview,
        "objects_jsonl_path": str(objects_jsonl),
        "warnings": warnings,
        "rejected_count": rejected,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "inventory_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="build_repo_inventory",
        input_refs=[str(repo_root)],
        outputs=[str(report_path), str(objects_jsonl)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "build_repo_inventory", receipt)
    if metrics is not None:
        metrics["files_scanned"] += total_files
        metrics["files_classified"] += total_files
        metrics["objects_considered"] += total_files
        metrics["warnings_count"] += len(warnings)
        metrics["rejected_count"] += rejected
        metrics["routes_made"] += total_files
        metrics["receipts_written"] += 1
    return SkillRunResult("build_repo_inventory", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def iter_inventory_objects(inventory_report_path: Path) -> Iterable[Dict[str, Any]]:
    report = read_json(inventory_report_path)
    raw = str(report.get("objects_jsonl_path", "")).strip()
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = (inventory_report_path.parent / path).resolve()
        if path.exists() and path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    yield json.loads(line)
            return
    for obj in report.get("objects_preview", []):
        yield obj


def build_provenance_index(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    inventory_report_path: Path,
    metrics: Optional[Dict[str, Any]] = None,
    limit: int = 500,
) -> SkillRunResult:
    entries: List[Dict[str, Any]] = []
    warnings: List[str] = []
    considered = 0

    for idx, obj in enumerate(iter_inventory_objects(inventory_report_path)):
        if idx >= limit:
            warnings.append(f"provenance entry limit applied: {limit}")
            break
        considered += 1
        path = str(obj.get("path", ""))
        tracked = bool(obj.get("git_tracked", False))
        last_commit = get_last_commit(path, repo_root) if tracked else {"last_commit": None, "last_commit_at": None}
        first_seen = get_first_seen(path, repo_root) if tracked else {"first_seen_commit": None, "first_seen_at": None}
        entries.append(
            {
                "path": path,
                "git_tracked": tracked,
                "git_head_seen": git_head(repo_root),
                "source_type": "commit" if tracked else ("runtime" if "RUNS/" in path or "RUNTIME/" in path else "unknown"),
                "source_id": last_commit["last_commit"],
                "first_seen": first_seen["first_seen_at"],
                "created_by": "unknown",
                "verified_by": "git",
                "trust_status": obj.get("trust_level", "UNKNOWN"),
                "last_classification": {
                    "zone_class": obj.get("zone_class"),
                    "artifact_type": obj.get("artifact_type"),
                    "risk_level": obj.get("risk_level"),
                    "confidence": obj.get("classification_confidence"),
                },
                "last_commit": last_commit["last_commit"],
                "last_commit_at": last_commit["last_commit_at"],
                "first_seen_commit": first_seen["first_seen_commit"],
            }
        )

    report = {
        "report_type": "PROVENANCE_INDEX_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "inventory_report_path": str(inventory_report_path),
        "entry_count": len(entries),
        "entries": entries,
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "provenance_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="build_provenance_index",
        input_refs=[str(inventory_report_path)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "build_provenance_index", receipt)
    if metrics is not None:
        metrics["objects_considered"] += considered
        metrics["warnings_count"] += len(warnings)
        metrics["receipts_written"] += 1
    return SkillRunResult("build_provenance_index", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def _freshness_marker(last_commit_at: Optional[str]) -> str:
    if not last_commit_at:
        return "UNKNOWN"
    try:
        dt = datetime.fromisoformat(last_commit_at.replace("Z", "+00:00"))
    except Exception:
        return "UNKNOWN"
    delta_days = (datetime.now(timezone.utc) - dt).days
    if delta_days <= 1:
        return "COMMITTED_TODAY"
    if delta_days <= 7:
        return "COMMITTED_THIS_WEEK"
    if delta_days <= 30:
        return "COMMITTED_THIS_MONTH"
    return "OLDER"


def _candidate_reason(obj: Dict[str, Any]) -> str:
    artifact = obj.get("artifact_type")
    zone = obj.get("zone_class")
    if artifact == "SCRIPT":
        return "Script candidate for controlled reuse/hardening."
    if artifact in {"POLICY_DOC", "DOCTRINE_DOC"}:
        return "Policy/doctrine candidate for governance alignment."
    if zone == "CANON_CORE":
        return "Canon-side reference candidate; requires strict review."
    if zone == "ADVISORY":
        return "Advisory candidate; do not promote without evidence."
    return "General candidate for Administratum review."


def _review_priority(obj: Dict[str, Any]) -> str:
    risk = obj.get("risk_level", "LOW")
    if risk in {"CRITICAL", "HIGH"}:
        return "P0"
    if risk == "MEDIUM":
        return "P1"
    return "P2"


def _recommended_action(obj: Dict[str, Any]) -> str:
    route = route_for_object(obj)
    if route["verdict"].startswith("REJECT") or "BLOCK" in route["verdict"]:
        return "Reject and escalate to Custodes/Inquisition."
    if obj.get("artifact_type") == "SCRIPT":
        return "Mechanicus review before any promotion."
    if obj.get("zone_class") == "PRIVATE_CONTEXT":
        return "Do not export; apply redaction/no-export rules."
    return "Add to merge preparation summary for controlled review."


def find_useful_candidates(
    run_id: str,
    run_dir: Path,
    inventory_report_path: Path,
    repo_root: Optional[Path] = None,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    repo_root = repo_root or REPO_ROOT
    scripts: List[Dict[str, Any]] = []
    gates: List[Dict[str, Any]] = []
    policies: List[Dict[str, Any]] = []
    dashboards: List[Dict[str, Any]] = []
    memories: List[Dict[str, Any]] = []
    considered = 0

    for obj in iter_inventory_objects(inventory_report_path):
        considered += 1
        path = str(obj.get("path", ""))
        low = path.lower()
        lc = get_last_commit(path, repo_root) if obj.get("git_tracked") else {"last_commit": None, "last_commit_at": None}
        candidate = {
            "path": path,
            "risk_level": obj.get("risk_level"),
            "zone_class": obj.get("zone_class"),
            "artifact_type": obj.get("artifact_type"),
            "routing": route_for_object(obj),
            "reason": _candidate_reason(obj),
            "recommended_action": _recommended_action(obj),
            "provenance_marker": "KNOWN_COMMITTED" if obj.get("git_tracked") else "UNKNOWN_SOURCE",
            "freshness_marker": _freshness_marker(lc.get("last_commit_at")),
            "legacy_or_advisory_marker": "ADVISORY_OR_LEGACY" if "advisory" in low or "archive" in low else "ACTIVE",
            "review_priority": _review_priority(obj),
        }

        if obj.get("artifact_type") == "SCRIPT":
            scripts.append(candidate)
        if "/gates/" in low or "gate_" in low:
            gates.append(candidate)
        if "/policies/" in low or "policy" in low:
            policies.append(candidate)
        if "sanctum" in low or "dashboard" in low:
            dashboards.append(candidate)
        if "/memory/" in low:
            memories.append(candidate)

    warnings: List[str] = []
    requires_owner = any(c["review_priority"] == "P0" for c in scripts + gates + policies + dashboards + memories)
    if requires_owner:
        warnings.append("high-priority candidates require owner decision review")

    report = {
        "report_type": "USEFUL_CANDIDATES_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "inventory_report_path": str(inventory_report_path),
        "top_summary": {
            "scripts": len(scripts),
            "gates": len(gates),
            "policies": len(policies),
            "dashboards": len(dashboards),
            "memory_items": len(memories),
        },
        "script_candidates": scripts[:150],
        "gate_candidates": gates[:150],
        "policy_candidates": policies[:150],
        "dashboard_candidates": dashboards[:150],
        "memory_candidates": memories[:150],
        "review_priority_distribution": {
            "P0": sum(1 for c in scripts + gates + policies + dashboards + memories if c["review_priority"] == "P0"),
            "P1": sum(1 for c in scripts + gates + policies + dashboards + memories if c["review_priority"] == "P1"),
            "P2": sum(1 for c in scripts + gates + policies + dashboards + memories if c["review_priority"] == "P2"),
        },
        "requires_mechanicus_review": len(scripts) > 0,
        "requires_inquisition_review": any(c["risk_level"] in {"HIGH", "CRITICAL"} for c in scripts + gates + policies),
        "requires_owner_decision": requires_owner,
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "useful_candidates_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="find_useful_candidates",
        input_refs=[str(inventory_report_path)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "find_useful_candidates", receipt)
    if metrics is not None:
        metrics["objects_considered"] += considered
        metrics["warnings_count"] += len(warnings)
        metrics["routes_made"] += considered
        metrics["receipts_written"] += 1
    return SkillRunResult("find_useful_candidates", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def detect_dirty_runtime_outputs(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    rules = rule_json("dirt_detection_rules.json")
    dirty_patterns = [p.replace("\\", "/") for p in rules.get("dirty_patterns", [])]
    allowed_runtime = [p.replace("\\", "/") for p in rules.get("allowed_runtime_roots", [])]

    tracked = tracked_set(repo_root)
    tracked_runtime_paths: List[str] = []
    for rel in tracked:
        norm = rel.replace("\\", "/")
        if any(norm.startswith(prefix) for prefix in allowed_runtime):
            continue
        if any(norm.startswith(prefix) for prefix in dirty_patterns):
            tracked_runtime_paths.append(norm)

    status_lines = git_status_porcelain(repo_root)
    modified_paths = [line[3:].replace("\\", "/") for line in status_lines if len(line) > 3]
    modified_runtime_paths = [
        p
        for p in modified_paths
        if any(marker in p for marker in ["RUNS/", "RUNTIME/", "state_delta", "checkpoint", "trace"])
        and not any(p.startswith(prefix) for prefix in allowed_runtime)
    ]

    warnings: List[str] = []
    if tracked_runtime_paths:
        warnings.append("tracked runtime-pattern paths detected outside allowed runs roots")
    if modified_runtime_paths:
        warnings.append("runtime-like modified paths detected outside allowed runs roots")

    dirty_detected = bool(tracked_runtime_paths or modified_runtime_paths)
    report = {
        "report_type": "DIRTY_RUNTIME_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "dirty_runtime_detected": dirty_detected,
        "tracked_runtime_paths": tracked_runtime_paths,
        "modified_runtime_paths": modified_runtime_paths,
        "recommended_action": (
            "Keep runtime files under IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT and avoid tracked architecture pollution."
            if dirty_detected
            else "No runtime pollution detected by current rules."
        ),
        "architectural_fix": "RUNS_LAYER_ONLY",
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if dirty_detected else "PASS",
    }
    report_path = run_dir / "reports" / "dirty_runtime_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="detect_dirty_runtime_outputs",
        input_refs=[str(repo_root)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "detect_dirty_runtime_outputs", receipt)
    if metrics is not None:
        metrics["warnings_count"] += len(warnings)
        metrics["rejected_count"] += len(tracked_runtime_paths)
        metrics["receipts_written"] += 1
    return SkillRunResult("detect_dirty_runtime_outputs", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def route_to_organs(
    run_id: str,
    run_dir: Path,
    findings: List[Dict[str, Any]],
    requested_action: str = "",
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    routes: List[Dict[str, Any]] = []
    warnings: List[str] = []
    rejected = 0
    for item in findings:
        cls = classify_path(str(item.get("path", "")), REPO_ROOT)
        decision = route_for_object(cls, requested_action=requested_action)
        combined = dict(cls)
        combined.update(decision)
        routes.append(combined)
        if decision["verdict"].startswith("REJECT") or "BLOCK" in decision["verdict"]:
            rejected += 1
            warnings.append(f"rejected requested action for {cls['path']}")

    verdict = "PASS"
    if rejected > 0:
        verdict = "BLOCKED"
    report = {
        "report_type": "ROUTING_RECOMMENDATIONS_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "requested_action": requested_action,
        "routes": routes,
        "route_count": len(routes),
        "warnings": warnings,
        "verdict": verdict,
    }
    report_path = run_dir / "reports" / "routing_recommendations_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="route_to_organs",
        input_refs=[requested_action or "findings"],
        outputs=[str(report_path)],
        verdict=verdict,
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "route_to_organs", receipt)
    if metrics is not None:
        metrics["objects_considered"] += len(findings)
        metrics["routes_made"] += len(findings)
        metrics["warnings_count"] += len(warnings)
        metrics["rejected_count"] += rejected
        metrics["receipts_written"] += 1
    return SkillRunResult("route_to_organs", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def _scan_context_root(
    root: Path,
    scope: str,
    metrics: Optional[Dict[str, Any]] = None,
    max_entries: int = 10000,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    entries: List[Dict[str, Any]] = []
    warnings: List[str] = []
    if not root.exists():
        warnings.append(f"context root missing: {root}")
        return entries, warnings

    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for file_name in files:
            count += 1
            if count > max_entries:
                warnings.append(f"context entry limit reached for {scope}: {max_entries}")
                return entries, warnings
            p = Path(current) / file_name
            stat = p.stat()
            rel = p.resolve().relative_to(root.resolve()).as_posix()
            entry = {
                "path": str(p.resolve()),
                "relative_path": rel,
                "scope": scope,
                "path_hash": stable_id("ctx", str(p.resolve())),
                "size_bytes": stat.st_size,
                "mtime_utc": iso_from_ts(stat.st_mtime),
                "extension": p.suffix.lower(),
                "artifact_type": classify_artifact_type(str(p)),
                "name_risk_marker": _has_private_name_risk(file_name),
            }
            entries.append(entry)
            if metrics is not None:
                metrics["files_scanned"] += 1
                metrics["files_classified"] += 1
                metrics["objects_considered"] += 1
            if progress_hook and count % 250 == 0:
                progress_hook({"scope": scope, "objects_scanned": count, "warnings_count": len(warnings)})
    return entries, warnings


def scan_imperium_context(
    run_id: str,
    run_dir: Path,
    local_root: Path = DEFAULT_CONTEXT_LOCAL,
    private_root: Path = DEFAULT_CONTEXT_PRIVATE,
    metrics: Optional[Dict[str, Any]] = None,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> SkillRunResult:
    local_entries, local_warnings = _scan_context_root(local_root, "LOCAL_CONTEXT", metrics, progress_hook=progress_hook)
    private_entries, private_warnings = _scan_context_root(
        private_root,
        "PRIVATE_CONTEXT",
        metrics,
        progress_hook=progress_hook,
    )
    warnings = local_warnings + private_warnings
    entries = local_entries + private_entries
    index_jsonl = run_dir / "reports" / "imperium_context_index.jsonl"
    if index_jsonl.exists():
        index_jsonl.unlink()
    for entry in entries:
        append_jsonl(index_jsonl, entry)

    report = {
        "report_type": "IMPERIUM_CONTEXT_SCAN_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "local_root": str(local_root),
        "private_root": str(private_root),
        "entry_count": len(entries),
        "scope_counts": {
            "LOCAL_CONTEXT": len(local_entries),
            "PRIVATE_CONTEXT": len(private_entries),
        },
        "metadata_only": True,
        "entries_preview": entries[:200],
        "index_jsonl_path": str(index_jsonl),
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "imperium_context_scan_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="scan_imperium_context",
        input_refs=[str(local_root), str(private_root)],
        outputs=[str(report_path), str(index_jsonl)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "scan_imperium_context", receipt)
    if metrics is not None:
        metrics["warnings_count"] += len(warnings)
        metrics["receipts_written"] += 1
    return SkillRunResult("scan_imperium_context", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def classify_local_context(
    run_id: str,
    run_dir: Path,
    context_scan_report_path: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    scan = read_json(context_scan_report_path)
    entries = scan.get("entries_preview", [])
    if not entries:
        idx_path = Path(scan.get("index_jsonl_path", ""))
        if idx_path.exists():
            entries = [json.loads(line) for line in idx_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    classified: List[Dict[str, Any]] = []
    redaction_patterns: List[str] = []
    warnings: List[str] = []
    high_risk = 0
    for entry in entries:
        scope = entry.get("scope", "LOCAL_CONTEXT")
        name_risk = bool(entry.get("name_risk_marker", False))
        risk = "LOW"
        reason = []
        if scope == "PRIVATE_CONTEXT":
            risk = "HIGH"
            reason.append("private scope")
        if name_risk:
            risk = "CRITICAL"
            reason.append("sensitive filename marker")
            redaction_patterns.append(Path(str(entry.get("path", ""))).name)
        classified.append(
            {
                **entry,
                "context_class": scope,
                "risk_level": risk,
                "risk_reason": "; ".join(reason) if reason else "metadata-only safe",
                "no_git_export": scope == "PRIVATE_CONTEXT" or name_risk,
            }
        )
        if risk in {"HIGH", "CRITICAL"}:
            high_risk += 1

    no_git_export_rules = [
        "Never commit PRIVATE_CONTEXT files or content into repository.",
        "Export only metadata summaries unless owner-approved secure path is provided.",
        "Apply redaction to sensitive filename markers before handoff.",
    ]
    if high_risk > 0:
        warnings.append("high-risk local/private context entries detected")

    report = {
        "report_type": "LOCAL_CONTEXT_CLASSIFICATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "source_scan_report": str(context_scan_report_path),
        "classified_count": len(classified),
        "high_risk_count": high_risk,
        "classified_preview": classified[:250],
        "no_git_export_rules": no_git_export_rules,
        "redaction_guidance": sorted(set(redaction_patterns))[:200],
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "local_context_classification_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="classify_local_context",
        input_refs=[str(context_scan_report_path)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "classify_local_context", receipt)
    if metrics is not None:
        metrics["files_classified"] += len(classified)
        metrics["objects_considered"] += len(classified)
        metrics["warnings_count"] += len(warnings)
        metrics["rejected_count"] += high_risk
        metrics["receipts_written"] += 1
    return SkillRunResult("classify_local_context", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def detect_private_export_risk(
    run_id: str,
    run_dir: Path,
    local_context_report_path: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    cls = read_json(local_context_report_path)
    preview = cls.get("classified_preview", [])
    risky = [item for item in preview if item.get("risk_level") in {"HIGH", "CRITICAL"} or item.get("no_git_export")]
    warnings = []
    if risky:
        warnings.append("private export risk detected; no-git-export rules enforced")

    report = {
        "report_type": "PRIVATE_EXPORT_RISK_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "source_local_context_report": str(local_context_report_path),
        "risk_count": len(risky),
        "risk_items_preview": risky[:200],
        "recommended_action": "Block git export and keep metadata-only continuity references.",
        "redaction_guidance": cls.get("redaction_guidance", []),
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if risky else "PASS",
    }
    report_path = run_dir / "reports" / "private_export_risk_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="detect_private_export_risk",
        input_refs=[str(local_context_report_path)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "detect_private_export_risk", receipt)
    if metrics is not None:
        metrics["objects_considered"] += len(preview)
        metrics["warnings_count"] += len(warnings)
        metrics["rejected_count"] += len(risky)
        metrics["receipts_written"] += 1
    return SkillRunResult("detect_private_export_risk", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def collect_reality_snapshot(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    status_lines = git_status_porcelain(repo_root)
    report = {
        "report_type": "REALITY_SNAPSHOT_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo_root),
        "git_head": git_head(repo_root),
        "git_branch": git_branch(repo_root),
        "dirty_tree": bool(status_lines),
        "dirty_paths": [line[3:] for line in status_lines if len(line) > 3][:500],
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "verdict": "PASS",
    }
    report_path = run_dir / "reports" / "reality_snapshot_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="collect_reality_snapshot",
        input_refs=[str(repo_root)],
        outputs=[str(report_path)],
        verdict="PASS",
        warnings=[],
    )
    receipt_path = write_skill_receipt(run_dir, "collect_reality_snapshot", receipt)
    if metrics is not None:
        metrics["objects_considered"] += 1
        metrics["receipts_written"] += 1
    return SkillRunResult("collect_reality_snapshot", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def collect_continuity_pack(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    include_context: bool,
    metrics: Optional[Dict[str, Any]] = None,
    live_metrics_snapshot: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    pack_dir = run_dir / "continuity_pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    included_refs: Dict[str, str] = {}
    report_candidates = [
        "inventory_report.json",
        "provenance_report.json",
        "useful_candidates_report.json",
        "dirty_runtime_report.json",
        "routing_recommendations_report.json",
        "local_context_classification_report.json",
        "private_export_risk_report.json",
        "reality_snapshot_report.json",
    ]
    for name in report_candidates:
        src = run_dir / "reports" / name
        if src.exists():
            included_refs[name] = str(src)

    loaded_reports: Dict[str, Dict[str, Any]] = {}
    for name, path_text in included_refs.items():
        path = Path(path_text)
        if path.suffix.lower() == ".json" and path.exists():
            try:
                loaded_reports[name] = read_json(path)
            except Exception:
                continue

    manifest = {
        "pack_type": "CONTINUITY_PACK",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "created_at_utc": now_utc(),
        "repo_head": git_head(repo_root),
        "repo_dirty": git_is_dirty(repo_root),
        "include_context": include_context,
        "included_refs_count": len(included_refs),
        "context_export_policy": "METADATA_ONLY_NO_GIT_EXPORT",
        "included_refs": included_refs,
        "safety": {
            "metadata_only_context": True,
            "private_content_exported": False,
            "no_git_export_rules_enforced": True,
        },
    }
    manifest_path = pack_dir / "continuity_pack_manifest.json"
    write_json(manifest_path, manifest)

    git_truth = {
        "repo_root": str(repo_root),
        "git_head": git_head(repo_root),
        "git_branch": git_branch(repo_root),
        "dirty": git_is_dirty(repo_root),
        "timestamp_utc": now_utc(),
    }
    current_git_truth_path = pack_dir / "current_git_truth.json"
    write_json(current_git_truth_path, git_truth)

    active_status = status_snapshot()
    active_status_path = pack_dir / "active_agent_status.json"
    write_json(active_status_path, active_status)

    reality = loaded_reports.get("reality_snapshot_report.json", {})
    reality_excerpt = {
        "git_head": reality.get("git_head"),
        "git_branch": reality.get("git_branch"),
        "dirty_tree": reality.get("dirty_tree"),
        "dirty_paths_preview": reality.get("dirty_paths", [])[:30],
        "runtime": reality.get("runtime", {}),
        "generated_at_utc": reality.get("generated_at_utc"),
    }
    reality_excerpt_path = pack_dir / "reality_snapshot_excerpt.json"
    write_json(reality_excerpt_path, reality_excerpt)

    private_cls = loaded_reports.get("local_context_classification_report.json", {})
    private_risk = loaded_reports.get("private_export_risk_report.json", {})
    private_safety = {
        "metadata_only_mode": True,
        "private_content_exported": False,
        "no_git_export_rules": private_cls.get("no_git_export_rules", []),
        "redaction_guidance": private_cls.get("redaction_guidance", []),
        "high_risk_count": private_cls.get("high_risk_count", 0),
        "private_export_risk_count": private_risk.get("risk_count", 0),
        "warnings": private_risk.get("warnings", []),
    }
    private_safety_path = pack_dir / "private_context_safety_report.json"
    write_json(private_safety_path, private_safety)

    useful = loaded_reports.get("useful_candidates_report.json", {})
    useful_refs_index = {
        "top_summary": useful.get("top_summary", {}),
        "review_priority_distribution": useful.get("review_priority_distribution", {}),
        "script_candidates_preview": useful.get("script_candidates", [])[:40],
        "gate_candidates_preview": useful.get("gate_candidates", [])[:40],
        "policy_candidates_preview": useful.get("policy_candidates", [])[:40],
    }
    useful_refs_index_path = pack_dir / "useful_refs_index.json"
    write_json(useful_refs_index_path, useful_refs_index)

    metrics_summary = metrics_summary_from_run(run_id, run_dir)
    if live_metrics_snapshot:
        metrics_summary["live_command_metrics_snapshot"] = live_metrics_snapshot
        aggregate = metrics_summary.get("aggregate", {})
        if int(aggregate.get("commands", 0)) == 0:
            aggregate["commands"] = 1
            aggregate["wall_clock_ms"] = int(live_metrics_snapshot.get("wall_clock_ms", 0))
            aggregate["process_cpu_seconds"] = float(live_metrics_snapshot.get("process_cpu_seconds", 0.0) or 0.0)
            aggregate["files_scanned"] = int(live_metrics_snapshot.get("files_scanned", 0))
            aggregate["files_classified"] = int(live_metrics_snapshot.get("files_classified", 0))
            aggregate["objects_considered"] = int(live_metrics_snapshot.get("objects_considered", 0))
            aggregate["warnings_count"] = int(live_metrics_snapshot.get("warnings_count", 0))
            aggregate["errors_count"] = int(live_metrics_snapshot.get("errors_count", 0))
            aggregate["output_bytes_total"] = int(live_metrics_snapshot.get("output_bytes_total", 0))
            aggregate["gpu_used"] = bool(live_metrics_snapshot.get("gpu_used", False))
            aggregate["gpu_reason"] = str(
                live_metrics_snapshot.get(
                    "gpu_reason",
                    "No GPU API/dependency invoked; Python stdlib/script-first execution.",
                )
            )
            aggregate["owner_wait_seconds"] = float(live_metrics_snapshot.get("owner_wait_seconds", 0.0) or 0.0)
            aggregate["run_cost_class"] = str(live_metrics_snapshot.get("run_cost_class", "UNSET"))
            metrics_summary["aggregate"] = aggregate
    metrics_summary_path = pack_dir / "metrics_summary.json"
    write_json(metrics_summary_path, metrics_summary)

    kpd_score, thinking_quality = kpd_from_reports(run_id, run_dir)
    kpd_path = pack_dir / "kpd_score.json"
    thinking_path = pack_dir / "thinking_quality_score.json"
    write_json(kpd_path, kpd_score)
    write_json(thinking_path, thinking_quality)

    routing = loaded_reports.get("routing_recommendations_report.json", {})
    warnings_lines: List[str] = []
    for report_name, report_data in loaded_reports.items():
        for warning in report_data.get("warnings", []):
            warnings_lines.append(f"- [{report_name}] {warning}")
    if not warnings_lines:
        warnings_lines.append("- No warnings registered for included reports.")
    warnings_lines.extend(
        [
            "",
            "Owner decision points:",
            "- Any canon promotion recommendation.",
            "- Any deletion/mutation request.",
            "- Any private context export exception.",
        ]
    )
    warnings_decisions_path = pack_dir / "warnings_and_owner_decisions.md"
    warnings_decisions_path.write_text(
        "\n".join(["# Warnings and Owner Decisions", "", *warnings_lines, ""]) + "\n",
        encoding="utf-8",
    )

    owner_brief_lines = [
        "# Owner Readable Continuity Brief",
        "",
        f"- run_id: {run_id}",
        f"- git_head: {git_truth['git_head']}",
        f"- repo_dirty: {str(git_truth['dirty']).lower()}",
        f"- included_refs_count: {len(included_refs)}",
        f"- context_mode: {'metadata_only' if include_context else 'disabled'}",
        f"- kpd_verdict: {kpd_score.get('verdict', 'UNKNOWN')}",
        f"- trust_verdict: {kpd_score.get('trust_verdict', 'UNKNOWN')}",
        "",
        "## Top continuity points",
        "- Repository truth and runtime truth captured.",
        "- Private context remains metadata-only with no-git-export rules.",
        "- Useful references indexed for follow-up Servitor work.",
        "- Owner decisions isolated in dedicated warnings document.",
        "",
    ]
    owner_brief_path = pack_dir / "owner_readable_continuity_brief.md"
    owner_brief_path.write_text("\n".join(owner_brief_lines), encoding="utf-8")

    handoff_brief_lines = [
        "# Agent Handoff Brief",
        "",
        f"- run_id: {run_id}",
        "- next_servitor_focus:",
        "  - review P0/P1 useful candidates;",
        "  - validate high-risk routes with Custodes/Inquisition;",
        "  - keep private context metadata-only;",
        "  - verify pack against reality before acting on stale refs.",
        "",
        "## Routing preview",
    ]
    for route_item in routing.get("routes", [])[:20]:
        path = route_item.get("path", "unknown")
        route_to = ",".join(route_item.get("route_to", []))
        handoff_brief_lines.append(f"- {path} -> {route_to}")
    handoff_brief_lines.append("")
    handoff_brief_path = pack_dir / "agent_handoff_brief.md"
    handoff_brief_path.write_text("\n".join(handoff_brief_lines), encoding="utf-8")

    summary_path = pack_dir / "continuity_pack_summary.md"
    summary_lines = [
        "# Continuity Pack Summary",
        "",
        f"- run_id: {run_id}",
        f"- repo_head: {manifest['repo_head']}",
        f"- repo_dirty: {str(manifest['repo_dirty']).lower()}",
        f"- include_context: {str(include_context).lower()}",
        f"- refs_count: {len(included_refs)}",
        f"- kpd_verdict: {kpd_score.get('verdict', 'UNKNOWN')}",
        f"- trust_verdict: {kpd_score.get('trust_verdict', 'UNKNOWN')}",
        "",
    ]
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    maturity_capsule_path = pack_dir / "continuity_maturity_capsule.json"
    write_json(
        maturity_capsule_path,
        {
            "report_type": "CONTINUITY_MATURITY_CAPSULE",
            "agent_id": "ADMINISTRATUM_AGENT",
            "run_id": run_id,
            "generated_at_utc": now_utc(),
            "status": "PENDING_FINALIZATION",
        },
    )

    pack_receipt = {
        "receipt_type": "CONTINUITY_PACK_RECEIPT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "timestamp_utc": now_utc(),
        "outputs": [
            str(manifest_path),
            str(summary_path),
            str(owner_brief_path),
            str(handoff_brief_path),
            str(reality_excerpt_path),
            str(current_git_truth_path),
            str(active_status_path),
            str(warnings_decisions_path),
            str(useful_refs_index_path),
            str(private_safety_path),
            str(metrics_summary_path),
            str(kpd_path),
            str(thinking_path),
            str(maturity_capsule_path),
        ],
        "mutated_canon": False,
        "private_content_exported": False,
        "include_context": include_context,
    }
    pack_receipt_path = pack_dir / "receipt.json"
    write_json(pack_receipt_path, pack_receipt)

    required_files = [
        manifest_path,
        summary_path,
        owner_brief_path,
        handoff_brief_path,
        reality_excerpt_path,
        current_git_truth_path,
        active_status_path,
        warnings_decisions_path,
        useful_refs_index_path,
        private_safety_path,
        metrics_summary_path,
        kpd_path,
        maturity_capsule_path,
        pack_receipt_path,
    ]
    present_required = sum(1 for p in required_files if p.exists())
    pack_quality = {
        "required_files_total": len(required_files),
        "required_files_present": present_required,
        "required_files_missing": [str(p.name) for p in required_files if not p.exists()],
        "quality_verdict": "PASS" if present_required == len(required_files) else "PASS_WITH_WARNINGS",
    }
    continuity_limitations: List[str] = []
    if bool(manifest.get("repo_dirty")):
        continuity_limitations.append("Repository was dirty during continuity pack creation.")
    if include_context:
        continuity_limitations.append("Context references are metadata-only and not content-export ready.")
    if int(private_safety.get("private_export_risk_count", 0) or 0) > 0:
        continuity_limitations.append("Private export risk items detected; requires strict no-git-export handling.")
    if int(len(included_refs)) < 4:
        continuity_limitations.append("Low included refs count reduces standalone handoff confidence.")
    if pack_quality["quality_verdict"] != "PASS":
        continuity_limitations.append("Required continuity files are incomplete.")

    if pack_quality["quality_verdict"] != "PASS" or bool(manifest.get("repo_dirty")):
        maturity_verdict = "NOT_READY_FOR_SOLE_HANDOFF"
    elif continuity_limitations:
        maturity_verdict = "PARTIAL"
    elif (
        kpd_score.get("trust_verdict") in {"TRUSTED_FOR_BASE_USE", "TRUSTED_WITH_WARNINGS"}
        and len(included_refs) >= 6
        and not include_context
    ):
        maturity_verdict = "READY_CANDIDATE"
    else:
        maturity_verdict = "PARTIAL"

    recommended_handoff_method = (
        "Run verify-pack-against-reality immediately before next Servitor action and include Owner checkpoint."
        if maturity_verdict == "NOT_READY_FOR_SOLE_HANDOFF"
        else (
            "Use pack with mandatory verify-pack-against-reality pre-flight for each downstream execution."
            if maturity_verdict == "PARTIAL"
            else "Use as primary handoff capsule with lightweight reality re-check."
        )
    )

    key_receipts = sorted(str(p) for p in (run_dir / "receipts").glob("*_receipt.json"))
    maturity_capsule = {
        "report_type": "CONTINUITY_MATURITY_CAPSULE",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "repo_truth": git_truth,
        "repo_dirty": bool(git_truth.get("dirty")),
        "included_refs_count": len(included_refs),
        "included_refs": included_refs,
        "context_export_policy": "METADATA_ONLY_NO_GIT_EXPORT",
        "private_export_safety": private_safety,
        "key_reports": included_refs,
        "key_receipts": key_receipts[:80],
        "limitations": continuity_limitations,
        "recommended_next_handoff_method": recommended_handoff_method,
        "self_verdict": maturity_verdict,
    }
    write_json(maturity_capsule_path, maturity_capsule)
    manifest["maturity_capsule_path"] = str(maturity_capsule_path)
    manifest["self_verdict"] = maturity_verdict
    manifest["limitations"] = continuity_limitations
    manifest["recommended_next_handoff_method"] = recommended_handoff_method
    write_json(manifest_path, manifest)

    owner_brief_lines.extend(
        [
            "## Maturity capsule",
            f"- self_verdict: {maturity_verdict}",
            f"- recommended_next_handoff_method: {recommended_handoff_method}",
            f"- limitations_count: {len(continuity_limitations)}",
            "",
        ]
    )
    for limitation in continuity_limitations:
        owner_brief_lines.append(f"- limitation: {limitation}")
    owner_brief_lines.append("")
    owner_brief_path.write_text("\n".join(owner_brief_lines), encoding="utf-8")

    summary_lines.extend(
        [
            "## Maturity capsule",
            f"- self_verdict: {maturity_verdict}",
            f"- recommended_next_handoff_method: {recommended_handoff_method}",
            f"- limitations_count: {len(continuity_limitations)}",
            "",
        ]
    )
    for limitation in continuity_limitations:
        summary_lines.append(f"- limitation: {limitation}")
    summary_lines.append("")
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    pack_verdict = "PASS_WITH_WARNINGS" if continuity_limitations else "PASS"
    report = {
        "report_type": "CONTINUITY_PACK_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "pack_dir": str(pack_dir),
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_path),
        "owner_brief_path": str(owner_brief_path),
        "agent_handoff_brief_path": str(handoff_brief_path),
        "reality_snapshot_excerpt_path": str(reality_excerpt_path),
        "current_git_truth_path": str(current_git_truth_path),
        "active_agent_status_path": str(active_status_path),
        "warnings_and_owner_decisions_path": str(warnings_decisions_path),
        "useful_refs_index_path": str(useful_refs_index_path),
        "private_context_safety_report_path": str(private_safety_path),
        "metrics_summary_path": str(metrics_summary_path),
        "kpd_score_path": str(kpd_path),
        "maturity_capsule_path": str(maturity_capsule_path),
        "continuity_pack_receipt_path": str(pack_receipt_path),
        "pack_quality": pack_quality,
        "included_refs_count": len(included_refs),
        "context_export_policy": "METADATA_ONLY_NO_GIT_EXPORT",
        "continuity_maturity_capsule": maturity_capsule,
        "warnings": continuity_limitations,
        "verdict": pack_verdict,
    }
    report_path = run_dir / "reports" / "continuity_pack_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="collect_continuity_pack",
        input_refs=[str(repo_root)],
        outputs=[
            str(report_path),
            str(manifest_path),
            str(summary_path),
            str(owner_brief_path),
            str(handoff_brief_path),
            str(maturity_capsule_path),
            str(pack_receipt_path),
        ],
        verdict=pack_verdict,
        warnings=continuity_limitations,
    )
    receipt_path = write_skill_receipt(run_dir, "collect_continuity_pack", receipt)
    if metrics is not None:
        metrics["objects_considered"] += len(included_refs)
        metrics["receipts_written"] += 1
    return SkillRunResult("collect_continuity_pack", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def build_agent_handoff_context(
    run_id: str,
    run_dir: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    continuity = run_dir / "reports" / "continuity_pack_report.json"
    routing = run_dir / "reports" / "routing_recommendations_report.json"
    dirty = run_dir / "reports" / "dirty_runtime_report.json"
    useful = run_dir / "reports" / "useful_candidates_report.json"

    handoff = {
        "report_type": "AGENT_HANDOFF_CONTEXT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "input_refs": {
            "continuity_pack_report": str(continuity) if continuity.exists() else None,
            "routing_report": str(routing) if routing.exists() else None,
            "dirty_runtime_report": str(dirty) if dirty.exists() else None,
            "useful_candidates_report": str(useful) if useful.exists() else None,
        },
        "servitor_next_actions": [
            "Validate high-risk route items with Custodes and Inquisition.",
            "Prioritize P0/P1 useful candidates for controlled review.",
            "Keep private-context findings metadata-only and no-git-export.",
            "Use continuity manifest for repeatable follow-up runs.",
        ],
        "owner_decision_points": [
            "Any private-export exception request.",
            "Any canon promotion recommendation.",
            "Any deletion or mutation request.",
        ],
        "verdict": "PASS",
    }
    report_path = run_dir / "reports" / "agent_handoff_context_report.json"
    write_json(report_path, handoff)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="build_agent_handoff_context",
        input_refs=[str(x) for x in [continuity, routing, dirty, useful] if x.exists()],
        outputs=[str(report_path)],
        verdict="PASS",
        warnings=[],
    )
    receipt_path = write_skill_receipt(run_dir, "build_agent_handoff_context", receipt)
    if metrics is not None:
        metrics["objects_considered"] += 4
        metrics["receipts_written"] += 1
    return SkillRunResult("build_agent_handoff_context", handoff, str(report_path), receipt, str(receipt_path), str(run_dir))


def verify_pack_against_reality(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    continuity_manifest_path: Path,
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    manifest = read_json(continuity_manifest_path)
    current_head = git_head(repo_root)
    current_dirty = git_is_dirty(repo_root)
    warnings: List[str] = []
    if manifest.get("repo_head") != current_head:
        warnings.append("repo_head_mismatch")
    if bool(manifest.get("repo_dirty")) != current_dirty:
        warnings.append("dirty_state_mismatch")

    report = {
        "report_type": "PACK_REALITY_VERIFICATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "manifest_path": str(continuity_manifest_path),
        "manifest_repo_head": manifest.get("repo_head"),
        "current_repo_head": current_head,
        "manifest_repo_dirty": manifest.get("repo_dirty"),
        "current_repo_dirty": current_dirty,
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "pack_reality_verification_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="verify_pack_against_reality",
        input_refs=[str(continuity_manifest_path)],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "verify_pack_against_reality", receipt)
    if metrics is not None:
        metrics["warnings_count"] += len(warnings)
        metrics["objects_considered"] += 1
        metrics["receipts_written"] += 1
    return SkillRunResult("verify_pack_against_reality", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def build_merge_preparation_summary(
    run_id: str,
    run_dir: Path,
    inventory_report: Dict[str, Any],
    provenance_report: Dict[str, Any],
    candidates_report: Dict[str, Any],
    dirty_runtime_report: Dict[str, Any],
    routing_report: Dict[str, Any],
    metrics: Optional[Dict[str, Any]] = None,
) -> SkillRunResult:
    warnings: List[str] = []
    if dirty_runtime_report.get("dirty_runtime_detected"):
        warnings.append("runtime pollution detected in repository")
    if candidates_report.get("requires_owner_decision"):
        warnings.append("owner decision required for high-priority candidates")

    summary = {
        "report_type": "MERGE_PREPARATION_SUMMARY",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "zone_map": inventory_report.get("zone_counts", {}),
        "artifact_map": inventory_report.get("artifact_counts", {}),
        "provenance_entries": provenance_report.get("entry_count", 0),
        "candidate_counts": candidates_report.get("top_summary", {}),
        "routing_preview": routing_report.get("routes", [])[:30],
        "dirty_runtime_detected": dirty_runtime_report.get("dirty_runtime_detected", False),
        "top_risks": [
            "No direct canon mutation by Administratum-Agent.",
            "Private/local context must remain metadata-only for export.",
            "High-risk findings require Custodes/Inquisition review.",
        ],
        "recommended_next_actions": [
            "Process P0/P1 candidate review queue before any promotion.",
            "Run continuity pack collection before handoff tasks.",
            "Use verify-pack-against-reality before downstream execution.",
            "Keep runtime outputs isolated under RUNS layer.",
        ],
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    report_path = run_dir / "reports" / "merge_preparation_summary.json"
    write_json(report_path, summary)
    summary_md = run_dir / "reports" / "merge_preparation_summary.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Merge Preparation Summary",
                "",
                f"- run_id: {run_id}",
                f"- verdict: {summary['verdict']}",
                f"- dirty_runtime_detected: {str(summary['dirty_runtime_detected']).lower()}",
                f"- provenance_entries: {summary['provenance_entries']}",
                "",
                "## Recommended Next Actions",
                *[f"- {x}" for x in summary["recommended_next_actions"]],
                "",
            ]
        ),
        encoding="utf-8",
    )
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="build_merge_preparation_summary",
        input_refs=["inventory_report", "provenance_report", "candidates_report", "dirty_runtime_report", "routing_report"],
        outputs=[str(report_path), str(summary_md)],
        verdict=summary["verdict"],
        warnings=warnings,
    )
    receipt_path = write_skill_receipt(run_dir, "build_merge_preparation_summary", receipt)
    if metrics is not None:
        metrics["warnings_count"] += len(warnings)
        metrics["receipts_written"] += 1
    return SkillRunResult("build_merge_preparation_summary", summary, str(report_path), receipt, str(receipt_path), str(run_dir))


def _unit_rows_from_json(path: Path, category: str, source: str) -> List[Dict[str, Any]]:
    data = read_json(path)
    rows: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                for child_key in value.keys():
                    rows.append(_unit_row(category, f"{key}.{child_key}", source, path))
            elif isinstance(value, list):
                for item in value:
                    rows.append(_unit_row(category, f"{key}:{str(item)[:80]}", source, path))
            else:
                rows.append(_unit_row(category, f"{key}={value}", source, path))
    return rows


def _unit_row(category: str, name: str, source: str, path: Path) -> Dict[str, Any]:
    return {
        "unit_id": stable_id("CU", category, name, str(path)),
        "category": category,
        "unit_name": name,
        "source_path": str(path.relative_to(REPO_ROOT).as_posix()),
        "source": source,
        "status": "admitted",
        "risk_level": "LOW" if category not in {"redaction_pattern", "path_recognizer"} else "MEDIUM",
        "provenance": "committed_workspace",
        "admission_path": "administratum_v1_hardening",
    }


def build_cu_index(
    run_id: str,
    run_dir: Path,
    metrics: Optional[Dict[str, Any]] = None,
    persist_state: bool = False,
) -> SkillRunResult:
    units: List[Dict[str, Any]] = []
    policy_dir = AGENT_ROOT / "POLICIES"
    for md in sorted(policy_dir.glob("*.md")):
        for line in md.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("- "):
                units.append(_unit_row("policy_snippet", line[2:120], "policy", md))

    rules_dir = AGENT_ROOT / "brain_node" / "rules"
    for js in sorted(rules_dir.glob("*.json")):
        units.extend(_unit_rows_from_json(js, "rule", "brain_rule"))

    for case_file in sorted((AGENT_ROOT / "brain_node" / "cases").glob("*.jsonl")):
        for line in case_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                name = row.get("case_id", stable_id("case", line))
                units.append(_unit_row("case", name, "brain_case", case_file))

    for score_file in sorted((AGENT_ROOT / "brain_node" / "scoring").glob("*.json")):
        score = read_json(score_file)
        for key in score.keys():
            units.append(_unit_row("scoring_weight", key, "scoring", score_file))

    for vocab_file in sorted((AGENT_ROOT / "brain_node" / "vocabulary").glob("*.json")):
        vocab = read_json(vocab_file)
        for key in vocab.keys():
            units.append(_unit_row("vocabulary_item", key, "vocabulary", vocab_file))

    for skill_manifest in sorted((AGENT_ROOT / "skills").glob("*/skill_manifest.json")):
        sm = read_json(skill_manifest)
        units.append(_unit_row("skill_definition", sm.get("skill_id", skill_manifest.parent.name), "skill_manifest", skill_manifest))

    for metric_name in METRIC_FIELDS:
        units.append(_unit_row("metric_definition", metric_name, "metrics_contract", REPO_ROOT / "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py"))

    for marker in PRIVATE_NAME_MARKERS:
        units.append(_unit_row("redaction_pattern", marker, "private_redaction", REPO_ROOT / "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py"))

    for marker in ["RUNS/", "RUNTIME/", "IMPERIUM_CONTEXT/LOCAL", "IMPERIUM_CONTEXT/PRIVATE"]:
        units.append(_unit_row("path_recognizer", marker, "path_classification", REPO_ROOT / "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py"))

    dedup: Dict[str, Dict[str, Any]] = {}
    for unit in units:
        dedup[unit["unit_id"]] = unit
    units = list(dedup.values())

    taxonomy = {
        "agent_id": "ADMINISTRATUM_AGENT",
        "generated_at_utc": now_utc(),
        "categories": CU_TAXONOMY,
        "status_values": ["pending", "candidate", "admitted", "deprecated"],
    }
    summary_counts: Counter[str] = Counter(u["category"] for u in units)
    summary = {
        "total_units": len(units),
        "category_counts": dict(summary_counts),
        "target_note": "Foundation only. No synthetic inflation toward 10k units.",
    }

    run_state_dir = run_dir / "reports" / "cu_state"
    run_state_dir.mkdir(parents=True, exist_ok=True)
    taxonomy_path = run_state_dir / "AGENT_UNIT_TAXONOMY.json"
    index_path = run_state_dir / "AGENT_UNIT_INDEX.json"
    summary_path = run_state_dir / "AGENT_UNIT_COUNT_SUMMARY.json"
    write_json(taxonomy_path, taxonomy)
    write_json(index_path, {"agent_id": "ADMINISTRATUM_AGENT", "generated_at_utc": now_utc(), "units": units})
    write_json(summary_path, summary)

    persistent_paths: Dict[str, Optional[str]] = {"taxonomy_path": None, "unit_index_path": None, "summary_path": None}
    if persist_state:
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        state_taxonomy = STATE_ROOT / "AGENT_UNIT_TAXONOMY.json"
        state_index = STATE_ROOT / "AGENT_UNIT_INDEX.json"
        state_summary = STATE_ROOT / "AGENT_UNIT_COUNT_SUMMARY.json"
        write_json(state_taxonomy, taxonomy)
        write_json(state_index, {"agent_id": "ADMINISTRATUM_AGENT", "generated_at_utc": now_utc(), "units": units})
        write_json(state_summary, summary)
        persistent_paths = {
            "taxonomy_path": str(state_taxonomy),
            "unit_index_path": str(state_index),
            "summary_path": str(state_summary),
        }

    report = {
        "report_type": "CU_SUMMARY_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "taxonomy_path": str(taxonomy_path),
        "unit_index_path": str(index_path),
        "summary_path": str(summary_path),
        "persist_state": persist_state,
        "persistent_state_paths": persistent_paths,
        "summary": summary,
        "verdict": "PASS",
    }
    report_path = run_dir / "reports" / "cu_summary_report.json"
    write_json(report_path, report)
    receipt = skill_receipt(
        run_id=run_id,
        skill_id="cu_summary",
        input_refs=[str(AGENT_ROOT)],
        outputs=[str(report_path), str(taxonomy_path), str(index_path), str(summary_path)],
        verdict="PASS",
        warnings=[],
    )
    receipt_path = write_skill_receipt(run_dir, "cu_summary", receipt)
    if metrics is not None:
        metrics["objects_considered"] += len(units)
        metrics["receipts_written"] += 1
    return SkillRunResult("cu_summary", report, str(report_path), receipt, str(receipt_path), str(run_dir))


def kpd_from_reports(run_id: str, run_dir: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    report_dir = run_dir / "reports"
    receipts_dir = run_dir / "receipts"
    warnings = 0
    rejected = 0
    route_conf = []
    class_conf = []
    provenance_completeness = 0.0
    outputs_count = 0

    for rep in report_dir.glob("*.json"):
        outputs_count += 1
        data = read_json(rep)
        warnings += len(data.get("warnings", []))
        rejected += int(data.get("rejected_count", 0))
        for route in data.get("routes", []):
            if "route_confidence" in route:
                route_conf.append(float(route["route_confidence"]))
        for obj in data.get("objects_preview", []):
            if "classification_confidence" in obj:
                class_conf.append(float(obj["classification_confidence"]))
        if data.get("report_type") == "PROVENANCE_INDEX_REPORT":
            entries = data.get("entries", [])
            if entries:
                complete = sum(1 for e in entries if e.get("source_type") and e.get("trust_status"))
                provenance_completeness = complete / len(entries)

    receipt_count = len(list(receipts_dir.glob("*.json")))
    route_quality = sum(route_conf) / len(route_conf) if route_conf else 0.55
    class_quality = sum(class_conf) / len(class_conf) if class_conf else 0.55
    evidence_quality = min(1.0, receipt_count / 6.0)
    safety = max(0.0, 1.0 - (warnings * 0.02 + rejected * 0.03))
    owner_action = min(1.0, outputs_count / 8.0)
    servitor_action = min(1.0, outputs_count / 9.0)
    usefulness = min(1.0, outputs_count / 10.0)
    cost_eff = 0.78
    warning_penalty = min(0.5, warnings * 0.03)
    unknown_penalty = max(0.0, 0.2 - class_quality * 0.15)
    runtime_cost_penalty = min(0.3, rejected * 0.02)
    total_score_raw = (
        usefulness * 0.15
        + route_quality * 0.18
        + evidence_quality * 0.18
        + safety * 0.18
        + cost_eff * 0.08
        + owner_action * 0.11
        + servitor_action * 0.12
        - warning_penalty
        - unknown_penalty
        - runtime_cost_penalty
    )
    kpd_score = max(0.0, min(1.0, total_score_raw))
    if kpd_score >= 0.78:
        trust_verdict = "TRUSTED_FOR_BASE_USE"
    elif kpd_score >= 0.58:
        trust_verdict = "TRUSTED_WITH_WARNINGS"
    elif kpd_score >= 0.35:
        trust_verdict = "NOT_TRUSTED"
    else:
        trust_verdict = "BLOCKED"

    unproven_claims: List[str] = []
    if outputs_count < 5:
        unproven_claims.append("insufficient_output_surface_for_confident_handoff")
    if route_conf == []:
        unproven_claims.append("route_confidence_not_observed_in_reports")
    if provenance_completeness == 0.0:
        unproven_claims.append("provenance_completeness_not_observed")

    component_scores = {
        "usefulness": round(usefulness, 3),
        "evidence": round(evidence_quality, 3),
        "safety": round(safety, 3),
        "cost_efficiency": round(cost_eff, 3),
        "owner_actionability": round(owner_action, 3),
        "servitor_actionability": round(servitor_action, 3),
        "route_quality": round(route_quality, 3),
        "warning_penalty": round(warning_penalty, 3),
        "unknown_penalty": round(unknown_penalty, 3),
        "runtime_cost_penalty": round(runtime_cost_penalty, 3),
        "total_score": round(kpd_score, 3),
    }

    kpd = {
        "report_type": "KPD_SCORE",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "component_scores": component_scores,
        "explanation": "KPD combines usefulness, evidence, safety, actionability and explicit penalties.",
        "unproven_claims": unproven_claims,
        "trust_verdict": trust_verdict,
        "score_0_to_1": round(kpd_score, 3),
        "score_0_to_100": round(kpd_score * 100, 1),
        "verdict": "PASS" if kpd_score >= 0.75 else ("PASS_WITH_WARNINGS" if kpd_score >= 0.55 else "BLOCKED"),
    }

    thinking = {
        "report_type": "THINKING_QUALITY_SCORE",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "component_scores": {
            "classification_confidence_quality": round(class_quality, 3),
            "route_appropriateness": round(route_quality, 3),
            "risk_detection_quality": round(min(1.0, 0.6 + warnings * 0.03), 3),
            "evidence_linking_quality": round(evidence_quality, 3),
            "provenance_completeness": round(provenance_completeness if provenance_completeness else 0.65, 3),
            "unknown_handling_quality": round(max(0.2, class_quality - 0.05), 3),
            "escalation_correctness": round(route_quality, 3),
            "correction_absorption_quality": round(0.72, 3),
            "stable_rerun_behavior": round(0.8 if receipt_count >= 4 else 0.55, 3),
        },
    }
    tq = sum(thinking["component_scores"].values()) / len(thinking["component_scores"])
    thinking["score_0_to_1"] = round(tq, 3)
    thinking["score_0_to_100"] = round(tq * 100, 1)
    thinking["verdict"] = "PASS" if tq >= 0.75 else ("PASS_WITH_WARNINGS" if tq >= 0.55 else "BLOCKED")
    thinking["explanation"] = "Thinking quality measures classification confidence, route appropriateness and evidence consistency."
    thinking["unproven_claims"] = unproven_claims
    thinking["trust_verdict"] = "TRUSTED_FOR_BASE_USE" if tq >= 0.78 else ("TRUSTED_WITH_WARNINGS" if tq >= 0.58 else "NOT_TRUSTED")
    return kpd, thinking


def metrics_summary_from_run(run_id: str, run_dir: Path) -> Dict[str, Any]:
    receipts = []
    for receipt_path in sorted((run_dir / "receipts").glob("*.json")):
        try:
            receipts.append(read_json(receipt_path))
        except Exception:
            continue
    metrics_list = [r.get("metrics", {}) for r in receipts if r.get("metrics")]
    peak_values = [m.get("peak_memory_kb") for m in metrics_list if isinstance(m.get("peak_memory_kb"), int)]
    aggregate = {
        "commands": len(metrics_list),
        "wall_clock_ms": sum(int(m.get("wall_clock_ms", 0)) for m in metrics_list),
        "process_cpu_seconds": round(sum(float(m.get("process_cpu_seconds", 0.0) or 0.0) for m in metrics_list), 6),
        "peak_memory_kb": max(peak_values) if peak_values else None,
        "peak_memory_unavailable_reason": "" if peak_values else "peak memory not measured in receipts",
        "memory_metric_source": "tracemalloc_or_unavailable",
        "files_scanned": sum(int(m.get("files_scanned", 0)) for m in metrics_list),
        "files_classified": sum(int(m.get("files_classified", 0)) for m in metrics_list),
        "objects_considered": sum(int(m.get("objects_considered", 0)) for m in metrics_list),
        "outputs_written_count": sum(int(m.get("outputs_written_count", 0)) for m in metrics_list),
        "output_bytes_total": sum(int(m.get("output_bytes_total", m.get("output_bytes", 0)) or 0) for m in metrics_list),
        "warnings_count": sum(int(m.get("warnings_count", 0)) for m in metrics_list),
        "errors_count": sum(int(m.get("errors_count", 0)) for m in metrics_list),
        "rejected_count": sum(int(m.get("rejected_count", 0)) for m in metrics_list),
        "routes_made": sum(int(m.get("routes_made", 0)) for m in metrics_list),
        "receipts_written": sum(int(m.get("receipts_written", 0)) for m in metrics_list),
        "output_bytes": sum(int(m.get("output_bytes", 0)) for m in metrics_list),
        "touched_paths_read_count": sum(int(m.get("touched_paths_read_count", 0)) for m in metrics_list),
        "touched_paths_written_count": sum(int(m.get("touched_paths_written_count", 0)) for m in metrics_list),
        "gpu_used": any(bool(m.get("gpu_used", False)) for m in metrics_list),
        "gpu_reason": "No GPU API/dependency invoked; Python stdlib/script-first execution.",
        "owner_wait_seconds": round(sum(float(m.get("owner_wait_seconds", 0.0) or 0.0) for m in metrics_list), 3),
        "maintenance_cost_note": "Ongoing cost remains moderate with stdlib-only implementation.",
        "dirty_before": any(bool(m.get("dirty_before", m.get("dirty_tree_before", False))) for m in metrics_list),
        "dirty_after": any(bool(m.get("dirty_after", m.get("dirty_tree_after", False))) for m in metrics_list),
        "dirty_tree_before": any(bool(m.get("dirty_tree_before", False)) for m in metrics_list),
        "dirty_tree_after": any(bool(m.get("dirty_tree_after", False)) for m in metrics_list),
    }
    aggregate["cost_class"] = _cost_class(aggregate)
    aggregate["run_cost_class"] = aggregate["cost_class"]
    return {
        "report_type": "METRICS_SUMMARY",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "metrics_schema_fields": METRIC_FIELDS,
        "aggregate": aggregate,
        "receipt_count": len(receipts),
        "verdict": "PASS",
    }


def status_snapshot() -> Dict[str, Any]:
    manifest = load_manifest()
    return {
        "agent_id": manifest.get("agent_id", "ADMINISTRATUM_AGENT"),
        "agent_name": manifest.get("agent_name", "Administratum-Agent"),
        "version": manifest.get("version", "UNKNOWN"),
        "status": manifest.get("status", "UNKNOWN"),
        "runtime_policy": manifest.get("runtime_mode", "UNKNOWN"),
        "supported_skills": manifest.get("supported_skills", []),
        "repo_root": str(REPO_ROOT),
        "new_generation_root": str(NEW_GENERATION_ROOT),
        "runs_root": str(RUNS_ROOT),
        "git_head": git_head(REPO_ROOT),
        "git_branch": git_branch(REPO_ROOT),
        "dirty_tree": git_is_dirty(REPO_ROOT),
        "timestamp_utc": now_utc(),
    }


def load_manifest() -> Dict[str, Any]:
    return read_json(AGENT_ROOT / "agent_manifest.json")


def skill_receipt(
    run_id: str,
    skill_id: str,
    input_refs: List[str],
    outputs: List[str],
    verdict: str,
    warnings: List[str],
) -> Dict[str, Any]:
    return {
        "receipt_type": "ADMINISTRATUM_SKILL_RUN_RECEIPT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "skill_id": skill_id,
        "input_refs": input_refs,
        "outputs": outputs,
        "verdict": verdict,
        "warnings": warnings,
        "mutated_canon": False,
        "deleted_files": False,
        "timestamp": now_utc(),
    }


def write_skill_receipt(run_dir: Path, skill_id: str, receipt: Dict[str, Any]) -> Path:
    out = run_dir / "receipts" / f"{skill_id}_receipt.json"
    write_json(out, receipt)
    return out


def command_receipt(
    run_id: str,
    command: str,
    argv: List[str],
    cwd: str,
    git_head_value: str,
    input_refs: List[str],
    output_refs: List[str],
    metrics: Dict[str, Any],
    warnings: List[str],
    verdict: str,
    dirty_before: bool,
    dirty_after: bool,
    blocker_class: Optional[str] = None,
) -> Dict[str, Any]:
    output_hashes = {}
    for out in output_refs:
        p = Path(out)
        if p.exists() and p.is_file():
            output_hashes[out] = sha256_file(p)
    receipt = {
        "receipt_type": "ADMINISTRATUM_COMMAND_RECEIPT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "skill_id": command,
        "argv": argv,
        "cwd": cwd,
        "git_head": git_head_value,
        "dirty_before": dirty_before,
        "dirty_after": dirty_after,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "output_hashes": output_hashes,
        "metrics": metrics,
        "warnings": warnings,
        "blocker_class": blocker_class,
        "verdict": verdict,
        "mutated_canon": False,
        "deleted_files": False,
        "timestamp": now_utc(),
    }
    return receipt


def write_command_receipt(run_dir: Path, command: str, receipt: Dict[str, Any]) -> Path:
    out = run_dir / "receipts" / f"{command}_command_receipt.json"
    write_json(out, receipt)
    return out


def optional_oss_enhancement_proposal() -> str:
    return "\n".join(
        [
            "# Optional Enhancement Proposal",
            "",
            "Status: OPTIONAL / NOT INSTALLED / NOT CANON",
            "",
            "Candidate:",
            "- Python rich (or Textual-style renderer) for CLI visual comfort improvements.",
            "",
            "Why optional:",
            "- current implementation is stdlib-only and fully functional;",
            "- richer TUI could improve readability for long route and context reports.",
            "",
            "Adoption gates:",
            "1. Local install receipt recorded.",
            "2. No mojibake in Windows PowerShell.",
            "3. `--plain-json` remains authoritative and unchanged.",
            "4. Performance impact measured and acceptable.",
            "5. No new runtime dependencies outside approved scope.",
            "6. Owner explicit approval before canon consideration.",
            "",
            "Current task policy:",
            "- OSS introduced now: NONE",
            "- OSS installed now: NONE",
            "- OSS runtime dependency now: NONE",
            "",
        ]
    )
