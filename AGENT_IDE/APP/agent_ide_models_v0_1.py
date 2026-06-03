from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping


TASK_ID = "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC"


@dataclass(frozen=True)
class ProviderDescriptor:
    provider_id: str
    enabled: bool
    kind: str
    source_key: str
    relative_path: str
    parse_mode: str
    required: bool
    description: str = ""

    @staticmethod
    def from_dict(raw: Mapping[str, Any]) -> "ProviderDescriptor":
        return ProviderDescriptor(
            provider_id=str(raw.get("provider_id", "")),
            enabled=bool(raw.get("enabled", True)),
            kind=str(raw.get("kind", "builtin_readonly_descriptor")),
            source_key=str(raw.get("source_key", "")),
            relative_path=str(raw.get("relative_path", "")),
            parse_mode=str(raw.get("parse_mode", "json")),
            required=bool(raw.get("required", False)),
            description=str(raw.get("description", "")),
        )


@dataclass
class FilePassport:
    path: str = ""
    owner_organ: str = "UNKNOWN"
    related_block: str = "UNKNOWN"
    file_kind: str = "UNKNOWN"
    purpose_short: str = ""
    status: str = "UNKNOWN"
    ide_visible: bool = True
    drilldown_priority: str = "LOW"
    related_owner_pains: List[str] = field(default_factory=list)
    edit_surface: str = "UNKNOWN"
    evidence_source: str = ""
    warnings: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(raw: Mapping[str, Any]) -> "FilePassport":
        return FilePassport(
            path=str(raw.get("path", "")),
            owner_organ=str(raw.get("owner_organ", "UNKNOWN")),
            related_block=str(raw.get("related_block", "UNKNOWN")),
            file_kind=str(raw.get("file_kind", "UNKNOWN")),
            purpose_short=str(raw.get("purpose_short", "")),
            status=str(raw.get("status", "UNKNOWN")),
            ide_visible=bool(raw.get("ide_visible", True)),
            drilldown_priority=str(raw.get("drilldown_priority", "LOW")),
            related_owner_pains=[str(x) for x in raw.get("related_owner_pains", [])],
            edit_surface=str(raw.get("edit_surface", "UNKNOWN")),
            evidence_source=str(raw.get("evidence_source", "")),
            warnings=[str(x) for x in raw.get("warnings", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "owner_organ": self.owner_organ,
            "related_block": self.related_block,
            "file_kind": self.file_kind,
            "purpose_short": self.purpose_short,
            "status": self.status,
            "ide_visible": self.ide_visible,
            "drilldown_priority": self.drilldown_priority,
            "related_owner_pains": list(self.related_owner_pains),
            "edit_surface": self.edit_surface,
            "evidence_source": self.evidence_source,
            "warnings": list(self.warnings),
        }


@dataclass
class IdeViewModel:
    task_id: str = TASK_ID
    truth: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    organs: List[Dict[str, Any]] = field(default_factory=list)
    file_passports: List[Dict[str, Any]] = field(default_factory=list)
    unknown_file_kind_count: int = 0
    role_rule_surface: Dict[str, Any] = field(default_factory=dict)
    language_gate_surface: Dict[str, Any] = field(default_factory=dict)
    checker_tool_surface: Dict[str, Any] = field(default_factory=dict)
    tui_surface: Dict[str, Any] = field(default_factory=dict)
    report_receipt_surface: Dict[str, Any] = field(default_factory=dict)
    route_surface: Dict[str, Any] = field(default_factory=dict)
    owner_pain_map: Dict[str, Any] = field(default_factory=dict)
    gap_success: Dict[str, Any] = field(default_factory=dict)
    selected_file: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "truth": dict(self.truth),
            "warnings": list(self.warnings),
            "organs": list(self.organs),
            "file_passports": list(self.file_passports),
            "unknown_file_kind_count": self.unknown_file_kind_count,
            "role_rule_surface": dict(self.role_rule_surface),
            "language_gate_surface": dict(self.language_gate_surface),
            "checker_tool_surface": dict(self.checker_tool_surface),
            "tui_surface": dict(self.tui_surface),
            "report_receipt_surface": dict(self.report_receipt_surface),
            "route_surface": dict(self.route_surface),
            "owner_pain_map": dict(self.owner_pain_map),
            "gap_success": dict(self.gap_success),
            "selected_file": dict(self.selected_file),
        }
