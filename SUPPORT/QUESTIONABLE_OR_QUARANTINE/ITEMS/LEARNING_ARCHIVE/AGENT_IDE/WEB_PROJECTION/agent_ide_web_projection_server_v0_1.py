from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

import sys

WEB_DIR = Path(__file__).resolve().parent
VIEW_MODEL_DIR = WEB_DIR.parent / "VIEW_MODEL"
REACT_DIST_DIR = WEB_DIR.parent / "REACT_IDE" / "dist"
PLUGIN_MANIFEST_PATH = WEB_DIR.parent / "PLUGINS" / "builtin_readonly_providers_v0_1.json"
DESKTOP_SHELL_DIR = WEB_DIR.parent / "DESKTOP_SHELL"
REPORT_DIR_CURRENT_TASK = (
    WEB_DIR.parent
    / "REPORTS"
    / "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
)
REPORT_DIR_PREVIOUS_TASK = (
    WEB_DIR.parent
    / "REPORTS"
    / "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
)
SELF_VALIDATOR_SUMMARY_FILE = "self_validation_summary.json"

ALLOWED_PREVIEW_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".py",
    ".ps1",
    ".cmd",
    ".toml",
    ".yml",
    ".yaml",
    ".ts",
    ".tsx",
    ".js",
    ".css",
    ".html",
}
PREVIEW_MAX_CHARS = 12000
PREVIEW_MAX_LINES = 240

if str(VIEW_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(VIEW_MODEL_DIR))

