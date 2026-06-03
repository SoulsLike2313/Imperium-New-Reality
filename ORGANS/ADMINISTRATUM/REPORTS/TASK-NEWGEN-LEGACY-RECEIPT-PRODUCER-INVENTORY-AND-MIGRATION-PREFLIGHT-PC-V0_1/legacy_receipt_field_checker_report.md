# Legacy Receipt Field Checker Report

- scan_id: legacy_receipt_field_scan_v0_1
- scanned_root: IMPERIUM_NEW_GENERATION
- dangerous_fields: final_head, closure_head, commit_hash, remote_head, head, finalization_head, review_target, PASS, clean_pass

## Classification Summary
- SAFE_NEW_SEMANTICS: 14
- AMBIGUOUS_LEGACY_FIELD: 16
- LIKELY_SELF_HEAD_RISK: 4
- MANUAL_REVIEW: 322
- NOT_APPLICABLE: 217

## Top Non-Safe Findings
| classification | risk | owner | field | path | reason |
|---|---|---|---|---|---|
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_card_checker_v0_1.py` | line 12: DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "schema_validation_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_current_truth_checker_v0_1.py` | line 15: DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "current_truth_checker_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_current_truth_checker_v0_1.py` | line 15: DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "current_truth_checker_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_file_atlas_builder_v0_1.py` | line 38: "RECEIPT", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_file_atlas_checker_v0_1.py` | line 13: DEFAULT_OUTPUT = REPORT_ROOT / "file_atlas_check_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_file_atlas_tui_smoke_v0_1.py` | line 14: DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "tui_smoke_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_organ_query_v0_1.py` | line 15: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TOOLS/administratum_tui_smoke_v0_1.py` | line 14: DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "tui_smoke_receipt.json" |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TUI/LAUNCH_ADMINISTRATUM_TUI_V0_1.cmd` | no_signal_line_found |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TUI/administratum_tui_v0_1.py` | line 115: print(f"- {entry.get('warn_id', 'WARN')}: {entry.get('summary', '')}") |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TUI/administratum_tui_v0_1.py` | line 115: print(f"- {entry.get('warn_id', 'WARN')}: {entry.get('summary', '')}") |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/APP/agent_ide_app_v0_1.py` | line 24: "routes": "Routes / Reports / Receipts", |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/APP/agent_ide_data_loader_v0_1.py` | line 157: report_surface = payloads.get("report_receipt_index", {}) |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_capture_v0_1.py` | no_signal_line_found |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_capture_v0_2.py` | no_signal_line_found |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_parity_v0_2.spec.js` | line 32: "self-validator-verdict", |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/REACT_IDE/src/App.js` | line 16: reports: "Reports / Receipts", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/SELF_VALIDATOR/agent_ide_self_validator_v0_1.py` | line 82: build_summary = build_and_persist_models(repo_root) |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/SELF_VALIDATOR/agent_ide_self_validator_v0_1.py` | line 82: build_summary = build_and_persist_models(repo_root) |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/SELF_VALIDATOR/agent_ide_self_validator_v0_2.py` | line 97: build_summary = build_and_persist_models(repo_root) |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/SELF_VALIDATOR/agent_ide_self_validator_v0_2.py` | line 97: build_summary = build_and_persist_models(repo_root) |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_block_registry_checker_v0_1.py` | line 14: "/block_registry_check_receipt.json" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_data_probe_v0_1.py` | line 56: "--receipt-out", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_desktop_shell_probe_v0_1.py` | line 123: probe_path = desktop_shell_dir / "tauri_probe_receipt.json" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_react_build_check_v0_1.py` | line 61: receipt_path = report_dir / "react_build_check_receipt.json" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_scope_checker_v0_1.py` | line 38: "--receipt-out", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_scope_checker_v0_2.py` | line 45: "--receipt-out", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_smoke_test_v0_1.py` | line 25: "--receipt-out", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/AGENT_IDE/WEB_PROJECTION/agent_ide_web_projection_server_v0_1.py` | line 28: SELF_VALIDATOR_SUMMARY_FILE = "self_validation_summary.json" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/WEB_PROJECTION/agent_ide_web_projection_server_v0_1.py` | line 28: SELF_VALIDATOR_SUMMARY_FILE = "self_validation_summary.json" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/AGENT_IDE/WEB_PROJECTION/app.js` | line 11: reportsReceipts: "Reports / Receipts", |
| MANUAL_REVIEW | P2 | ASTRONOMICON | PASS | `IMPERIUM_NEW_GENERATION/ASTRONOMICON/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | ASTRONOMICON | PASS | `IMPERIUM_NEW_GENERATION/ASTRONOMICON/TOOLS/astronomicon_organ_query_v0_1.py` | line 15: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | ASTRONOMICON | PASS | `IMPERIUM_NEW_GENERATION/ASTRONOMICON/TOOLS/astronomicon_route_packet_checker_v0_1.py` | line 21: "required_receipts", |
| MANUAL_REVIEW | P1 | ASTRONOMICON | PASS | `IMPERIUM_NEW_GENERATION/ASTRONOMICON/TOOLS/astronomicon_task_essence_checker_v0_1.py` | line 16: "task_summary", |
| MANUAL_REVIEW | P1 | ASTRONOMICON | PASS | `IMPERIUM_NEW_GENERATION/ASTRONOMICON/TOOLS/astronomicon_tui_smoke_v0_1.py` | line 23: verdict = "PASS" if smoke_ok else "BLOCK" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/base_half_cli.py` | line 113: identity_summary: str |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/base_half_cli.py` | line 113: identity_summary: str |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/officio_contract_check.py` | line 59: if re.match(r"^(STEP/BUNDLE/VERDICT/OWNER COMMENTS)\s*:", stripped, flags=re.IGNORECASE): |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/operator_shell_widgets.py` | line 69: tool_summary = payload.get("tool_summary", {}) if isinstance(payload.get("tool_summary"), dict) else {} |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/run_eight_organ_operator_shell_sweep.py` | line 447: verdict = "PASS_RICH_OPERATOR_SHELL_8_ORGANS" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/run_eight_organ_sweep.py` | line 62: for key in ("verdict", "status", "decision"): |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py` | line 12: STAGE_TYPES = {"PLAN", "IMPLEMENT", "VERIFY", "INTEGRATE", "REPORT", "HANDOFF"} |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py` | line 12: STAGE_TYPES = {"PLAN", "IMPLEMENT", "VERIFY", "INTEGRATE", "REPORT", "HANDOFF"} |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py` | line 141: {"phase_id": "S5", "phase_name": "report_and_release", "goal": "reports, receipts, commit", "checkpoint_gate": True}, |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/tool_registry_reader.py` | line 46: "capability_summary": "future graph/task-map tooling capability", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CAPABILITY_RECEIPT.schema.json` | line 3: "title": "TOOL_CAPABILITY_RECEIPT", |
| MANUAL_REVIEW | P2 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TEMPLATES/task_start_doctrinarium_block_v0_1.md` | line 31: - verdict_boundary: PASS_FOR_<SLICE>_ONLY |
| MANUAL_REVIEW | P2 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TEMPLATES/task_start_full_boot_sequence_v0_1.md` | line 49: - If organ route returns `Owner Verdict Needed`, STOP and wait. |
| MANUAL_REVIEW | P2 | DOCTRINARIUM | head | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TEMPLATES/task_start_full_boot_sequence_v0_1.md` | line 49: - If organ route returns `Owner Verdict Needed`, STOP and wait. |
| MANUAL_REVIEW | P1 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py` | no_signal_line_found |
| MANUAL_REVIEW | P2 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/TOOLS/doctrinarium_organ_query_v0_1.py` | line 15: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | DOCTRINARIUM | PASS | `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/TUI/doctrinarium_tui_v0_1.py` | line 17: build_verdict_payload, |
| MANUAL_REVIEW | P2 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/INQUISITION/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/INQUISITION/TOOLS/inquisition_organ_query_v0_1.py` | line 15: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/INQUISITION/TUI/inquisition_shell_v0_1.py` | line 47: "fakegreen": "Detect unscoped PASS risk from closure verdict", |
| MANUAL_REVIEW | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/INQUISITION/TUI/inquisition_tui_v0_1.py` | line 17: build_verdict_payload, |
| AMBIGUOUS_LEGACY_FIELD | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/HEAD_TAXONOMY_MANIFEST_TEMPLATE.json` | line 7: "receipt_finalization_head": "", |
| AMBIGUOUS_LEGACY_FIELD | P2 | UNKNOWN | review_target | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/REVIEW_TARGET_MANIFEST_TEMPLATE.json` | no_signal_line_found |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.ps1` | line 5: $outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-... |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.sh` | line 6: OUTPUT_DIR="${REPO_ROOT}/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-... |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_head_taxonomy_adjudication.ps1` | no_signal_line_found |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_head_taxonomy_adjudication.py` | line 124: combined = payload.get("combined_review_adjudication_receipt") |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_head_taxonomy_adjudication.py` | line 124: combined = payload.get("combined_review_adjudication_receipt") |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_head_taxonomy_adjudication.sh` | no_signal_line_found |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1` | line 5: $outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-... |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh` | line 6: OUTPUT_DIR="${REPO_ROOT}/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-... |
| AMBIGUOUS_LEGACY_FIELD | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_review_target_alignment.ps1` | no_signal_line_found |
| MANUAL_REVIEW | P2 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_review_target_alignment.py` | line 84: "previous_closure_head", |
| MANUAL_REVIEW | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_review_target_alignment.py` | line 84: "previous_closure_head", |
| AMBIGUOUS_LEGACY_FIELD | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_review_target_alignment.sh` | no_signal_line_found |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.ps1` | line 5: $outputDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-... |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.py` | line 14: TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.py` | line 14: TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1" |
| AMBIGUOUS_LEGACY_FIELD | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh` | line 6: OUTPUT_DIR="${REPO_ROOT}/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-... |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/score_efficiency_delta.py` | line 2: """Compute 5-scale efficiency delta receipt for Matrix Spine runtime corridor task.""" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/score_efficiency_delta.py` | line 2: """Compute 5-scale efficiency delta receipt for Matrix Spine runtime corridor task.""" |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py` | line 14: TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py` | line 14: TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1" |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/TOOLS/validate_ssh_connection_matrix_v0_1.py` | line 263: verdict = "PASS" |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_2.py` | line 116: def receipt_records() -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_2.py` | line 116: def receipt_records() -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_3.py` | line 118: def receipt_records() -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_3.py` | line 118: def receipt_records() -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_4.py` | line 116: def update_status_summary(self) -> None: |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_5_ru.py` | line 72: "ARSENAL/RECEIPTS": "КВИТАНЦИИ", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_5_ru.py` | line 72: "ARSENAL/RECEIPTS": "КВИТАНЦИИ", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_6_soft_ru.py` | line 149: def update_status_summary(self) -> None: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_7_heraldry.py` | no_signal_line_found |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_8_clean_seals.py` | no_signal_line_found |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_9_steampunk.py` | line 214: def update_status_summary(self) -> None: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v0_9_steampunk.py` | line 214: def update_status_summary(self) -> None: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_client_v1_0_no_fake_heraldry.py` | no_signal_line_found |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_tui_v0_1.py` | line 116: def discover_receipts(repo_root: Path) -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_tui_v0_1.py` | line 116: def discover_receipts(repo_root: Path) -> list[dict[str, Any]]: |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1/build_assets_v0_1.py` | line 77: "expected_receipts", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1/build_assets_v0_1.py` | line 77: "expected_receipts", |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1/DOSSIER_SOURCE/ACCEPTANCE_GATES.md` | line 11: 6. No fake CANON: every CANON card has receipt/evidence. |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1/DOSSIER_SOURCE/TEMPLATES/closure_receipt.template.json` | line 3: "verdict": "PASS / PASS_WITH_WARNINGS / BLOCKED / FAIL", |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1/DOSSIER_SOURCE/TEMPLATES/validation_receipt.template.json` | line 2: "receipt_id": "", |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1/DOSSIER_SOURCE/ACCEPTANCE_GATES.md` | line 11: 5. Validation receipts were created for successful checks. |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1/DOSSIER_SOURCE/TEMPLATES/ghost_evolve_training_proof.template.json` | line 9: "receipts": [], |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1/DOSSIER_SOURCE/TEMPLATES/validation_receipt.template.json` | line 2: "receipt_id": "", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/scripts/run_wave001_controlled_install.py` | line 346: receipts_root = report_root / "receipts" |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/scripts/run_wave001_controlled_install.py` | line 346: receipts_root = report_root / "receipts" |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/build_mechanicus_arsenal_field_guide_batch_001.py` | line 117: return "PROMOTE_CANON_AFTER_RECEIPT" |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/build_mechanicus_arsenal_field_guide_batch_001.py` | line 117: return "PROMOTE_CANON_AFTER_RECEIPT" |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_field_guide_batch_001.py` | line 84: report_root / "closure_receipt.json", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_foundation_v0_1.py` | line 32: "expected_receipts", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_mass_intake_v0_1.py` | line 56: promoted_by = str(card.get("promoted_by_receipt", "")) |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py` | line 17: "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS/**/*.json", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_owner_approval_matrix_v0_1.py` | line 56: "receipt_required", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_scope_packs_v0_1.py` | line 38: "required_receipts", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_owner_approved_tool_normalization_v0_1.py` | line 121: "normalization_receipt.json", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/evidence_index_smoke_v0_1.py` | line 106: ("gate OR verdict OR fake", MAX_QUERY_RESULTS), |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/generate_mechanicus_arsenal_mass_intake_v0_1.py` | line 120: "Claiming CANON without validation receipt evidence", |
| MANUAL_REVIEW | P0 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py` | line 26: required_receipts: tuple[str, ...] |
| MANUAL_REVIEW | P0 | MECHANICUS | commit_hash | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py` | line 26: required_receipts: tuple[str, ...] |
| MANUAL_REVIEW | P0 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py` | line 26: required_receipts: tuple[str, ...] |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_validator_v0_1.py` | line 13: from mechanicus_validation_receipt_builder_v0_1 import build_validation_receipt, write_receipt |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_validator_v0_1.py` | line 13: from mechanicus_validation_receipt_builder_v0_1 import build_validation_receipt, write_receipt |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py` | line 14: from mechanicus_install_receipt_builder_v0_1 import ( |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py` | line 14: from mechanicus_install_receipt_builder_v0_1 import ( |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py` | line 16: MAX_SUMMARY_CHARS = 240 |
| MANUAL_REVIEW | P1 | MECHANICUS | commit_hash | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py` | line 16: MAX_SUMMARY_CHARS = 240 |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_query_runner_v0_1.py` | line 69: SELECT source_path, title, summary |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py` | line 47: promoted_by = str(card.get("promoted_by_receipt", "")).strip() |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_organ_query_v0_1.py` | line 16: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_owner_approval_matrix_builder_v0_1.py` | line 50: "receipt_required", |
| MANUAL_REVIEW | P0 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py` | line 54: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P0 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py` | line 54: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P0 | MECHANICUS | remote_head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py` | line 54: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_schema_validation_runner_v0_1.py` | line 178: verdict = "PASS" |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_scope_pack_consumer_v0_1.py` | line 26: "required_receipts", |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_taskpack_validator_v0_1.py` | line 27: "TEMPLATES/closure_receipt.template.json", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_detection_runner_v0_1.py` | line 13: from mechanicus_validation_receipt_builder_v0_1 import ( |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_candidate_builder_v0_1.py` | line 52: notes="Primary search accelerator for reports/receipts/card lookup.", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_candidate_builder_v0_1.py` | line 52: notes="Primary search accelerator for reports/receipts/card lookup.", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_decision_builder_v0_1.py` | line 28: "SEARCH_INDEXING_RECEIPT_PATH_INDEX", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_finalize_v0_1.py` | line 177: ("receipt", "receipt"), |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_finalize_v0_1.py` | line 177: ("receipt", "receipt"), |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_scope_refresh_v0_1.py` | line 25: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_scope_refresh_v0_1.py` | line 25: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py` | line 13: from mechanicus_validation_receipt_builder_v0_1 import build_validation_receipt, write_receipt |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py` | line 13: from mechanicus_validation_receipt_builder_v0_1 import build_validation_receipt, write_receipt |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_validation_receipt_builder_v0_1.py` | line 21: def make_receipt_id(task_id: str, capability_id: str, check_name: str) -> str: |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/newgen_repo_hygiene_check_v0_1.py` | line 98: verdict = "PASS" if total_hits == 0 else "WARN" |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/MECHANICUS/TUI/mechanicus_tui_v0_1.py` | line 18: build_verdict_payload, |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/TOOLS/officio_boot_ack_v0_1.py` | line 72: ack_verdict = "PASS" if all_ack else "STOP" |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TEMPLATES/OFFICIO_4_PART_FINAL_RESPONSE_TEMPLATE_RU_V0_1.md` | no_signal_line_found |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TEMPLATES/OFFICIO_ROLE_ACK_BLOCK_TEMPLATE_V0_1.md` | line 20: - expected_receipts: <REPORT/RECEIPT LIST> |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | head | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TEMPLATES/OFFICIO_ROLE_ACK_BLOCK_TEMPLATE_V0_1.md` | line 20: - expected_receipts: <REPORT/RECEIPT LIST> |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TEMPLATES/organ_verdict_template_v0_1.json` | line 2: "schema_id": "newgen_organ_verdict_v0_1", |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_organ_query_v0_1.py` | line 15: from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_response_contract_checker_v0_1.py` | line 109: def has_russian_owner_summary(text: str) -> bool: |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_role_pack_exporter_v0_1.py` | line 80: f"- verdict: PASS\n\n" |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_role_registry_checker_v0_1.py` | no_signal_line_found |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_taskpack_acceptance_checker_v0_1.py` | line 31: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P2 | OFFICIO_AGENTIS | head | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_taskpack_acceptance_checker_v0_1.py` | line 31: "GATE-U04-EVIDENCE-RECEIPT", |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TUI/LAUNCH_OFFICIO_AGENTIS_TUI_V0_1.cmd` | line 3: python "%~dp0officio_agentis_tui_v0_1.py" --mode summary --strict |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TUI/officio_tui_v0_1.py` | line 17: build_verdict_payload, |
| AMBIGUOUS_LEGACY_FIELD | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/CONTRACTS/NEXT_PIPELINE_HANDOFF_AND_CLOSURE_PROVENANCE_CONTRACT_V0_1.md` | line 1: # Next Pipeline Handoff and Closure Provenance Contract V0.1 |
| AMBIGUOUS_LEGACY_FIELD | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/CONTRACTS/CAP_CLOSURE_SEMANTICS_CONTRACT.md` | line 9: A cap changes state only with explicit evidence and state receipt. |
| AMBIGUOUS_LEGACY_FIELD | P1 | INQUISITION | head | `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/CONTRACTS/CAP_CLOSURE_SEMANTICS_CONTRACT.md` | line 9: A cap changes state only with explicit evidence and state receipt. |
| AMBIGUOUS_LEGACY_FIELD | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/CONTRACTS/HARD_RED_TEAM_CLOSURE_GATE.md` | line 11: - stale receipt; |
| AMBIGUOUS_LEGACY_FIELD | P1 | INQUISITION | head | `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/CONTRACTS/HARD_RED_TEAM_CLOSURE_GATE.md` | line 11: - stale receipt; |
| MANUAL_REVIEW | P2 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1/HEAD_TAXONOMY_MANIFEST.json` | no_signal_line_found |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py` | line 43: build_agent_handoff_context, |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py` | line 43: build_agent_handoff_context, |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_dossier_factory.py` | line 308: verdict: str |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_dossier_factory.py` | line 308: verdict: str |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py` | line 35: "build_merge_preparation_summary", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py` | line 35: "build_merge_preparation_summary", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_gate_core_v0_1.py` | line 79: "ledger_receipts": root / "LEDGER" / "RECEIPTS", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_push_vm2_v0_1.py` | line 50: return 0 if not str(result.get("verdict", "")).startswith("BLOCKED") else 1 |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_send_vm2_v0_1.py` | line 17: parser.add_argument("--source-head", default="UNKNOWN", help="Source repository HEAD to stamp in receipt.") |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/TEMPLATES/START_PROMPT.template.txt` | no_signal_line_found |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/TESTS/test_transfer_gate_pc_push_fetch_v0_1.py` | line 66: "verdict": "SYNTHETIC_PASS", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/TESTS/test_transfer_gate_pc_push_fetch_v0_1.py` | line 66: "verdict": "SYNTHETIC_PASS", |
| MANUAL_REVIEW | P1 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/TESTS/test_transfer_gate_v0_1.py` | line 77: "verdict": "SYNTHETIC_PASS", |
| MANUAL_REVIEW | P1 | INQUISITION | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/INQUISITION_AGENT/TOOLS/inquisition_agent_runner.py` | line 17: identity_summary="Audit, anti-fake-green, scope integrity, and evidence truth enforcement.", |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py` | line 91: "human_summary", |
| MANUAL_REVIEW | P1 | OFFICIO_AGENTIS | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py` | line 91: "human_summary", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_AGENT_COMMON/SHELL/organ_shell_v0_1.py` | line 30: "identity": {"description": "Show organ identity summary", "action_type": "read_only"}, |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/ORGAN_AGENT_COMMON/SHELL/organ_shell_v0_1.py` | line 30: "identity": {"description": "Show organ identity summary", "action_type": "read_only"}, |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/TOOLS/build_organ_dialogue_demo_v0_1.py` | line 21: "verdict": "FOUNDATION_READY", |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/TOOLS/build_organ_dialogue_demo_v0_1.py` | line 21: "verdict": "FOUNDATION_READY", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/TOOLS/smoke_organ_dialogue_demo_v0_1.py` | line 76: isinstance(run_report, dict) and run_report.get("verdict") == "PASS", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/TOOLS/validate_organ_dialogue_demo_v0_1.py` | line 42: "FINAL_RECEIPT.json", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260519-ORGAN-AGENT-IDENTITY-HALF-RICH-SHELL-8-ORGANS-V0_1/run_eight_organ_sweep.py` | line 17: TASK_RECEIPT = TASK_REPORT_DIR / f"{TASK_ID}_RECEIPT.json" |
| MANUAL_REVIEW | P2 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5/TASKPACK_SOURCE/TEMPLATES/FINAL_RECEIPT.template.json` | line 3: "verdict": "PASS/WARN/BLOCK", |
| MANUAL_REVIEW | P1 | MECHANICUS | head | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5/sse_proof_check.py` | line 104: "stdout_summary": trim_text(details.get("stdout_summary")), |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-SANCTUM-MINI-ACTIONS-VISUAL-POLISH-PC-V0_2/DASHBOARD_APP_CAPTURE.js` | line 10: tabReceipts: "Receipts", |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R/OWNER_API_CHECKS_INGEST/api_zip_extracted/api/actions.py` | line 294: "stdout_summary": "", |
| MANUAL_REVIEW | P1 | MECHANICUS | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R/OWNER_API_CHECKS_INGEST/api_zip_extracted/api/mechanicus_adapter.py` | line 84: receipt_paths: list[Path] = [] |
| MANUAL_REVIEW | P1 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R/OWNER_API_CHECKS_INGEST/api_zip_extracted/api/state_builder.py` | line 341: verdict = "PASS" |
| MANUAL_REVIEW | P1 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R/OWNER_API_CHECKS_INGEST/api_zip_extracted/api/state_builder.py` | line 341: verdict = "PASS" |
| MANUAL_REVIEW | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/EVIDENCE/TASKPACK_DOSSIER/00_START_MESSAGE_FOR_SERVITOR.txt` | line 7: I will preserve reusable backend/action seeds, remove or quarantine runtime/generated dirt, add cleanup reports/gates, run checks, commit, push, and return a... |
| MANUAL_REVIEW | P2 | UNKNOWN | PASS | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/EVIDENCE/TASKPACK_DOSSIER/ACCEPTANCE_GATES.md` | no_signal_line_found |
| MANUAL_REVIEW | P2 | UNKNOWN | head | `IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/EVIDENCE/TASKPACK_DOSSIER/ACCEPTANCE_GATES.md` | no_signal_line_found |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164153-3b09c5/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164153-3b09c5/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164200-20ad07/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164200-20ad07/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164612-079fbf/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164612-079fbf/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164612-1f51c2/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164612-1f51c2/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164627-4b6060/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-164627-4b6060/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-170150-55de86/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-170150-55de86/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-175436-869c68/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-175436-869c68/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-175439-067f92/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | head | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-175439-067f92/reports/dossier_verify_extract/verify_ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/MANIFEST.json` | line 11: "verdict": "PASS", |
| MANUAL_REVIEW | P2 | ADMINISTRATUM | PASS | `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-175912-45cadd/reports/dossier_verify_extract/verify_tampered_dossier/MANIFEST.json` | line 11: "verdict": "PASS", |
