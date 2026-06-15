#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

SURFACE = "ADMINISTRATUM_WARP_RUNTIME_REPORT_BUNDLE_BUILDER_V0_8_1"
TASK_ID = "H-TASK-NEWREALITY-PC-SERVITOR-WARP-RUNTIME-ACTIVE-TASK-STAGE-LEDGER-V0_7"


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(["git", "-C", str(repo), *args], text=True, encoding="utf-8", errors="replace", capture_output=True)
    return process.stdout + process.stderr


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def local_handoff_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_LOCAL_HANDOFF")
    if configured:
        return Path(configured).resolve()
    return Path(repo.anchor) / "IMPERIUM_LOCAL_HANDOFF"


def output_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_SERVITOR_OUTPUT_ROOT")
    if configured:
        return Path(configured).resolve()
    return local_handoff_root(repo) / "SERVITOR_OUTPUTS" / TASK_ID


def runtime_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_WARP_RUNTIME_ROOT")
    if configured:
        return Path(configured).resolve()
    return local_handoff_root(repo) / "WARP_RUNS"


def runtime_registry(repo: Path) -> Path:
    return runtime_root(repo) / "_registry" / "warp_registry.json"


def copy_file(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return True


def copy_tree_files(src: Path, dst: Path) -> int:
    if not src.exists():
        return 0
    count = 0
    for path in src.rglob("*"):
        if path.is_file():
            target = dst / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            count += 1
    return count


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_bundle(repo: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    work = out_dir / f"final_report_bundle_{stamp}"
    work.mkdir(parents=True, exist_ok=True)

    write_text(work / "GIT_STATUS.txt", git(repo, "status", "--short"))
    write_text(work / "GIT_STATUS_SB.txt", git(repo, "status", "-sb"))
    write_text(work / "GIT_DIFF_STAT.txt", git(repo, "diff", "--stat"))
    write_text(work / "GIT_LOG.txt", git(repo, "log", "--oneline", "--decorate", "-10"))
    write_text(work / "GIT_DIFF.patch", git(repo, "diff", "--binary"))

    copied = []
    for rel in [
        "ORGANS/MECHANICUS/TOOL_REGISTRY/tool_registry.json",
        "ORGANS/ADMINISTRATUM/RUNTIME_HYGIENE/runtime_paths_policy.json",
        "ORGANS/STRATEGIUM/RESOURCE_FLEET/resource_fleet_registry.json",
        "ORGANS/IMPERIAL_IDE/WEB_SANCTUM/app/index.html",
        "ORGANS/IMPERIAL_IDE/WEB_SANCTUM/app/main.js",
        "ORGANS/IMPERIAL_IDE/WEB_SANCTUM/app/styles.css",
    ]:
        src = repo / rel
        dst = work / "source_snapshots" / rel.replace("/", "__")
        if copy_file(src, dst):
            copied.append(rel)

    registry = read_json(runtime_registry(repo), {})
    run_dir = Path(registry.get("runtime_path", "")) if registry.get("runtime_path") else runtime_root(repo) / registry.get("warp_id", "NO_WARP")
    runtime_files = []
    for name in [
        "stage_ledger.json",
        "administratum_receipts.jsonl",
        "astronomicon_stage_gates.json",
        "inquisition_findings.json",
        "jobs.jsonl",
    ]:
        src = run_dir / name
        if copy_file(src, work / "runtime" / name):
            runtime_files.append(name)
    for src in [runtime_registry(repo), runtime_root(repo) / "_registry" / "active_task.json", runtime_root(repo) / "_registry" / "admission_receipts.jsonl"]:
        if copy_file(src, work / "runtime_registry" / src.name):
            runtime_files.append(src.name)

    out_root = output_root(repo)
    screenshot_count = copy_tree_files(out_root / "playwright" / "screenshots", work / "screenshots")
    playwright_count = copy_tree_files(out_root / "playwright" / "test-results", work / "playwright" / "test-results")
    report_count = copy_tree_files(out_root / "playwright" / "report", work / "playwright" / "report")

    manifest = {
        "status": "PASS",
        "surface": SURFACE,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo),
        "runtime_root": str(runtime_root(repo)),
        "runtime_run_dir": str(run_dir),
        "runtime_files": runtime_files,
        "source_snapshots": copied,
        "screenshot_count": screenshot_count,
        "playwright_result_file_count": playwright_count,
        "playwright_report_file_count": report_count,
        "owner_acceptance_required": True,
        "commit_push_performed": False,
    }
    write_text(work / "FINAL_REPORT_MANIFEST.json", json.dumps(manifest, indent=2))
    write_text(work / "OWNER_SUMMARY_RU.md", "# Owner summary\n\nWARP runtime bundle generated. Review ledger, validation findings, screenshots and git truth before applying any patch.\n")

    zip_path = out_dir / f"FINAL_REPORT_BUNDLE_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in work.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(work))
    return {"status": "PASS", "surface": SURFACE, "bundle": str(zip_path), "work_dir": str(work), **manifest}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("cmd", nargs="?", default="build")
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else output_root(repo) / "runtime_report"
    if args.cmd != "build":
        print(json.dumps({"status": "BLOCKED", "surface": SURFACE, "reason": "UNKNOWN_COMMAND", "cmd": args.cmd}, indent=2))
        return
    print(json.dumps(build_bundle(repo, out_dir), indent=2))


if __name__ == "__main__":
    main()
