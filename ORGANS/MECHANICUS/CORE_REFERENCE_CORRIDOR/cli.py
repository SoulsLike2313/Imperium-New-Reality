"""Thin command adapter for the Authoritative Safe Execution Spine."""

from __future__ import annotations

import argparse
import json
import sys

from .service import CorridorService


def _emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=True, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="imperium-core-reference-corridor")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bootstrap")
    sub.add_parser("status")
    sub.add_parser("execute-demo")
    sub.add_parser("build-reports")
    sub.add_parser("build-final-reports")
    sub.add_parser("validate")
    sub.add_parser("validate-retry-01")
    sub.add_parser("validate-retry-02")
    sub.add_parser("validate-retry-03")
    sub.add_parser("advance-owner-review")
    sub.add_parser("ui-snapshot")
    action = sub.add_parser("ui-action")
    action.add_argument("--action-id", required=True)
    action.add_argument("--payload-json", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        service = CorridorService(".")
        if args.command == "bootstrap":
            result = service.bootstrap()
        elif args.command == "status":
            result = service.status()
        elif args.command == "execute-demo":
            result = service.execute_demo()
        elif args.command == "build-reports":
            result = service.run_internal_capability("CORE_REPORT_BUILDER", "REPORT_BUILD_RECEIPT")
        elif args.command == "build-final-reports":
            result = service.run_internal_capability(
                "CORE_REPORT_BUILDER", "REPORT_BUILD_FINAL_RECEIPT", seal_evidence_index=True
            )
        elif args.command == "validate":
            result = service.run_internal_capability("CORE_VALIDATION_SUITE", "VALIDATION_RECEIPT")
        elif args.command == "validate-retry-01":
            result = service.run_internal_capability("CORE_VALIDATION_SUITE", "VALIDATION_RETRY_01_RECEIPT")
        elif args.command == "validate-retry-02":
            result = service.run_internal_capability("CORE_VALIDATION_SUITE", "VALIDATION_RETRY_02_RECEIPT")
        elif args.command == "validate-retry-03":
            result = service.run_internal_capability("CORE_VALIDATION_SUITE", "VALIDATION_RETRY_03_RECEIPT")
        elif args.command == "advance-owner-review":
            result = service.advance_to_owner_review()
        elif args.command == "ui-snapshot":
            result = service.snapshot()
        elif args.command == "ui-action":
            payload = json.loads(args.payload_json)
            if not isinstance(payload, dict):
                raise ValueError("payload-json must decode to an object")
            result = service.ui_action(args.action_id, payload)
        else:
            raise ValueError("unknown command")
    except Exception as exc:
        _emit({"verdict": "BLOCK", "error_code": exc.__class__.__name__, "message": str(exc)})
        return 2
    _emit(result)
    return 0 if not str(result.get("verdict", "")).startswith("BLOCK") else 2


if __name__ == "__main__":
    sys.exit(main())
