#!/usr/bin/env python3
"""imperial_ide_ops_cli - command-line driver for the operational engine.

Lets the owner run the whole task loop without dragging ZIPs around:
    classify | build-taskpack | register | launch-card | lifecycle |
    safety | git-status | validate-receipt

All actions are dry-run by default and never touch the kernel tree.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Allow running from anywhere: add ENGINE to path.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.normpath(os.path.join(_HERE, "..", "ENGINE"))
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from imperium_ops import (  # noqa: E402
    astronomicon_register as astro,
    git_closure,
    launch_card as lc,
    lifecycle,
    receipts,
    safety_gate,
    task_console,
    taskpack_builder as tpb,
)


def _detect_repo_root(explicit: str = None) -> str:
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("IMPERIUM_ROOT")
    if env:
        return os.path.abspath(env)
    return os.getcwd()


def _ops_staging_root(repo_root: str) -> str:
    return os.path.join(repo_root, "ORGANS", "IMPERIAL_IDE", "OPS", "STAGING")


def _default_taskpack_out(repo_root: str) -> str:
    return os.path.join(_ops_staging_root(repo_root), "TASKPACKS")


def _intent_from_args(args) -> task_console.TaskIntent:
    return task_console.new_task(
        title=args.title,
        goal=args.goal or args.title,
        task_type=args.type,
        scope=args.scope,
        risk=args.risk,
        organs_route=args.organs.split(",") if args.organs else None,
        push_policy=args.push,
        version=args.version,
    )


def cmd_classify(args) -> int:
    intent = _intent_from_args(args)
    ok, problems = task_console.validate_intent(intent)
    print(json.dumps({
        "task_id": intent.task_id,
        "task_type": intent.task_type,
        "scope": intent.scope,
        "risk": intent.risk,
        "organs_route": intent.organs_route,
        "valid": ok,
        "problems": problems,
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def cmd_build_taskpack(args) -> int:
    intent = _intent_from_args(args)
    out_root = args.out or _default_taskpack_out(_detect_repo_root(args.repo))
    extracted = tpb.write_taskpack(out_root, intent)
    blockers = tpb.admission_precheck(extracted)
    zip_path = os.path.join(os.path.dirname(extracted), "TASKPACK.zip")
    info = tpb.build_zip(extracted, zip_path)
    print(json.dumps({
        "task_id": intent.task_id,
        "extracted": extracted,
        "zip": zip_path,
        "zip_info": info,
        "admission_blockers": blockers,
    }, ensure_ascii=False, indent=2))
    return 0 if not blockers else 2


def cmd_register(args) -> int:
    repo = _detect_repo_root(args.repo)
    intent = _intent_from_args(args)
    out_root = _default_taskpack_out(repo)
    extracted = tpb.write_taskpack(out_root, intent)
    reg = astro.register(repo, extracted, intent, dry_run=not args.real)
    print(json.dumps(reg.to_dict(), ensure_ascii=False, indent=2))
    return 0 if reg.admitted else 2


def cmd_launch_card(args) -> int:
    repo = _detect_repo_root(args.repo)
    intent = _intent_from_args(args)
    out_root = _default_taskpack_out(repo)
    extracted = tpb.write_taskpack(out_root, intent)
    reg = astro.register(repo, extracted, intent, dry_run=not args.real)
    card = lc.build_launch_card(intent, reg.registered_path, reg.admitted, reg.sha256)
    print(lc.render_launch_card_text(card))
    return 0 if reg.admitted else 2


def cmd_lifecycle(args) -> int:
    repo = _detect_repo_root(args.repo)
    intent = _intent_from_args(args)
    out_root = _default_taskpack_out(repo)
    state = safety_gate.load_safety(repo)
    result = lifecycle.run_lifecycle(repo, intent, out_root, state=state, dry_run=not args.real)
    print(lifecycle.render_progress(result))
    print()
    print(f"VERDICT: {result.verdict}")
    return 0 if result.verdict != "BLOCKED" else 2


def cmd_safety(args) -> int:
    repo = _detect_repo_root(args.repo)
    state = safety_gate.load_safety(repo)
    print(json.dumps(safety_gate.safety_report(state), ensure_ascii=False, indent=2))
    return 0


def cmd_git_status(args) -> int:
    repo = _detect_repo_root(args.repo)
    print(json.dumps(git_closure.git_status(repo), ensure_ascii=False, indent=2))
    return 0


def cmd_validate_receipt(args) -> int:
    with open(args.path, "r", encoding="utf-8") as fh:
        receipt = json.load(fh)
    ok, missing = receipts.validate_receipt(receipt)
    risk = receipts.fake_green_risk(receipt)
    print(json.dumps({"valid": ok, "missing": missing, "fake_green_risk": risk}, ensure_ascii=False, indent=2))
    return 0 if ok and not risk else 2


def cmd_task_templates(args) -> int:
    path = os.path.normpath(os.path.join(_HERE, "..", "TEMPLATES", "task_templates.json"))
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_smoke(args) -> int:
    repo = _detect_repo_root(args.repo)
    out_root = os.path.join(_ops_staging_root(repo), "SMOKE_TASKPACKS")
    intent = task_console.new_task(
        title="OPS task console smoke",
        goal="Build an Astronomicon compatible taskpack from inside Imperial IDE OPS",
        task_type="integration",
        scope="IMPERIAL_IDE",
        risk="CONTROLLED_WRITE",
        organs_route=["ASTRONOMICON", "MECHANICUS", "INQUISITION", "ADMINISTRATUM"],
        push_policy="VALIDATED_PUSH",
    )
    ok, problems = task_console.validate_intent(intent)
    extracted = tpb.write_taskpack(out_root, intent)
    blockers = tpb.admission_precheck(extracted)
    zip_path = os.path.join(os.path.dirname(extracted), "TASKPACK.zip")
    zip_info = tpb.build_zip(extracted, zip_path)
    with open(os.path.join(extracted, "MANIFEST.json"), "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    state = safety_gate.load_safety(repo)
    bad_report = {
        "task_id": intent.task_id,
        "result_summary": "bare PASS",
        "evidence_level": "E2",
        "validation": {"result": "PASS"},
    }
    held = lifecycle.run_lifecycle(
        repo, intent, out_root, state=state, servitor_report=bad_report, dry_run=True
    )
    released = lifecycle.run_lifecycle(repo, intent, out_root, state=state, dry_run=True)
    safety = safety_gate.safety_receipt_fields(repo, state)
    root_files_present = {
        name: os.path.isfile(os.path.join(extracted, name))
        for name in tpb.REQUIRED_TASKPACK_FILES
    }
    checks = {
        "validate_intent_tuple_contract": ok and problems == [],
        "root_files_present": all(root_files_present.values()),
        "manifest_schema_version": manifest.get("schema_version") == tpb.SCHEMA_VERSION,
        "cyrillic_field_present": "cyrillic_in_taskpack"
        in (manifest.get("language_and_encoding_policy") or {}),
        "required_organs_present": bool(manifest.get("required_organs")),
        "organ_route_present": bool(manifest.get("organ_route")),
        "admission_precheck_clean": blockers == [],
        "zip_sha256_recorded": len(zip_info.get("sha256", "")) == 64,
        "fake_green_trap_catches_bare_pass": held.verdict == "HELD",
        "complete_bundle_released": released.verdict == "RELEASED",
        "real_execution_blocked": not safety["real_servitor_execution_enabled"],
        "live_llm_disabled": not safety["live_llm_backend_enabled"],
        "unsafe_shell_blocked": not safety["unsafe_shell_available"],
        "unknown_tool_blocked": safety["unknown_tool_blocked"],
    }
    status = "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED"
    print(json.dumps({
        "status": status,
        "task_id": intent.task_id,
        "repo_root": repo,
        "generated_taskpack_path": zip_path,
        "generated_taskpack_sha256": zip_info["sha256"],
        "root_files_present": root_files_present,
        "admission_blockers": blockers,
        "safety": safety,
        "checks": checks,
    }, ensure_ascii=False, indent=2))
    return 0 if status != "BLOCKED" else 2


def _add_intent_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--title", required=True)
    p.add_argument("--goal", default="")
    p.add_argument("--type", default=None)
    p.add_argument("--scope", default="IMPERIAL_IDE")
    p.add_argument("--risk", default="CONTROLLED_WRITE")
    p.add_argument("--organs", default="")
    p.add_argument("--push", default="VALIDATED_PUSH")
    p.add_argument("--version", default="V0_1")
    p.add_argument("--repo", default=None)
    p.add_argument("--real", action="store_true", help="disable dry-run (still gated by safety)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="imperial-ide-ops", description="Imperial IDE operational engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("classify"); _add_intent_args(p); p.set_defaults(func=cmd_classify)
    p = sub.add_parser("build-taskpack"); _add_intent_args(p); p.add_argument("--out", default=None); p.set_defaults(func=cmd_build_taskpack)
    p = sub.add_parser("register"); _add_intent_args(p); p.set_defaults(func=cmd_register)
    p = sub.add_parser("launch-card"); _add_intent_args(p); p.set_defaults(func=cmd_launch_card)
    p = sub.add_parser("lifecycle"); _add_intent_args(p); p.set_defaults(func=cmd_lifecycle)
    p = sub.add_parser("smoke"); p.add_argument("--repo", default=None); p.set_defaults(func=cmd_smoke)
    p = sub.add_parser("task-templates"); p.set_defaults(func=cmd_task_templates)

    p = sub.add_parser("safety"); p.add_argument("--repo", default=None); p.set_defaults(func=cmd_safety)
    p = sub.add_parser("git-status"); p.add_argument("--repo", default=None); p.set_defaults(func=cmd_git_status)
    p = sub.add_parser("validate-receipt"); p.add_argument("path"); p.set_defaults(func=cmd_validate_receipt)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
