#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mechanicus: Imperium Intelligence Pack Builder v0.1.2

Builds a lightweight, machine-readable repo intelligence pack instead of a crude
codebase dump. v0.1.2 adds a non-self-referential receipt contract: the ZIP
contains manifest/index/edges/slices, while final ZIP SHA256 and closure proof
live in sidecar receipt files next to the ZIP.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SURFACE = "MECHANICUS_IMPERIUM_INTELLIGENCE_PACK_BUILDER_V0_1"
VERSION = "0.1.2"

TEXT_EXTS = {
    ".py", ".ps1", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".csv", ".sql", ".gitignore"
}
CODE_EXTS = {".py", ".ps1", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bat", ".cmd", ".sql"}
DOC_EXTS = {".md", ".txt", ".rst"}
DATA_EXTS = {".json", ".jsonl", ".yaml", ".yml", ".csv", ".toml", ".ini", ".cfg"}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".7z", ".tar", ".gz", ".exe", ".dll", ".pyc", ".har"}

ROOT_LOCAL_PREFIXES = (
    ".git/", ".imperium_patch_backups/", "_LOCAL_HANDOFF/", "LOCAL_HANDOFF/",
    "IMPERIUM_EVIDENCE_VAULT_SMOKE", "EVIDENCE_VAULT_SMOKE", "INTELLIGENCE_PACK_OUTPUTS/",
)
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", "playwright-report", "test-results"}
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".trace.zip", ".har")

DEFAULT_SLICE_PREFIXES = (
    "ORGANS/MECHANICUS/INTELLIGENCE_PACK/",
    "ORGANS/INQUISITION/REPORTING/",
    "ORGANS/ADMINISTRATUM/DATA_ATLAS/INTELLIGENCE_PACK/",
    "ORGANS/DOCTRINARIUM/LAWS/",
    "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/PASSPORTS/",
    "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/RESEARCH_QUEUE/",
    "AGENTS.md",
    ".gitignore",
)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_id(value: str) -> str:
    keep = []
    for ch in value:
        if ch.isalnum() or ch in "._-":
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip("._-") or "NO_ID"


def norm_rel(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def run_git(repo: Path, args: Sequence[str], allow_fail: bool = True) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, encoding="utf-8", errors="replace")
        if p.returncode and not allow_fail:
            raise RuntimeError(p.stderr.strip() or p.stdout.strip())
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:
        if allow_fail:
            return 127, "", str(exc)
        raise


def git_truth(repo: Path) -> Dict[str, object]:
    fields = {}
    commands = {
        "head": ["rev-parse", "HEAD"],
        "head_short": ["rev-parse", "--short=12", "HEAD"],
        "branch": ["branch", "--show-current"],
        "status_short": ["status", "--short"],
        "status_branch_short": ["status", "--branch", "--short"],
        "last_commits": ["log", "--oneline", "--decorate", "-10"],
    }
    for key, cmd in commands.items():
        code, out, err = run_git(repo, cmd)
        fields[key] = out.strip() if code == 0 else None
        if code != 0:
            fields[f"{key}_error"] = err.strip()
    fields["git_available"] = fields.get("head") is not None
    return fields


def is_forbidden_repo_path(rel: str) -> bool:
    rel = norm_rel(rel)
    for prefix in ROOT_LOCAL_PREFIXES:
        if rel == prefix.rstrip("/") or rel.startswith(prefix):
            return True
    parts = rel.split("/")
    if any(part in FORBIDDEN_PARTS for part in parts):
        return True
    low = rel.lower()
    if low.endswith(FORBIDDEN_SUFFIXES):
        return True
    return False


def list_repo_files(repo: Path) -> List[str]:
    code, out, _ = run_git(repo, ["ls-files"])
    files: List[str] = []
    if code == 0 and out.strip():
        files = [norm_rel(x) for x in out.splitlines() if x.strip()]
    else:
        for root, dirs, names in os.walk(repo):
            root_p = Path(root)
            dirs[:] = [d for d in dirs if d not in FORBIDDEN_PARTS and d != ".git"]
            for name in names:
                rel = norm_rel(str((root_p / name).relative_to(repo)))
                files.append(rel)
    return sorted(set(f for f in files if not is_forbidden_repo_path(f)))