from agent_ide_view_model_builder_v0_2 import (  # noqa: E402
    build_and_persist_models,
    build_models,
    discover_repo_root,
)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json_safe(path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not path.exists():
        return default or {}
    try:
        return _read_json(path)
    except Exception:
        return default or {}


def _ensure_models(repo_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    build_and_persist_models(repo_root)
    return build_models(repo_root)


def _select_static_dir() -> Path:
    if (REACT_DIST_DIR / "index.html").exists():
        return REACT_DIST_DIR
    return WEB_DIR


def _is_restricted_path(raw_path: str) -> bool:
    upper = raw_path.upper().replace("\\", "/")
    if "/PRIVATE/" in upper or "/LOCAL/" in upper:
        return True
    return False


def _safe_preview(repo_root: Path, raw_path: str) -> Dict[str, Any]:
    if not raw_path or raw_path == "[RESTRICTED]":
        return {
            "allowed": False,
            "path": raw_path,
            "reason": "RESTRICTED_OR_EMPTY_PATH",
            "content": "",
        }
    if ":" in raw_path:
        return {
            "allowed": False,
            "path": raw_path,
            "reason": "ABSOLUTE_PATH_NOT_ALLOWED",
            "content": "",
        }

    normalized = raw_path.replace("\\", "/").lstrip("/")
    candidate = (repo_root / normalized).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return {
            "allowed": False,
            "path": raw_path,
            "reason": "OUTSIDE_REPO_BOUNDARY",
            "content": "",
        }

    if _is_restricted_path(normalized):
        return {
            "allowed": False,
            "path": raw_path,
            "reason": "PRIVATE_LOCAL_POLICY_RESTRICTED",
            "content": "",
        }
    if not candidate.exists() or not candidate.is_file():
        return {
            "allowed": False,
            "path": raw_path,
            "reason": "FILE_NOT_FOUND",
            "content": "",
        }

    ext = candidate.suffix.lower()
    if ext not in ALLOWED_PREVIEW_EXTENSIONS:
        return {
            "allowed": False,
            "path": raw_path,
            "reason": f"EXTENSION_NOT_ALLOWED::{ext}",
            "content": "",
        }

    try:
        lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        return {
            "allowed": False,
            "path": raw_path,
            "reason": f"READ_ERROR::{exc}",
            "content": "",
        }

    preview_lines = lines[:PREVIEW_MAX_LINES]
    content = "\n".join(preview_lines)
    truncated = len(lines) > PREVIEW_MAX_LINES or len(content) > PREVIEW_MAX_CHARS
    if len(content) > PREVIEW_MAX_CHARS:
        content = content[:PREVIEW_MAX_CHARS]

    return {
        "allowed": True,
        "path": normalized,
        "line_count_total": len(lines),
        "line_count_preview": len(preview_lines),
        "truncated": truncated,
        "content": content,
    }


class ProjectionHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str | None = None, repo_root: Path | None = None, **kwargs: Any):
        self.repo_root = repo_root or discover_repo_root()
        self.static_dir = _select_static_dir()
        super().__init__(*args, directory=directory, **kwargs)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/view-model":
            full_model, dashboard_model, _block_model = _ensure_models(self.repo_root)
            payload = dict(dashboard_model)
            payload["checker_tool_surface"] = full_model.get("checker_tool_surface", {})
            payload["plugin_surface"] = _read_json_safe(PLUGIN_MANIFEST_PATH, default={"providers": []})
            self._send_json(payload)
            return
        if parsed.path == "/api/block-view-model":
            _full_model, _dashboard_model, block_model = _ensure_models(self.repo_root)
            self._send_json(block_model)
            return
        if parsed.path == "/api/plugins":
            self._send_json(_read_json_safe(PLUGIN_MANIFEST_PATH, default={"providers": []}))
            return
        if parsed.path == "/api/toolchain-probe":
            probe_path = DESKTOP_SHELL_DIR / "tauri_probe_receipt.json"
            self._send_json(_read_json_safe(probe_path, default={"status": "UNPROVEN", "probes": []}))
            return
        if parsed.path == "/api/desktop-shell-decision":
            decision_path = DESKTOP_SHELL_DIR / "tauri_or_electron_decision_v0_1.json"
            self._send_json(_read_json_safe(decision_path, default={"status": "UNPROVEN", "decision": "UNKNOWN"}))
            return
        if parsed.path == "/api/self-validator-summary":
            current = REPORT_DIR_CURRENT_TASK / SELF_VALIDATOR_SUMMARY_FILE
            previous = REPORT_DIR_PREVIOUS_TASK / SELF_VALIDATOR_SUMMARY_FILE
            if current.exists():
                self._send_json(_read_json_safe(current, default={"status": "UNPROVEN"}))
                return
            self._send_json(_read_json_safe(previous, default={"status": "UNPROVEN"}))
            return
        if parsed.path == "/api/file-preview":
            query = parse_qs(parsed.query)
            raw_path = ""
            if "path" in query and query["path"]:
                raw_path = str(query["path"][0])
            self._send_json(_safe_preview(self.repo_root, raw_path))
            return
        if parsed.path == "/api/health":
            full_model, dashboard_model, _block_model = _ensure_models(self.repo_root)
            self._send_json(
                {
                    "status": "PASS",
                    "schema_version": dashboard_model.get("schema_version", ""),
                    "head": full_model.get("truth", {}).get("git", {}).get("head", "UNKNOWN"),
                    "warnings_count": len(dashboard_model.get("warnings", [])),
                    "passport_count": dashboard_model.get("atlas_summary", {}).get("passport_count", 0),
                    "ui_mode": "REACT_DIST" if self.static_dir == REACT_DIST_DIR else "LEGACY_FALLBACK",
                }
            )
            return
        request_path = parsed.path
        if request_path in {"", "/"}:
            self.path = "/index.html"
            return super().do_GET()

        file_candidate = (self.static_dir / request_path.lstrip("/")).resolve()
        if file_candidate.exists() and file_candidate.is_file():
            self.path = request_path
            return super().do_GET()

        if self.static_dir == REACT_DIST_DIR and (self.static_dir / "index.html").exists():
            self.path = "/index.html"
            return super().do_GET()

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")


def run_server(host: str, port: int, repo_root: Path) -> None:
    def handler(*args: Any, **kwargs: Any) -> ProjectionHandler:
        return ProjectionHandler(*args, directory=str(_select_static_dir()), repo_root=repo_root, **kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(
        json.dumps(
            {
                "status": "LISTENING",
                "host": host,
                "port": port,
                "url": f"http://{host}:{port}",
                "repo_root": repo_root.as_posix(),
                "ui_mode": "REACT_DIST" if _select_static_dir() == REACT_DIST_DIR else "LEGACY_FALLBACK",
            },
            ensure_ascii=False,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent IDE web projection server (local-only).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()
    run_server(args.host, args.port, repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
