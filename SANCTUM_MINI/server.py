"""Local Sanctum Mini server (Python stdlib only)."""

from __future__ import annotations

import argparse
import json
import mimetypes
import queue
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from api.actions import (
    execute_terminal_command,
    get_action_history,
    get_terminal_history,
    list_actions,
    run_action,
    terminal_allowlist,
)
from api.event_stream import encode_sse, make_event, subscribe_events, unsubscribe_events
from api.state_builder import build_health, build_state


REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = Path(__file__).resolve().parent / "static"


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


class SanctumMiniHandler(BaseHTTPRequestHandler):
    server_version = "SanctumMiniHTTP/0.4"

    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _write_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        if not _is_within(file_path, STATIC_ROOT):
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return

        content = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _write_bytes(self, content: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> tuple[dict, HTTPStatus | None, str | None]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return {}, HTTPStatus.BAD_REQUEST, "Invalid Content-Length"

        raw_body = self.rfile.read(content_length) if content_length > 0 else b""
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            if not isinstance(payload, dict):
                return {}, HTTPStatus.BAD_REQUEST, "JSON object body required"
            return payload, None, None
        except json.JSONDecodeError:
            return {}, HTTPStatus.BAD_REQUEST, "Invalid JSON body"

    def _mechanicus_screenshot_entry(self, state: dict, index: int | None = None) -> dict | None:
        screenshots = state.get("mechanicus", {}).get("latest_screenshots", [])
        if not screenshots:
            return None
        if index is None:
            return screenshots[0]
        if index < 0 or index >= len(screenshots):
            return None
        return screenshots[index]

    def _serve_mechanicus_screenshot(self, index: int | None = None) -> None:
        state = build_state(repo_root=REPO_ROOT)
        entry = self._mechanicus_screenshot_entry(state, index=index)
        if not entry:
            self.send_error(HTTPStatus.NOT_FOUND, "Mechanicus screenshot not found")
            return
        file_path = Path(str(entry.get("path", "")))
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Mechanicus screenshot file missing")
            return
        if not _is_within(file_path, REPO_ROOT):
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden screenshot path")
            return

        content = file_path.read_bytes()
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self._write_bytes(content=content, content_type=content_type)

    def _serve_sse_events(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        subscriber_id, buffer = subscribe_events()
        heartbeat_interval = 8.0
        last_heartbeat = time.monotonic()
        try:
            state = build_state(repo_root=REPO_ROOT)
            snapshot_event = make_event(
                event_type="state_snapshot",
                source="sanctum_state_builder",
                truth_status=str(state.get("server", {}).get("status", "UNKNOWN")),
                organ=state.get("server", {}).get("active_organ"),
                details={
                    "head": state.get("repo", {}).get("head"),
                    "worktree_state": state.get("repo", {}).get("worktree_state"),
                    "warnings_count": state.get("global_truth", {}).get("warnings_count"),
                    "errors_count": state.get("global_truth", {}).get("errors_count"),
                    "blockers_count": state.get("global_truth", {}).get("blockers_count"),
                },
            )
            self.wfile.write(encode_sse(snapshot_event))
            self.wfile.flush()

            while True:
                timeout = max(0.2, heartbeat_interval - (time.monotonic() - last_heartbeat))
                try:
                    event = buffer.get(timeout=timeout)
                    self.wfile.write(encode_sse(event))
                    self.wfile.flush()
                except queue.Empty:
                    heartbeat = make_event(
                        event_type="heartbeat",
                        source="sanctum_sse_gateway",
                        truth_status="PASS",
                        details={"heartbeat_interval_sec": heartbeat_interval},
                    )
                    self.wfile.write(encode_sse(heartbeat))
                    self.wfile.flush()
                    last_heartbeat = time.monotonic()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return
        except Exception as exc:  # noqa: BLE001
            error_event = make_event(
                event_type="error",
                source="sanctum_sse_gateway",
                truth_status="ERROR",
                details={"error": str(exc)},
            )
            try:
                self.wfile.write(encode_sse(error_event))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
        finally:
            unsubscribe_events(subscriber_id)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/api/events":
            self._serve_sse_events()
            return
        if path == "/api/health":
            self._write_json(build_health(repo_root=REPO_ROOT))
            return
        if path == "/api/state":
            self._write_json(build_state(repo_root=REPO_ROOT))
            return
        if path == "/api/organs":
            state = build_state(repo_root=REPO_ROOT)
            self._write_json(
                {
                    "generated_at_utc": state["generated_at_utc"],
                    "organs": state["organs"],
                }
            )
            return
        if path == "/api/mechanicus":
            state = build_state(repo_root=REPO_ROOT)
            self._write_json(
                {
                    "generated_at_utc": state["generated_at_utc"],
                    "mechanicus": state["mechanicus"],
                }
            )
            return
        if path == "/api/mechanicus/screenshots":
            state = build_state(repo_root=REPO_ROOT)
            screenshots = state["mechanicus"].get("latest_screenshots", [])
            payload_items = []
            for idx, item in enumerate(screenshots):
                row = dict(item)
                row["asset_url"] = f"/api/mechanicus/screenshot/{idx}"
                payload_items.append(row)
            self._write_json(
                {
                    "generated_at_utc": state["generated_at_utc"],
                    "screenshots": payload_items,
                }
            )
            return
        if path == "/api/mechanicus/reports":
            state = build_state(repo_root=REPO_ROOT)
            self._write_json(
                {
                    "generated_at_utc": state["generated_at_utc"],
                    "reports": state["mechanicus"].get("latest_reports", []),
                }
            )
            return
        if path == "/api/mechanicus/screenshot/latest":
            self._serve_mechanicus_screenshot(index=None)
            return
        if path.startswith("/api/mechanicus/screenshot/"):
            suffix = path.replace("/api/mechanicus/screenshot/", "", 1).strip()
            if not suffix.isdigit():
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid screenshot index")
                return
            self._serve_mechanicus_screenshot(index=int(suffix))
            return
        if path in ("/api/actions", "/api/commands"):
            state = build_state(repo_root=REPO_ROOT)
            actions = list_actions(repo_root=REPO_ROOT, state=state)
            self._write_json(
                {
                    "generated_at_utc": state["generated_at_utc"],
                    "actions": actions,
                    "commands": state["mechanicus"].get("commands", []),
                    "execution_mode": "ALLOWLISTED_ACTIONS_ONLY",
                }
            )
            return
        if path == "/api/actions/history":
            self._write_json(
                {
                    "generated_at_utc": build_state(repo_root=REPO_ROOT)["generated_at_utc"],
                    "history": get_action_history(),
                }
            )
            return
        if path == "/api/terminal/history":
            self._write_json(
                {
                    "schema_version": "SANCTUM_MINI_TERMINAL_HISTORY_V0_3R",
                    "generated_at_utc": build_state(repo_root=REPO_ROOT)["generated_at_utc"],
                    "active_organ": "MECHANICUS_AGENT",
                    "organ": "MECHANICUS_AGENT",
                    "allowlist": terminal_allowlist(),
                    "history": get_terminal_history(),
                }
            )
            return

        if path in ("/", "/index.html"):
            self._write_file(STATIC_ROOT / "index.html")
            return
        if path.startswith("/static/"):
            relative = path.replace("/static/", "", 1)
            self._write_file(STATIC_ROOT / relative)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/api/actions/run", "/api/terminal/execute"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        payload, error_status, error_text = self._read_json_body()
        if error_status:
            self.send_error(error_status, error_text or "Invalid request")
            return

        state = build_state(repo_root=REPO_ROOT)

        if path == "/api/actions/run":
            action_id = str(payload.get("action_id", "")).strip()
            if not action_id:
                self._write_json(
                    {
                        "status": "BLOCK",
                        "error": "action_id is required",
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            result = run_action(action_id=action_id, repo_root=REPO_ROOT, state=state, source="action_button")
            response_status = HTTPStatus.OK if result.get("status") in {"PASS", "WARN"} else HTTPStatus.BAD_REQUEST
            self._write_json(result, status=response_status)
            return

        organ = str(payload.get("organ", "MECHANICUS_AGENT")).strip() or "MECHANICUS_AGENT"
        command = str(payload.get("command", "")).strip()
        result = execute_terminal_command(
            organ=organ,
            command=command,
            repo_root=REPO_ROOT,
            state=state,
        )
        response_status = HTTPStatus.OK if result.get("status") in {"PASS", "WARN", "BLOCK"} else HTTPStatus.BAD_REQUEST
        self._write_json(result, status=response_status)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sanctum Mini local dashboard server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface")
    parser.add_argument("--port", default=8765, type=int, help="Port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SanctumMiniHandler)
    print(f"SANCTUM MINI server started at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
