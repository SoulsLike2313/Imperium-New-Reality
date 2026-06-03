GATE_ACK:
- task_id: TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1
- current_head: b373f45bee437a8b67fd0996dc76c2ac94afe75e
- gatepack_path: C:\Users\PC\Downloads\TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1_DOSSIER.zip
- gatepack_sha256: 649a8b401f57081de13fc80864d3ee70d50a1fdff8634a278a4d9019e01503ce
- read_gates: [GATE-U00-GIT-TRUTH, GATE-U01-ROLE-ACK, GATE-U02-SCOPE-BOUNDARY, GATE-U04-EVIDENCE-RECEIPT, GATE-U05-STOP-CONDITIONS, GATE-U08-REPO-PURITY, GATE-U09-NO-FAKE-GREEN, GATE-U12-REPORT-OUTPUT-BUDGET, GATE-U13-PYTHON-TYPE-SAFETY, GATE-U14-WHOLE-REPO-SCOPE-RECON, GATE-U15-OPERATIONALITY-IMPACT, GATE-U16-BILINGUAL-UI, GATE-U17-DELIVERABLE-PACKAGE, GATE-U18-AGENT-FACTORY-COMPLIANCE, GATE-U19-SCRIPT-ARTIFACT-PRESERVATION, GATE-U20-AGENT-KPD-SELF-REVIEW, GATE-U21-COMMAND-CHUNKING, GATE-AI00-NO-DIRECT-MODEL-COMMAND]
- accepted_stop_conditions:
  - repo root mismatch
  - branch or starting head mismatch
  - unrelated dirty worktree before admission
  - missing mandatory Officio/Mechanicus/NewGen task inputs
  - required forbidden action needed (install/visual prototype/LLM-cloud/network)
  - forbidden path appears in diff
  - private/local external context would be indexed
  - fake-green risk (evidence missing for PASS claim)
  - report budget avalanche risk without owner gate
  - sqlite/fts unavailable or database cannot be created
- scope_boundary: "Build bounded NewGen-only Mechanicus evidence index foundation (SQLite/FTS + reports + handoff)"
- touched_paths:
  - IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1/*
  - IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py
  - IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_query_runner_v0_1.py
  - IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py
  - IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1/*
- forbidden_paths:
  - ORGANS/**
  - IMPERIUM_TEST_VERSION/**
  - IMPERIUM_NEW_GENERATION/SANCTUM_NG/**
  - private/local external context paths (e.g., E:\IMPERIUM_CONTEXT\**, C:\Users\PC\**)
  - runtime/source corridors outside declared NewGen Mechanicus evidence-index scope
- expected_receipts:
  - FINAL_REPORT.md
  - GATE_ACK.md
  - evidence_index_build_report.json
  - evidence_index_coverage_report.json
  - evidence_query_smoke_report.json
  - warning_error_pattern_seed_report.json
  - task_commit_linkage_seed_report.json
  - inquisition_evidence_safety_report.json
  - administratum_evidence_index_handoff.json
  - ghost_evolve_evidence_index_training_proof.json
  - quality_gate_result_report.json
  - closure_receipt.json
- repo_recon_required: true
- script_absorption_required: true
- clarification_needed: "none"
- verdict: PASS

OFFICIO_GATE_BLOCK:
ROLE_ACK: PC_SERVITOR accepted
LANGUAGE_ACK: owner-facing Russian accepted
SCOPE_ACK: allowed paths bounded to NewGen Mechanicus evidence index/task report roots; forbidden paths acknowledged
STOP_CONDITIONS_ACK: accepted
FORBIDDEN_ACTIONS_ACK: accepted (no install, no UI/visual prototypes, no LLM/cloud activation, no broad cleanup)
