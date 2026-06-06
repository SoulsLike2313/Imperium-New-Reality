#!/usr/bin/env python3
"""Important Six dashboard L2 server with safe action surface."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ACTIONS.important_six_dashboard_actions_v0_1 import (
    TASK_ID,
    ImportantSixDashboardActions,
    parse_json_payload,
    utc_now,
)


class ImportantSixDashboardL2Service:
    def __init__(self, repo_root: Path, app_root: Path, report_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.app_root = app_root.resolve()
        self.report_root = report_root.resolve()
        self.actions_runner = ImportantSixDashboardActions(
            repo_root=self.repo_root,
            dashboard_root=self.app_root,
            report_root=self.report_root,
            registry_path=self.app_root / "ACTIONS" / "important_six_dashboard_actions_registry_v0_1.json",
            transfer_config_path=self.app_root / "TRANSFER_ZONE" / "transfer_zone_config_v0_1.json",
            owner_question_schema_path=self.app_root / "OWNER_INTENT" / "owner_question_schema_v0_1.json",
            owner_diff_schema_path=self.app_root / "OWNER_INTENT" / "owner_diff_decision_schema_v0_1.json",
        )

    def status_payload(self) -> dict[str, Any]:
        return {
            "schema_id": "important_six_dashboard_l2_status_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "mode": "L2_SAFE_CONTROL_ACTION_SURFACE",
            "verdict_target": "CANONICAL_VERIFICATION_SPINE_V0_1",
            "safe_rules": [
                "no arbitrary shell execution",
                "no destructive actions",
                "writes only in scoped NewGen paths",
                "every action creates receipt",
            ],
            "api_routes": [
                "GET /api/actions",
                "POST /api/actions/<action_id>/run",
                "GET /api/actions/<action_id>/last-result",
                "GET /api/action-history",
                "GET /api/owner-questions",
                "POST /api/owner-intent/decision",
                "GET /api/diff/status",
            ],
        }


class DashboardL2RequestHandler(BaseHTTPRequestHandler):
    server_version = "ImportantSixDashboardL2/0.2"

    def _service(self) -> ImportantSixDashboardL2Service:
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
            self._send_json(
                {
                    "schema_id": "important_six_dashboard_l2_error_v0_1",
                    "error": "File not found",
                    "path": str(file_path),
                },
                status=HTTPStatus.NOT_FOUND,
            )
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _http_status_from_verdict(verdict: str) -> HTTPStatus:
        normalized = str(verdict or "").strip().upper()
        if normalized in {"PASS", "PASS_WITH_WARNINGS"}:
            return HTTPStatus.OK
        if normalized == "BLOCKED":
            return HTTPStatus.BAD_REQUEST
        return HTTPStatus.INTERNAL_SERVER_ERROR

    def _bad_request(self, message: str) -> None:
        self._send_json(
            {
                "schema_id": "important_six_dashboard_l2_error_v0_1",
                "error": "Bad request",
                "detail": message,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    def _not_found(self, route: str) -> None:
        self._send_json(
            {
                "schema_id": "important_six_dashboard_l2_error_v0_1",
                "error": "Unknown route",
                "path": route,
            },
            status=HTTPStatus.NOT_FOUND,
        )

    def _handle_actions_get(self, route: str, query: dict[str, list[str]]) -> None:
        service = self._service()

        if route == "/api/actions":
            self._send_json(service.actions_runner.list_actions())
            return

        prefix = "/api/actions/"
        if route.startswith(prefix) and route.endswith("/last-result"):
            action_id = route[len(prefix) : -len("/last-result")].strip("/")
            if not action_id:
                self._bad_request("Missing action_id in path")
                return
            try:
                payload = service.actions_runner.get_action_last_result(action_id)
            except KeyError:
                self._send_json(
                    {
                        "schema_id": "important_six_dashboard_l2_error_v0_1",
                        "error": "Unknown action_id",
                        "action_id": action_id,
                    },
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            self._send_json(payload)
            return

        if route == "/api/action-history":
            limit = 120
            if "limit" in query:
                try:
                    limit = max(1, min(int(query["limit"][0]), 800))
                except Exception:
                    limit = 120
            self._send_json(service.actions_runner.get_action_history(limit=limit))
            return

        if route == "/api/owner-questions":
            self._send_json(service.actions_runner.get_owner_questions())
            return

        if route == "/api/diff/status":
            self._send_json(service.actions_runner.get_diff_status())
            return

        if route == "/api/status":
            self._send_json(service.status_payload())
            return

        self._not_found(route)

    def _handle_actions_post(self, route: str, body: bytes) -> None:
        service = self._service()

        if route == "/api/owner-intent/decision":
            try:
                payload = parse_json_payload(body)
            except ValueError as exc:
                self._bad_request(str(exc))
                return
            result = service.actions_runner.record_owner_diff_decision_from_endpoint(payload)
            status = self._http_status_from_verdict(str(result.get("status", "BLOCKED")))
            self._send_json(result, status=status)
            return

        prefix = "/api/actions/"
        if route.startswith(prefix) and route.endswith("/run"):
            action_id = route[len(prefix) : -len("/run")].strip("/")
            if not action_id:
                self._bad_request("Missing action_id in path")
                return
            try:
                payload = parse_json_payload(body)
            except ValueError as exc:
                self._bad_request(str(exc))
                return
            try:
                result = service.actions_runner.run_action(action_id=action_id, payload=payload)
            except KeyError:
                self._send_json(
                    {
                        "schema_id": "important_six_dashboard_l2_error_v0_1",
                        "error": "Unknown action_id",
                        "action_id": action_id,
                    },
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {
                        "schema_id": "important_six_dashboard_l2_error_v0_1",
                        "error": "Action execution failed",
                        "action_id": action_id,
                        "detail": str(exc),
                    },
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return
            status = self._http_status_from_verdict(str(result.get("status", "BLOCKED")))
            self._send_json(result, status=status)
            return

        self._not_found(route)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query, keep_blank_values=False)
        service = self._service()

        if route == "/":
            self._send_file(service.app_root / "important_six_dashboard_v0_2.html", "text/html; charset=utf-8")
            return

        if route == "/important_six_dashboard_l2.css":
            self._send_file(service.app_root / "important_six_dashboard_l2.css", "text/css; charset=utf-8")
            return

        if route == "/important_six_dashboard_l2.js":
            self._send_file(service.app_root / "important_six_dashboard_l2.js", "application/javascript; charset=utf-8")
            return

        if route.startswith("/api/"):
            self._handle_actions_get(route, query)
            return

        self._not_found(route)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self._bad_request("Missing Content-Length")
            return

        try:
            body_length = int(length_header)
        except ValueError:
            self._bad_request("Invalid Content-Length")
            return

        if body_length < 0 or body_length > 512_000:
            self._bad_request("Request body too large")
            return

        body = self.rfile.read(body_length) if body_length > 0 else b""

        if route.startswith("/api/"):
            self._handle_actions_post(route, body)
            return

        self._not_found(route)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{utc_now()}] {self.address_string()} {fmt % args}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_app_root = script_path.parent
    default_report_root = (
        default_repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "REPORTS"
        / "TASK-NEWGEN-VERIFICATION-SPINE-CONVERGENCE-PC-V0_1"
    )

    parser = argparse.ArgumentParser(description="Run Important Six dashboard L2 action server.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--app-root", type=Path, default=default_app_root)
    parser.add_argument("--report-root", type=Path, default=default_report_root)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = ImportantSixDashboardL2Service(repo_root=args.repo_root, app_root=args.app_root, report_root=args.report_root)

    server = ThreadingHTTPServer((args.host, args.port), DashboardL2RequestHandler)
    server.service = service  # type: ignore[attr-defined]

    print(
        json.dumps(
            {
                "schema_id": "important_six_dashboard_l2_server_boot_v0_1",
                "task_id": TASK_ID,
                "host": args.host,
                "port": args.port,
                "url": f"http://{args.host}:{args.port}/",
                "mode": "L2_SAFE_CONTROL_ACTION_SURFACE",
                "report_root": str(args.report_root),
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