def sha256_file(path: Path, max_bytes: Optional[int] = 2_000_000) -> Optional[str]:
    try:
        if max_bytes is not None and path.stat().st_size > max_bytes:
            return None
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def sha256_file_required(path: Path) -> str:
    digest = sha256_file(path, max_bytes=None)
    if not digest:
        raise RuntimeError(f"Unable to hash required artifact: {path}")
    return digest


def classify_ext(ext: str) -> str:
    e = ext.lower()
    if e in CODE_EXTS:
        return "code"
    if e in DOC_EXTS:
        return "document"
    if e in DATA_EXTS:
        return "data_index"
    if e in BINARY_EXTS:
        return "binary_or_archive"
    if not e:
        return "no_extension"
    return "other"


def classify_zone(rel: str) -> str:
    up = rel.upper()
    parts = up.split("/")
    if "FIXTURE" in up or "FIXTURES" in parts or "SMOKE" in up or "HARNESS" in up:
        return "FIXTURE_OR_TEST_SOURCE"
    if up.startswith("REPORTS/"):
        return "SOURCE_REPORT_LEGACY_REVIEW"
    if "EVIDENCE" in up and not up.startswith("ORGANS/"):
        return "EVIDENCE_REVIEW"
    if up.startswith("ORGANS/") or up.startswith("SUPPORT/") or rel in {"AGENTS.md", ".gitignore"}:
        return "SOURCE"
    return "UNCLASSIFIED_SOURCE"


def owner_organ(rel: str) -> str:
    parts = norm_rel(rel).split("/")
    if len(parts) >= 2 and parts[0] == "ORGANS":
        return parts[1]
    if rel.startswith("SUPPORT/"):
        return "SUPPORT"
    if rel.startswith("REPORTS/"):
        return "REPORTS_LEGACY"
    return "ROOT"


def is_text_slice_candidate(rel: str, repo: Path, max_file_bytes: int) -> bool:
    if is_forbidden_repo_path(rel):
        return False
    ext = Path(rel).suffix.lower()
    if rel == ".gitignore":
        return True
    if ext not in TEXT_EXTS:
        return False
    abs_p = repo / rel
    try:
        if abs_p.stat().st_size > max_file_bytes:
            return False
    except Exception:
        return False
    rel_u = norm_rel(rel)
    return any(rel_u.startswith(prefix) or rel_u == prefix.rstrip("/") for prefix in DEFAULT_SLICE_PREFIXES)


