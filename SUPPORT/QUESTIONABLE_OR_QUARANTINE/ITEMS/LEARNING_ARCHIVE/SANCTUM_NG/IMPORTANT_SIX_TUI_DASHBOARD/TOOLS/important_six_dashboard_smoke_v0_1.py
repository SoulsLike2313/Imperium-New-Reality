#!/usr/bin/env python3
"""HTTP smoke runner for Important Six TUI API dashboard L1."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1"
EXPECTED_ORGANS = {
    "doctrinarium",
    "officio",
    "administratum",
    "astronomicon",
    "mechanicus",
    "inquisition",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, timeout_sec: float) -> dict[str, Any] | list[Any]:
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    default_report_dir = repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/"
        "TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1"
    )
    parser = argparse.ArgumentParser(description="Run Important Six dashboard API smoke checks.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8766")
    parser.add_argument("--timeout-sec", type=float, default=45.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=default_report_dir / "important_six_dashboard_api_smoke_report.json",
    )
    parser.add_argument(
        "--state-output",
        type=Path,
        default=default_report_dir / "important_six_dashboard_state_sample.json",
    )
    parser.add_argument(
        "--json-parse-output",
        type=Path,
        default=default_report_dir / "json_parse_validation_report.json",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    steps: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    def add_step(name: str, status: str, details: Any) -> None:
        steps.append({"step": name, "status": status, "details": details})
        if status == "BLOCK":
            blockers.append(name)
        elif status == "WARN":
            warnings.append(name)

    dashboard_state_payload: dict[str, Any] | None = None

    try:
        status_payload = fetch_json(f"{base_url}/api/status", args.timeout_sec)
        ok = isinstance(status_payload, dict) and status_payload.get("schema_id") == "important_six_dashboard_status_v0_1"
        add_step("api_status", "PASS" if ok else "BLOCK", status_payload)
    except Exception as exc:  # noqa: BLE001
        add_step("api_status", "BLOCK", str(exc))
        status_payload = None

    try:
        organs_payload = fetch_json(f"{base_url}/api/organs", args.timeout_sec)
        organs_list = organs_payload.get("organs", []) if isinstance(organs_payload, dict) else []
        organ_keys = {
            item.get("organ_key")
            for item in organs_list
            if isinstance(item, dict) and isinstance(item.get("organ_key"), str)
        }
        status = "PASS" if organ_keys == EXPECTED_ORGANS else "BLOCK"
        add_step(
            "api_organs",
            status,
            {
                "received": sorted(organ_keys),
                "expected": sorted(EXPECTED_ORGANS),
                "schema_id": organs_payload.get("schema_id") if isinstance(organs_payload, dict) else "UNKNOWN",
            },
        )
    except Exception as exc:  # noqa: BLE001
        add_step("api_organs", "BLOCK", str(exc))
        organ_keys = set()

    try:
        dashboard_state = fetch_json(f"{base_url}/api/dashboard-state", args.timeout_sec)
        if isinstance(dashboard_state, dict):
            dashboard_state_payload = dashboard_state
        organs_obj = dashboard_state.get("organs", {}) if isinstance(dashboard_state, dict) else {}
        count_ok = isinstance(organs_obj, dict) and len(organs_obj) == 6
        add_step(
            "api_dashboard_state",
            "PASS" if count_ok else "BLOCK",
            {
                "schema_id": dashboard_state.get("schema_id") if isinstance(dashboard_state, dict) else "UNKNOWN",
                "organ_count": len(organs_obj) if isinstance(organs_obj, dict) else 0,
            },
        )
    except Exception as exc:  # noqa: BLE001
        add_step("api_dashboard_state", "BLOCK", str(exc))

    for organ_key in sorted(EXPECTED_ORGANS):
        for action in ("tui-smoke", "query-sample", "terminal-snapshot"):
            route = f"{base_url}/api/organs/{organ_key}/{action}"
            step_name = f"{organ_key}_{action}"
            try:
                payload = fetch_json(route, args.timeout_sec)
                status = "PASS"
                if not isinstance(payload, dict):
                    status = "BLOCK"
                if action in {"tui-smoke", "query-sample"}:
                    if int(payload.get("exit_code", 1)) != 0:
                        status = "BLOCK"
                if action == "terminal-snapshot":
                    if payload.get("status") not in {"PASS", "WARN", "BLOCK"}:
                        status = "WARN"
                add_step(step_name, status, payload)
            except urllib.error.HTTPError as exc:
                add_step(step_name, "BLOCK", {"http_error": exc.code, "reason": str(exc)})
            except Exception as exc:  # noqa: BLE001
                add_step(step_name, "BLOCK", str(exc))

    if dashboard_state_payload is not None:
        write_json(args.state_output.resolve(), dashboard_state_payload)

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report_payload = {
        "schema_id": "important_six_dashboard_api_smoke_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "base_url": base_url,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "steps": steps,
    }
    write_json(args.output.resolve(), report_payload)

    json_parse_checks: list[dict[str, Any]] = []
    for path in (args.output.resolve(), args.state_output.resolve()):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            json_parse_checks.append(
                {
                    "path": str(path),
                    "status": "PASS",
                    "json_type": type(parsed).__name__,
                }
            )
        except Exception as exc:  # noqa: BLE001
            json_parse_checks.append(
                {
                    "path": str(path),
                    "status": "BLOCK",
                    "error": str(exc),
                }
            )

    parse_verdict = "PASS" if all(item["status"] == "PASS" for item in json_parse_checks) else "BLOCK"
    parse_report = {
        "schema_id": "important_six_dashboard_json_parse_validation_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": parse_verdict,
        "checks": json_parse_checks,
    }
    write_json(args.json_parse_output.resolve(), parse_report)

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
