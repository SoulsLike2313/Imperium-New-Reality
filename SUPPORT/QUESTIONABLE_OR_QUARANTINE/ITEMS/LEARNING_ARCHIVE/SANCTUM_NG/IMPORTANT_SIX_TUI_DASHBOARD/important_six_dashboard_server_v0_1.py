#!/usr/bin/env python3
"""Important Six TUI API dashboard L1 local server (read-only smoke/sample)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

TASK_ID = "TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1"
SAFE_MODE = "READ_ONLY_SMOKE_AND_SAMPLE_ONLY"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clip_text(text: str, max_chars: int = 12000) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[: max_chars - 24] + "\n...[TRUNCATED]", True


def load_json_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


class ImportantSixDashboardService:
    def __init__(self, repo_root: Path, config_path: Path, timeout_sec: float | None = None) -> None:
        self.repo_root = repo_root.resolve()
        self.config_path = config_path.resolve()
        self.config = load_json_file(self.config_path)
        self.app_dir = self.config_path.parent

        server_cfg = self.config.get("server", {})
        default_timeout = float(server_cfg.get("command_timeout_sec", 30))
        self.timeout_sec = default_timeout if timeout_sec is None else timeout_sec

        organs = self.config.get("organs")
        if not isinstance(organs, dict) or not organs:
            raise ValueError("Config must define non-empty 'organs' map")

        self.organs: dict[str, dict[str, Any]] = {}
        for key, value in organs.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            self.organs[key] = value

        if not self.organs:
            raise ValueError("No valid organs found in config")

        self.task_id = str(self.config.get("task_id", TASK_ID))
        self.mode = str(self.config.get("mode", "READ_ONLY_OR_SEMI_LIVE_TUI_SNAPSHOT_DASHBOARD_L1"))
        self.claim_boundary = str(self.config.get("claim_boundary", self.mode))
        self.not_proven = self._as_str_list(self.config.get("not_proven", []))
        self.safe_commands_only = self._as_str_list(self.config.get("safe_commands_only", []))

    @staticmethod
    def _as_str_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str)]

    def organ_keys(self) -> list[str]:
        return list(self.organs.keys())

    def _get_organ(self, organ_key: str) -> dict[str, Any]:
        if organ_key not in self.organs:
            raise KeyError(f"Unsupported organ: {organ_key}")
        return self.organs[organ_key]

    def _command_for(self, organ_key: str, kind: str) -> tuple[list[str], str, str]:
        spec = self._get_organ(organ_key)
        if kind == "tui":
            script_rel = str(spec.get("tui_script", "")).strip()
            args = self._as_str_list(spec.get("tui_args", []))
        elif kind == "query":
            script_rel = str(spec.get("query_script", "")).strip()
            args = self._as_str_list(spec.get("query_args", []))
        else:
            raise ValueError(f"Unknown command kind: {kind}")

        if not script_rel:
            raise ValueError(f"Missing script path for organ={organ_key} kind={kind}")

        script_abs = (self.repo_root / script_rel).resolve()
        if not script_abs.exists():
            raise FileNotFoundError(f"Script not found: {script_abs}")

        cmd = ["python3", str(script_abs), *args]
        cmd_display = " ".join(["python3", script_rel, *args])
        return cmd, script_rel, cmd_display

    def _run_command(self, command: list[str], command_display: str, script_rel: str) -> dict[str, Any]:
        started_at = utc_now()
        started_monotonic = time.monotonic()
        try:
            proc = subprocess.run(
                command,
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=self.timeout_sec,
            )
            duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
            stdout_text, stdout_truncated = clip_text(proc.stdout or "")
            stderr_text, stderr_truncated = clip_text(proc.stderr or "")
            parsed_json, parse_error = self._parse_json(stdout_text)
            return {
                "command": command_display,
                "script_path": script_rel,
                "exit_code": int(proc.returncode),
                "duration_ms": duration_ms,
                "timed_out": False,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "stdout_truncated": stdout_truncated,
                "stderr_truncated": stderr_truncated,
                "parsed_json": parsed_json,
                "parse_error": parse_error,
                "started_at_utc": started_at,
                "finished_at_utc": utc_now(),
            }
        except subprocess.TimeoutExpired as exc:
            duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
            stdout_text, stdout_truncated = clip_text((exc.stdout or "") if isinstance(exc.stdout, str) else "")
            stderr_text, stderr_truncated = clip_text((exc.stderr or "") if isinstance(exc.stderr, str) else "")
            return {
                "command": command_display,
                "script_path": script_rel,
                "exit_code": 124,
                "duration_ms": duration_ms,
                "timed_out": True,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "stdout_truncated": stdout_truncated,
                "stderr_truncated": stderr_truncated,
                "parsed_json": None,
                "parse_error": "TIMEOUT",
                "started_at_utc": started_at,
                "finished_at_utc": utc_now(),
            }

    @staticmethod
    def _parse_json(text: str) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
        stripped = text.strip()
        if not stripped:
            return None, "EMPTY_STDOUT"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            return None, f"JSON_DECODE_ERROR: {exc.msg}"
        if isinstance(parsed, (dict, list)):
            return parsed, None
        return None, "JSON_ROOT_NOT_OBJECT_OR_ARRAY"

    @staticmethod
    def _normalize_verdict(value: str | None) -> str:
        if not value:
            return "UNKNOWN"
        normalized = value.strip().upper()
        if normalized in {"PASS", "OK"}:
            return "PASS"
        if normalized in {"WARN", "WARNING", "PARTIAL"}:
            return "WARN"
        if normalized in {"BLOCK", "BLOCKED", "FAIL", "FAILED", "ERROR"}:
            return "BLOCK"
        return "UNKNOWN"

    def _extract_verdict(self, *results: dict[str, Any]) -> str:
        for result in results:
            parsed = result.get("parsed_json")
            if isinstance(parsed, dict):
                for key in ("verdict", "status", "gate_verdict", "result"):
                    value = parsed.get(key)
                    if isinstance(value, str):
                        normalized = self._normalize_verdict(value)
                        if normalized != "UNKNOWN":
                            return normalized
        return "UNKNOWN"

    def _build_status(self, verdict: str, tui_result: dict[str, Any], query_result: dict[str, Any]) -> str:
        if tui_result.get("timed_out") or query_result.get("timed_out"):
            return "BLOCK"
        if int(tui_result.get("exit_code", 1)) != 0 or int(query_result.get("exit_code", 1)) != 0:
            return "BLOCK"
        if verdict == "BLOCK":
            return "BLOCK"
        if verdict == "WARN":
            return "WARN"
        if verdict == "PASS":
            return "PASS"
        return "WARN"

    def organ_summary(self, organ_key: str) -> dict[str, Any]:
        spec = self._get_organ(organ_key)
        _, tui_script_rel, tui_cmd_display = self._command_for(organ_key, "tui")
        _, query_script_rel, query_cmd_display = self._command_for(organ_key, "query")
        return {
            "organ_key": organ_key,
            "organ_label": spec.get("organ_label", organ_key.upper()),
            "display_name": spec.get("display_name", {}),
            "role": spec.get("role", {}),
            "accent": spec.get("accent", "#7ea8ff"),
            "safe_mode": SAFE_MODE,
            "source": {
                "tui_command": tui_cmd_display,
                "query_command": query_cmd_display,
                "tui_script": tui_script_rel,
                "query_script": query_script_rel,
            },
        }

    def run_tui_smoke(self, organ_key: str) -> dict[str, Any]:
        command, script_rel, cmd_display = self._command_for(organ_key, "tui")
        payload = self._run_command(command, cmd_display, script_rel)
        payload.update(
            {
                "schema_id": "important_six_tui_smoke_v0_1",
                "organ_key": organ_key,
                "safe_mode": SAFE_MODE,
                "generated_at_utc": utc_now(),
            }
        )
        return payload

    def run_query_sample(self, organ_key: str) -> dict[str, Any]:
        command, script_rel, cmd_display = self._command_for(organ_key, "query")
        payload = self._run_command(command, cmd_display, script_rel)
        payload.update(
            {
                "schema_id": "important_six_query_sample_v0_1",
                "organ_key": organ_key,
                "safe_mode": SAFE_MODE,
                "generated_at_utc": utc_now(),
            }
        )
        return payload

    def terminal_snapshot(self, organ_key: str) -> dict[str, Any]:
        summary = self.organ_summary(organ_key)
        tui_result = self.run_tui_smoke(organ_key)
        query_result = self.run_query_sample(organ_key)
        verdict = self._extract_verdict(query_result, tui_result)
        status = self._build_status(verdict, tui_result, query_result)
        return {
            "schema_id": "important_six_terminal_snapshot_v0_1",
            "generated_at_utc": utc_now(),
            **summary,
            "verdict": verdict,
            "status": status,
            "tui_smoke": tui_result,
            "query_sample": query_result,
            "claim_boundary": self.claim_boundary,
        }

    def dashboard_state(self) -> dict[str, Any]:
        organs: dict[str, Any] = {}
        for organ_key in self.organ_keys():
            organs[organ_key] = self.terminal_snapshot(organ_key)
        return {
            "schema_id": "important_six_dashboard_state_v0_1",
            "task_id": self.task_id,
            "mode": self.mode,
            "claim_boundary": self.claim_boundary,
            "generated_at_utc": utc_now(),
            "safe_commands_only": self.safe_commands_only,
            "not_proven": self.not_proven,
            "organs": organs,
        }

    def status_payload(self) -> dict[str, Any]:
        return {
            "schema_id": "important_six_dashboard_status_v0_1",
            "task_id": self.task_id,
            "mode": self.mode,
            "claim_boundary": self.claim_boundary,
            "generated_at_utc": utc_now(),
            "important_six_count": len(self.organs),
            "allowed_organs": self.organ_keys(),
            "safe_commands_only": self.safe_commands_only,
            "not_proven": self.not_proven,
        }

    def organs_payload(self) -> dict[str, Any]:
        return {
            "schema_id": "important_six_organs_v0_1",
            "generated_at_utc": utc_now(),
            "organs": [self.organ_summary(organ_key) for organ_key in self.organ_keys()],
        }


class DashboardRequestHandler(BaseHTTPRequestHandler):
    server_version = "ImportantSixDashboard/0.1"

    def _service(self) -> ImportantSixDashboardService:
        return self.server.service  # type: ignore[attr-defined]

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path
        service = self._service()

        if route == "/":
            self._send_file(service.app_dir / "important_six_dashboard_v0_1.html", "text/html; charset=utf-8")
            return

        if route == "/important_six_dashboard.css":
            self._send_file(service.app_dir / "important_six_dashboard.css", "text/css; charset=utf-8")
            return

        if route == "/important_six_dashboard.js":
            self._send_file(service.app_dir / "important_six_dashboard.js", "application/javascript; charset=utf-8")
            return

        try:
            if route == "/api/status":
                self._send_json(service.status_payload())
                return

            if route == "/api/organs":
                self._send_json(service.organs_payload())
                return

            if route == "/api/dashboard-state":
                self._send_json(service.dashboard_state())
                return

            prefix = "/api/organs/"
            if route.startswith(prefix):
                parts = route[len(prefix) :].split("/")
                if len(parts) == 2:
                    organ_key, action = parts
                    if action == "tui-smoke":
                        self._send_json(service.run_tui_smoke(organ_key))
                        return
                    if action == "query-sample":
                        self._send_json(service.run_query_sample(organ_key))
                        return
                    if action == "terminal-snapshot":
                        self._send_json(service.terminal_snapshot(organ_key))
                        return

                self._send_json(
                    {
                        "schema_id": "important_six_dashboard_error_v0_1",
                        "error": "Unknown organ action route",
                        "path": route,
                        "allowed": [
                            "/api/organs/<organ>/tui-smoke",
                            "/api/organs/<organ>/query-sample",
                            "/api/organs/<organ>/terminal-snapshot",
                        ],
                    },
                    status=HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(
                {
                    "schema_id": "important_six_dashboard_error_v0_1",
                    "error": "Unknown route",
                    "path": route,
                },
                status=HTTPStatus.NOT_FOUND,
            )
        except KeyError as exc:
            self._send_json(
                {
                    "schema_id": "important_six_dashboard_error_v0_1",
                    "error": "Unsupported organ",
                    "detail": str(exc),
                    "allowed_organs": service.organ_keys(),
                },
                status=HTTPStatus.NOT_FOUND,
            )
        except Exception as exc:  # noqa: BLE001
            self._send_json(
                {
                    "schema_id": "important_six_dashboard_error_v0_1",
                    "error": "Internal server error",
                    "detail": str(exc),
                },
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, fmt: str, *args: Any) -> None:
        # Compact request logs for local operator visibility.
        print(f"[{utc_now()}] {self.address_string()} {fmt % args}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_config = script_path.parent / "important_six_dashboard_config_v0_1.json"
    parser = argparse.ArgumentParser(description="Run Important Six TUI API dashboard server.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--config", type=Path, default=default_config)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--timeout-sec", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = ImportantSixDashboardService(
        repo_root=args.repo_root,
        config_path=args.config,
        timeout_sec=args.timeout_sec,
    )

    server = ThreadingHTTPServer((args.host, args.port), DashboardRequestHandler)
    server.service = service  # type: ignore[attr-defined]

    print(
        json.dumps(
            {
                "schema_id": "important_six_dashboard_server_boot_v0_1",
                "task_id": service.task_id,
                "host": args.host,
                "port": args.port,
                "url": f"http://{args.host}:{args.port}/",
                "mode": service.mode,
                "safe_mode": SAFE_MODE,
                "allowed_organs": service.organ_keys(),
                "generated_at_utc": utc_now(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