def read_json_maybe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_indexes(repo: Path, files: List[str], max_hash_bytes: int) -> Dict[str, object]:
    tree_rows = []
    kind_counts: Dict[str, int] = {}
    organ_counts: Dict[str, Dict[str, int]] = {}
    passports = []
    edges = []

    for rel in files:
        p = repo / rel
        ext = p.suffix.lower()
        kind = classify_ext(ext)
        zone = classify_zone(rel)
        organ = owner_organ(rel)
        try:
            st = p.stat()
            size = int(st.st_size)
            mtime = _dt.datetime.fromtimestamp(st.st_mtime, _dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except Exception:
            size = None
            mtime = None
        row = {
            "path": rel,
            "organ": organ,
            "kind": kind,
            "zone": zone,
            "extension": ext,
            "size_bytes": size,
            "mtime_utc": mtime,
            "sha256": sha256_file(p, max_bytes=max_hash_bytes),
        }
        tree_rows.append(row)
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        organ_counts.setdefault(organ, {"files": 0, "source": 0, "review": 0})
        organ_counts[organ]["files"] += 1
        if zone == "SOURCE":
            organ_counts[organ]["source"] += 1
        elif zone != "SOURCE":
            organ_counts[organ]["review"] += 1

        edges.append({"from": rel, "to": organ, "type": "owned_by_organ"})
        if rel.endswith(".py"):
            tool_id = Path(rel).stem
            edges.append({"from": rel, "to": tool_id, "type": "implements_or_defines_tool"})
        if "DATA_ATLAS" in rel:
            edges.append({"from": rel, "to": "DATA_ATLAS", "type": "visualized_by"})
        if "DOCTRINARIUM/LAWS" in rel:
            edges.append({"from": rel, "to": "ARCHITECTURE_DOCTRINE", "type": "governs"})
        if "PASSPORT" in rel.upper() and ext == ".json":
            data = read_json_maybe(p)
            ids = []
            if isinstance(data, dict):
                for key in ("tools", "passports", "tool_passports"):
                    val = data.get(key)
                    if isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                tid = item.get("tool_id") or item.get("id") or item.get("name")
                                if tid:
                                    ids.append(str(tid))
                tid = data.get("tool_id") or data.get("id")
                if tid:
                    ids.append(str(tid))
            passports.append({"path": rel, "tool_ids": sorted(set(ids)), "organ": organ})
            for tid in sorted(set(ids)):
                edges.append({"from": tid, "to": rel, "type": "has_tool_passport"})

    return {
        "tree_rows": tree_rows,
        "kind_counts": kind_counts,
        "organ_map": {"organs": organ_counts},
        "tool_passports": passports,
        "edges": edges,
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_sqlite(path: Path, tree_rows: List[Dict[str, object]], edges: List[Dict[str, object]], passports: List[Dict[str, object]], manifest: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute("CREATE TABLE manifest (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.execute("CREATE TABLE files (path TEXT PRIMARY KEY, organ TEXT, kind TEXT, zone TEXT, extension TEXT, size_bytes INTEGER, mtime_utc TEXT, sha256 TEXT)")
        con.execute("CREATE TABLE edges (src TEXT, dst TEXT, edge_type TEXT, payload_json TEXT)")
        con.execute("CREATE TABLE tool_passports (path TEXT, tool_id TEXT, organ TEXT)")
        for k, v in manifest.items():
            con.execute("INSERT INTO manifest VALUES (?, ?)", (str(k), json.dumps(v, ensure_ascii=False)))
        for r in tree_rows:
            con.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                r.get("path"), r.get("organ"), r.get("kind"), r.get("zone"), r.get("extension"), r.get("size_bytes"), r.get("mtime_utc"), r.get("sha256")
            ))
        for e in edges:
            con.execute("INSERT INTO edges VALUES (?, ?, ?, ?)", (e.get("from"), e.get("to"), e.get("type"), json.dumps(e, ensure_ascii=False)))
        for p in passports:
            tids = p.get("tool_ids") or []
            if not tids:
                con.execute("INSERT INTO tool_passports VALUES (?, ?, ?)", (p.get("path"), None, p.get("organ")))
            for tid in tids:
                con.execute("INSERT INTO tool_passports VALUES (?, ?, ?)", (p.get("path"), tid, p.get("organ")))
        con.execute("CREATE INDEX idx_files_organ ON files(organ)")
        con.execute("CREATE INDEX idx_files_zone ON files(zone)")
        con.execute("CREATE INDEX idx_edges_src ON edges(src)")
        con.execute("CREATE INDEX idx_edges_dst ON edges(dst)")
        con.commit()
    finally:
        con.close()


def copy_slices(repo: Path, files: List[str], dest: Path, max_file_bytes: int, max_total_bytes: int) -> Tuple[List[Dict[str, object]], int]:
    copied = []
    total = 0
    for rel in files:
        if not is_text_slice_candidate(rel, repo, max_file_bytes=max_file_bytes):
            continue
        src = repo / rel
        try:
            size = src.stat().st_size
        except Exception:
            continue
        if total + size > max_total_bytes:
            continue
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append({"path": rel, "size_bytes": int(size), "reason": "selected_source_slice"})
        total += int(size)
    return copied, total


def zip_dir(src_dir: Path, zip_path: Path) -> str:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                arc = p.relative_to(src_dir).as_posix()
                zf.write(p, arc)
    return sha256_file_required(zip_path)


def owner_summary(manifest, kind_counts, organ_map, slices, zip_name: str, receipt: Optional[Dict[str, object]] = None) -> str:
    lines = [
        f"# Imperium Intelligence Pack — {manifest['patch_id']}",
        "",
        "Назначение: заменить crude codebase dump лёгким, машинно-читаемым intelligence pack.",
        "",
        "## Итог",
        f"- Repo files scanned: {manifest['repo_files_scanned']}",
        f"- Source slices included: {len(slices)}",
        f"- SQLite index: {manifest['sqlite_index']}",
        f"- Dependency edges: {manifest['dependency_edges_total']}",
        f"- ZIP: {zip_name}",
    ]
    if receipt:
        artifact = receipt.get("artifact", {}) if isinstance(receipt, dict) else {}
        lines += [
            f"- Final ZIP SHA256: {artifact.get('sha256')}",
            f"- Final ZIP bytes: {artifact.get('size_bytes')}",
            "- Digest contract: final ZIP hash lives in sidecar receipt, not inside the ZIP manifest.",
        ]
    lines += ["", "## Файловые классы"]
    for k, v in sorted(kind_counts.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## Органы"]
    for organ, data in sorted(organ_map.get("organs", {}).items()):
        lines.append(f"- {organ}: files={data.get('files')}, source={data.get('source')}, review={data.get('review')}")
    lines += [
        "",
        "## Правило",
        "Default handoff теперь должен быть manifest/index/edges/slices, а не полный dump репозитория.",
        "Final ZIP SHA256 не хранится внутри ZIP manifest; он хранится в sidecar receipt рядом с ZIP.",
    ]
    return "\n".join(lines) + "\n"


def sidecar_paths(out_root: Path, pack_id: str) -> Dict[str, Path]:
    base = out_root / pack_id
    return {
        "manifest": base.with_suffix(".INTELLIGENCE_PACK_MANIFEST.json"),
        "sha256sums": base.with_suffix(".FINAL_SHA256SUMS.txt"),
        "machine_receipt": base.with_suffix(".MACHINE_RECEIPT.json"),
        "owner_summary": base.with_suffix(".OWNER_SUMMARY_RU.md"),
    }


def build(args: argparse.Namespace) -> Dict[str, object]:
    repo = Path(args.repo).resolve()
    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    truth = git_truth(repo)
    head_short = truth.get("head_short") or "NO_GIT_HEAD"
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    patch_id = args.patch_id or f"INTELLIGENCE-PACK-{stamp}"
    pack_id = f"IMPERIUM_INTELLIGENCE_PACK_{safe_id(patch_id)}_{safe_id(str(head_short))}_{stamp}"
    staging = out_root / pack_id
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    files = list_repo_files(repo)
    indexes = build_indexes(repo, files, max_hash_bytes=args.max_hash_bytes)
    slices, slice_bytes = copy_slices(repo, files, staging / "PATCH_TARGET_SLICES", args.max_slice_file_bytes, args.max_slice_total_bytes)

    manifest = {
        "schema": "imperium.intelligence_pack.v0_1",
        "surface": SURFACE,
        "version": VERSION,
        "created_at_utc": utc_now(),
        "source_repo": str(repo),
        "source_head": truth.get("head"),
        "source_head_short": truth.get("head_short"),
        "source_branch": truth.get("branch"),
        "patch_id": patch_id,
        "pack_id": pack_id,
        "repo_files_scanned": len(files),
        "source_slices_total": len(slices),
        "source_slices_bytes": slice_bytes,
        "dependency_edges_total": len(indexes["edges"]),
        "sqlite_index": "ATLAS_INDEX.sqlite",
        "default_handoff_law": "manifest/index/edges/slices; no crude full repo dump by default",
        "forbidden_defaults": ["repo_dump", "raw_evidence", "runtime_cache", "local_patch_backups", "smoke_vaults", "nested_archives_without_fixture_manifest"],
        "digest_contract": {
            "contract_id": "mechanicus.intelligence_pack.final_digest_contract.v0_8_9_4",
            "final_zip_sha256_location": "sidecar:FINAL_SHA256SUMS.txt and sidecar:MACHINE_RECEIPT.json",
            "self_referential_pack_hash_inside_zip_manifest": False,
            "reason": "A final ZIP hash cannot be stable when stored inside the ZIP that it hashes.",
        },
        "sidecar_contract": {
            "manifest": "<pack_id>.INTELLIGENCE_PACK_MANIFEST.json",
            "sha256sums": "<pack_id>.FINAL_SHA256SUMS.txt",
            "machine_receipt": "<pack_id>.MACHINE_RECEIPT.json",
            "owner_summary": "<pack_id>.OWNER_SUMMARY_RU.md",
        },
    }

    write_json(staging / "MANIFEST.json", manifest)
    write_json(staging / "GIT_TRUTH.json", truth)
    write_jsonl(staging / "TREE_INDEX.jsonl", indexes["tree_rows"])
    write_json(staging / "FILE_KIND_COUNTS.json", indexes["kind_counts"])
    write_json(staging / "ORGAN_MAP.json", indexes["organ_map"])
    write_json(staging / "TOOL_PASSPORT_INDEX.json", {"tool_passports": indexes["tool_passports"]})
    write_json(staging / "DATA_ATLAS_INDEX_SLICE.json", {"data_atlas_paths": [r["path"] for r in indexes["tree_rows"] if "DATA_ATLAS" in r["path"]]})
    write_json(staging / "INQUISITION_FINDINGS_SLICE.json", {"note": "v0.1 only indexes Inquisition paths; future versions may ingest finding reports.", "inquisition_paths": [r["path"] for r in indexes["tree_rows"] if "/INQUISITION/" in ("/" + r["path"] + "/")]})
    write_jsonl(staging / "DEPENDENCY_EDGES.jsonl", indexes["edges"])
    write_json(staging / "SOURCE_SLICE_MANIFEST.json", {"slices": slices, "total_bytes": slice_bytes})
    write_sqlite(staging / "ATLAS_INDEX.sqlite", indexes["tree_rows"], indexes["edges"], indexes["tool_passports"], manifest)

    zip_path = out_root / f"{pack_id}.zip"
    (staging / "OWNER_SUMMARY_RU.md").write_text(owner_summary(manifest, indexes["kind_counts"], indexes["organ_map"], slices, zip_path.name), encoding="utf-8", newline="\n")
    embedded_manifest_sha256 = sha256_file_required(staging / "MANIFEST.json")
    pack_sha = zip_dir(staging, zip_path)
    pack_size = zip_path.stat().st_size

    paths = sidecar_paths(out_root, pack_id)
    final_manifest = dict(manifest)
    final_manifest.update({
        "pack_zip": str(zip_path),
        "pack_sha256": pack_sha,
        "pack_size_bytes": pack_size,
        "embedded_manifest_sha256": embedded_manifest_sha256,
        "receipt_sidecars": {k: str(v) for k, v in paths.items()},
    })
    receipt = {
        "status": "PASS_INTELLIGENCE_PACK_RECEIPT_WRITTEN",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "contract_id": "mechanicus.intelligence_pack.final_digest_contract.v0_8_9_4",
        "artifact": {
            "path": str(zip_path),
            "filename": zip_path.name,
            "sha256": pack_sha,
            "size_bytes": pack_size,
        },
        "embedded_manifest": {
            "path_in_zip": "MANIFEST.json",
            "sha256": embedded_manifest_sha256,
            "contains_final_zip_sha256": False,
        },
        "sidecars": {k: str(v) for k, v in paths.items()},
        "verification_recipe": [
            "Compute SHA256 over the final ZIP bytes.",
            "Compare it with FINAL_SHA256SUMS.txt, MACHINE_RECEIPT.json and INTELLIGENCE_PACK_MANIFEST.json.",
            "Do not require MANIFEST.json inside the ZIP to contain the final ZIP hash.",
        ],
    }

    write_json(paths["manifest"], final_manifest)
    write_json(paths["machine_receipt"], receipt)
    paths["sha256sums"].write_text(f"{pack_sha}  {zip_path.name}\n", encoding="utf-8", newline="\n")
    paths["owner_summary"].write_text(owner_summary(final_manifest, indexes["kind_counts"], indexes["organ_map"], slices, zip_path.name, receipt), encoding="utf-8", newline="\n")

    report = {
        "status": "PASS_INTELLIGENCE_PACK_BUILT",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "pack_dir": str(staging),
        "pack_zip": str(zip_path),
        "pack_sha256": pack_sha,
        "pack_size_bytes": pack_size,
        "sidecars": {k: str(v) for k, v in paths.items()},
        "manifest": final_manifest,
        "recommended_next_action_ru": "Run Inquisition intelligence pack hygiene gate and receipt gate on pack_zip, then upload ZIP plus receipt sidecars instead of crude repo dump.",
    }
    write_json(out_root / "LATEST_INTELLIGENCE_PACK_REPORT.json", report)
    return report


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build Imperium Intelligence Pack v0.1.2")
    ap.add_argument("--repo", required=True, help="Path to Imperium repo")
    ap.add_argument("--out-root", required=True, help="External output root for pack")
    ap.add_argument("--patch-id", default="INTELLIGENCE-PACK-V0_1")
    ap.add_argument("--max-hash-bytes", type=int, default=2_000_000)
    ap.add_argument("--max-slice-file-bytes", type=int, default=300_000)
    ap.add_argument("--max-slice-total-bytes", type=int, default=5_000_000)
    args = ap.parse_args(argv)
    report = build(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
