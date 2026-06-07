from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
IDE_ROOT = HERE.parent
OPS_ENGINE = IDE_ROOT / "OPS" / "ENGINE"
if str(OPS_ENGINE) not in sys.path:
    sys.path.insert(0, str(OPS_ENGINE))

from imperium_ops import astronomicon_register as astro  # noqa: E402
from imperium_ops import launch_card as launch_cards  # noqa: E402
from imperium_ops import task_console  # noqa: E402
from imperium_ops import taskpack_builder  # noqa: E402

from lifecycle_tracker import new_lifecycle, set_stage
from station_receipts import make_receipt, write_receipt
from station_state import StationState

_CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)api[_-]?key\s*[=:]"),
    re.compile(r"(?i)secret\s*[=:]"),
    re.compile(r"(?i)password\s*[=:]"),
    re.compile(r"(?i)token\s*[=:]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


class StationWorkflow:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.state = StationState(self.repo_root)
        self.generated_root = HERE / "generated_taskpacks"
        self.receipt_root = HERE / "receipts" / "runtime"
        self.template_path = IDE_ROOT / "OPS" / "TEMPLATES" / "task_templates.json"
        self.registration_skill = (
            self.repo_root
            / "ORGANS"
            / "ASTRONOMICON"
            / "SKILLS"
            / "TASKPACK_REGISTRATION_SKILL"
            / "astronomicon_taskpack_registration_skill_v0_1.py"
        )

    def templates(self) -> dict[str, Any]:
        with self.template_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return {"status": "PASS", "template_path": self.template_path.as_posix(), **data}

    def create_intent(
        self,
        title: str,
        goal: str = "",
        template_id: str = "integration",
    ) -> tuple[task_console.TaskIntent, dict[str, Any]]:
        templates = self.templates()["templates"]
        template = next((item for item in templates if item["template_id"] == template_id), None)
        if template is None:
            template = next(item for item in templates if item["template_id"] == "integration")
        intent = task_console.new_task(
            title=title,
            goal=goal or title,
            task_type=template["template_id"] if template["template_id"] in task_console.TASK_TYPES else None,
            scope=template["default_scope"],
            risk=template["default_risk"],
            organs_route=template["default_organs"],
            push_policy="VALIDATED_PUSH",
        )
        intent.allowed_write_scope = list(template["default_allowed_write_scope"])
        intent.forbidden_actions = list(template["default_forbidden_actions"])
        ok, problems = task_console.validate_intent(intent)
        preview = {
            "status": "PASS" if ok else "BLOCKED",
            "template_id": template["template_id"],
            "intent": intent.to_dict(),
            "problems": problems,
            "route_preview": [
                {"step": index + 1, "organ": organ, "mode": "DRY_RUN"}
                for index, organ in enumerate(intent.organs_route)
            ],
            "scope_preview": intent.allowed_write_scope,
            "mechanicus_policy": "DRY_RUN_REQUIRED_UNKNOWN_TOOL_BLOCKED",
        }
        return intent, preview

    def build_taskpack(self, title: str, goal: str = "", template_id: str = "integration") -> dict[str, Any]:
        intent, preview = self.create_intent(title, goal, template_id)
        if preview["status"] == "BLOCKED":
            return preview
        extracted = Path(taskpack_builder.write_taskpack(str(self.generated_root), intent))
        blockers = taskpack_builder.admission_precheck(str(extracted))
        zip_path = extracted.parent / "TASKPACK.zip"
        zip_info = taskpack_builder.build_zip(str(extracted), str(zip_path))
        return {
            "status": "PASS_WITH_WARNINGS" if not blockers else "BLOCKED",
            "mode": "DRY_RUN",
            "intent": intent.to_dict(),
            "route_preview": preview["route_preview"],
            "extracted_path": extracted.as_posix(),
            "taskpack_zip_path": zip_path.as_posix(),
            "taskpack_sha256": zip_info["sha256"],
            "file_count": zip_info["files"],
            "validation_blockers": blockers,
        }

    def validate_taskpack(self, extracted_path: str) -> dict[str, Any]:
        extracted = Path(extracted_path).resolve()
        blockers: list[str] = []
        if not extracted.is_relative_to(self.generated_root.resolve()):
            blockers.append("source path is outside STATION/generated_taskpacks")
        blockers.extend(taskpack_builder.admission_precheck(str(extracted)))
        secret_hits: list[str] = []
        if extracted.is_dir():
            for path in extracted.rglob("*"):
                if not path.is_file() or path.suffix.lower() == ".zip":
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    continue
                if any(pattern.search(text) for pattern in _CREDENTIAL_PATTERNS):
                    secret_hits.append(path.relative_to(extracted).as_posix())
        if secret_hits:
            blockers.append(f"credential-like content detected: {secret_hits}")
        return {
            "status": "PASS" if not blockers else "BLOCKED",
            "extracted_path": extracted.as_posix(),
            "required_root_files": taskpack_builder.REQUIRED_TASKPACK_FILES,
            "blockers": blockers,
            "secret_hits": secret_hits,
            "local_pc_only": True,
            "remote_registration_enabled": False,
        }

    def register_taskpack(
        self,
        title: str,
        goal: str = "",
        template_id: str = "integration",
        live: bool = False,
    ) -> dict[str, Any]:
        built = self.build_taskpack(title, goal, template_id)
        if built["status"] == "BLOCKED":
            return built
        validation = self.validate_taskpack(built["extracted_path"])
        intent, _ = self.create_intent(title, goal, template_id)
        blockers = list(validation["blockers"])
        if not self.registration_skill.is_file():
            blockers.append("Astronomicon registration skill path not found")

        if live:
            if blockers:
                result = {
                    "status": "BLOCKED",
                    "mode": "LIVE_LOCAL_PC",
                    "blockers": blockers,
                    "registered": False,
                }
            else:
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(self.registration_skill),
                        "--repo-root",
                        str(self.repo_root),
                        "--zip-path",
                        built["taskpack_zip_path"],
                        "--contour",
                        "PC",
                        "--print-launch-card",
                    ],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                    check=False,
                )
                result = {
                    "status": "PASS_WITH_WARNINGS" if completed.returncode == 0 else "BLOCKED",
                    "mode": "LIVE_LOCAL_PC",
                    "registered": completed.returncode == 0,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout[-6000:].strip(),
                    "stderr": completed.stderr[-2000:].strip(),
                    "blockers": [] if completed.returncode == 0 else ["Astronomicon skill returned non-zero"],
                }
        else:
            registration = astro.register(
                str(self.repo_root),
                built["extracted_path"],
                intent,
                dry_run=True,
            )
            result = {
                "status": "PASS_WITH_WARNINGS" if registration.admitted else "BLOCKED",
                "mode": "DRY_RUN",
                "registered": registration.admitted,
                "registration": registration.to_dict(),
                "blockers": registration.blockers,
            }

        receipt = make_receipt(
            "station_registration",
            result["status"],
            task_id=intent.task_id,
            live=live,
            dry_run_default=True,
            local_pc_only=True,
            remote_registration_enabled=False,
            source_path=built["taskpack_zip_path"],
            registration_skill_path=self.registration_skill.as_posix(),
            validation=validation,
            result=result,
        )
        receipt_path = self.receipt_root / f"{intent.task_id}_registration_receipt.json"
        result["receipt_path"] = write_receipt(receipt_path, receipt)
        result["built"] = built
        return result

    def launch_card(self, title: str, goal: str = "", template_id: str = "integration") -> dict[str, Any]:
        registration = self.register_taskpack(title, goal, template_id, live=False)
        intent, _ = self.create_intent(title, goal, template_id)
        reg_data = registration.get("registration", {})
        card = launch_cards.build_launch_card(
            intent,
            reg_data.get("registered_path", ""),
            bool(reg_data.get("admitted")),
            reg_data.get("sha256", ""),
        )
        return {
            "status": "PASS_WITH_WARNINGS" if card["admission"] == "ADMITTED" else "BLOCKED",
            "card": card,
            "text": launch_cards.render_launch_card_text(card),
        }

    def handoff_card(self, title: str, goal: str = "", template_id: str = "integration") -> dict[str, Any]:
        launch = self.launch_card(title, goal, template_id)
        task_id = launch.get("card", {}).get("task_id", "UNKNOWN_TASK")
        return {
            "status": launch["status"],
            "task_id": task_id,
            "handoff_target": "SERVITOR_PRIME",
            "handoff_mode": "COPY_READY_EXTERNAL_HANDOFF",
            "execution_started": False,
            "message": (
                f"SERVITOR PRIME HANDOFF: {task_id}. Read the registered taskpack, "
                "acknowledge scope and forbidden actions, then wait for an explicit execution gate."
            ),
            "blocked_actions": ["real_servitor_execution", "live_llm_backend", "unsafe_shell"],
        }

    def lifecycle(self, title: str, goal: str = "", template_id: str = "integration") -> dict[str, Any]:
        state = new_lifecycle("PENDING")
        intent, preview = self.create_intent(title, goal, template_id)
        state["task_id"] = intent.task_id
        set_stage(state, "INTENT_CAPTURED", "ACTIVE", title)
        set_stage(state, "CLASSIFIED", "ACTIVE" if preview["status"] != "BLOCKED" else "FAILED", intent.task_type)
        set_stage(state, "ROUTE_PREVIEWED", "DRY_RUN", " -> ".join(intent.organs_route))
        set_stage(state, "POLICY_CHECKED", "ACTIVE", "Mechanicus dry-run policy respected")
        built = self.build_taskpack(title, goal, template_id)
        set_stage(state, "TASKPACK_BUILT", "DRY_RUN" if built["status"] != "BLOCKED" else "FAILED", built.get("taskpack_zip_path", ""))
        validation = self.validate_taskpack(built.get("extracted_path", ""))
        set_stage(state, "TASKPACK_VALIDATED", "ACTIVE" if validation["status"] == "PASS" else "FAILED", str(validation["blockers"]))
        registration = self.register_taskpack(title, goal, template_id, live=False)
        set_stage(state, "DRY_RUN_REGISTERED", "DRY_RUN" if registration["status"] != "BLOCKED" else "FAILED", registration.get("receipt_path", ""))
        set_stage(state, "LIVE_REGISTERED", "BLOCKED", "live registration requires explicit owner confirmation")
        launch = self.launch_card(title, goal, template_id)
        set_stage(state, "LAUNCH_CARD_READY", "DRY_RUN" if launch["status"] != "BLOCKED" else "FAILED", launch.get("text", "")[:200])
        handoff = self.handoff_card(title, goal, template_id)
        set_stage(state, "HANDOFF_READY", "DRY_RUN", handoff["message"])
        set_stage(state, "EXECUTION_STARTED", "BLOCKED", "real execution gate is not open")
        snapshot = self.state.snapshot()
        set_stage(state, "REPORT_DETECTED", snapshot["reports"]["state"], "latest reports visible")
        set_stage(state, "VALIDATION_DETECTED", "ACTIVE", "station validation available")
        set_stage(state, "BUNDLE_GATE_CHECKED", "DRY_RUN", "Administratum gate remains explicit")
        set_stage(state, "GIT_CLOSURE_CHECKED", snapshot["git_closure"]["state"], "git truth visible")
        set_stage(state, "CLOSED_OR_BLOCKED", "BLOCKED", "execution is pending; no fake closure")
        return {"status": "PASS_WITH_WARNINGS", "lifecycle": state, "handoff": handoff}

    def smoke(self) -> dict[str, Any]:
        title = "Station operational workflow smoke"
        built = self.build_taskpack(title, "Validate station task creation workflow", "integration")
        validation = self.validate_taskpack(built["extracted_path"])
        registration = self.register_taskpack(title, "Validate station task creation workflow", "integration")
        launch = self.launch_card(title, "Validate station task creation workflow", "integration")
        handoff = self.handoff_card(title, "Validate station task creation workflow", "integration")
        lifecycle = self.lifecycle(title, "Validate station task creation workflow", "integration")
        snapshot = self.state.snapshot()
        checks = {
            "state_snapshot_active": snapshot["state"] == "ACTIVE",
            "templates_visible": bool(self.templates().get("templates")),
            "taskpack_built": built["status"] != "BLOCKED",
            "taskpack_valid": validation["status"] == "PASS",
            "dry_registration_passed": registration["status"] != "BLOCKED",
            "launch_card_captured": bool(launch.get("text")),
            "handoff_ready_without_execution": handoff["execution_started"] is False,
            "lifecycle_tracks_execution_pending": lifecycle["lifecycle"]["execution_complete"] is False,
            "agents_visible": snapshot["agents"]["agent_count"] >= 12,
            "reports_visible": snapshot["reports"]["state"] in {"LIVE", "UNKNOWN"},
            "receipts_visible": snapshot["receipts"]["state"] in {"LIVE", "UNKNOWN"},
            "safety_visible": snapshot["safety"]["result"] == "PASS_WITH_WARNINGS",
            "git_visible": bool(snapshot["git_closure"]["head"]),
        }
        return {
            "status": "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED",
            "checks": checks,
            "built": built,
            "validation": validation,
            "registration": registration,
            "launch_card": launch,
            "handoff": handoff,
            "lifecycle": lifecycle,
            "live_registration_smoke": {
                "status": "BLOCKED",
                "reason": (
                    "not run automatically because canonical Astronomicon registration would "
                    "replace current expected task; explicit owner station action is available"
                ),
            },
        }
