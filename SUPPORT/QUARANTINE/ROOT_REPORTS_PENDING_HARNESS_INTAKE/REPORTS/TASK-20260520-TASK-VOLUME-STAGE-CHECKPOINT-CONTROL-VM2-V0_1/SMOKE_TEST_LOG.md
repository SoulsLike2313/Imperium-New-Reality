# Smoke Test Log

- task_id: TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1
- generated_at_utc: 2026-05-19T23:55:06.661645Z
- verdict: PASS

## classify_small
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py classify --task-contract /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/fixture_small_task_contract.json --out /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_TASK_VOLUME_SMALL.json
- stdout:
```text
{
  "schema_version": "TASK_VOLUME_CONTROL_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.036480Z",
  "task_id": "TASK-EXAMPLE-SMALL-V0_1",
  "task_size_class": "SMALL",
  "context_budget_class": "LOW",
  "organ_count": 1,
  "expected_file_touch_class": "FILES_1_10",
  "expected_command_count_class": "CMDS_1_20",
  "expected_evidence_volume_class": "EVIDENCE_LOW",
  "accuracy_risk": "LOW",
  "checkpoint_required": false,
  "checkpoint_cadence": "END_ONLY",
  "split_required_if": [
    "scope spans 3 or more organs",
    "required checks exceed 5 commands",
    "evidence references exceed one report package"
  ],
  "continuation_protocol_required": false,
  "recommended_execution_phases": [
    {
      "phase_id": "S1",
      "phase_name": "single_pass",
      "goal": "bounded execution and report",
      "checkpoint_gate": true
    }
  ],
  "classification_trace": {
    "scope_count": 1,
    "required_checks_count": 1,
    "organs_detected": [],
    "source_schema_version": "TASK_CONTRACT_V0_1"
  }
}
```

## classify_large
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py classify --task-contract /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/fixture_large_task_contract.json --out /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_TASK_VOLUME_LARGE.json
- stdout:
```text
{
  "schema_version": "TASK_VOLUME_CONTROL_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.109182Z",
  "task_id": "TASK-EXAMPLE-LARGE-V0_1",
  "task_size_class": "LARGE",
  "context_budget_class": "HIGH",
  "organ_count": 3,
  "expected_file_touch_class": "FILES_30_80",
  "expected_command_count_class": "CMDS_60_140",
  "expected_evidence_volume_class": "EVIDENCE_HIGH",
  "accuracy_risk": "HIGH",
  "checkpoint_required": true,
  "checkpoint_cadence": "PER_STAGE",
  "split_required_if": [
    "scope spans 3 or more organs",
    "required checks exceed 5 commands",
    "evidence references exceed one report package"
  ],
  "continuation_protocol_required": true,
  "recommended_execution_phases": [
    {
      "phase_id": "S1",
      "phase_name": "design",
      "goal": "schemas and control model",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S2",
      "phase_name": "implementation",
      "goal": "bounded implementation",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S3",
      "phase_name": "validation",
      "goal": "smoke and evidence checks",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S4",
      "phase_name": "closure",
      "goal": "reports and commit",
      "checkpoint_gate": true
    }
  ],
  "classification_trace": {
    "scope_count": 6,
    "required_checks_count": 4,
    "organs_detected": [
      "ADMINISTRATUM_AGENT",
      "ASTRONOMICON_AGENT",
      "STRATEGIUM_AGENT"
    ],
    "source_schema_version": "TASK_CONTRACT_V0_1"
  }
}
```

## classify_mega
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py classify --task-contract /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/fixture_mega_task_contract.json --out /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_TASK_VOLUME_MEGA.json
- stdout:
```text
{
  "schema_version": "TASK_VOLUME_CONTROL_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.177530Z",
  "task_id": "TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1",
  "task_size_class": "MEGA",
  "context_budget_class": "EXTREME",
  "organ_count": 8,
  "expected_file_touch_class": "FILES_80_PLUS",
  "expected_command_count_class": "CMDS_140_PLUS",
  "expected_evidence_volume_class": "EVIDENCE_EXTREME",
  "accuracy_risk": "CRITICAL",
  "checkpoint_required": true,
  "checkpoint_cadence": "PER_STAGE",
  "split_required_if": [
    "scope spans 3 or more organs",
    "required checks exceed 5 commands",
    "evidence references exceed one report package",
    "mixed control/docs/cli/report planes exceed single-pass safety"
  ],
  "continuation_protocol_required": true,
  "recommended_execution_phases": [
    {
      "phase_id": "S1",
      "phase_name": "control_design",
      "goal": "task control docs and schemas",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S2",
      "phase_name": "builders",
      "goal": "CLI tools and skeleton generators",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S3",
      "phase_name": "validation",
      "goal": "compile/help/example checks",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S4",
      "phase_name": "organ_alignment",
      "goal": "responsibility alignment",
      "checkpoint_gate": true
    },
    {
      "phase_id": "S5",
      "phase_name": "report_and_release",
      "goal": "reports, receipts, commit",
      "checkpoint_gate": true
    }
  ],
  "classification_trace": {
    "scope_count": 12,
    "required_checks_count": 7,
    "organs_detected": [
      "ADMINISTRATUM_AGENT",
      "ASTRONOMICON_AGENT",
      "DOCTRINARIUM_AGENT",
      "INQUISITION_AGENT",
      "MECHANICUS_AGENT",
      "OFFICIO_AGENTIS_AGENT",
      "SCHOLA_IMPERIALIS_AGENT",
      "STRATEGIUM_AGENT"
    ],
    "source_schema_version": "TASK_CONTRACT_V0_1"
  }
}
```

## validate_task_volume_example
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py validate --input /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_TASK_VOLUME_CONTROL.json
- stdout:
```text
{
  "schema_version": "TASK_VOLUME_VALIDATION_RESULT_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.232570Z",
  "input": "/home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_TASK_VOLUME_CONTROL.json",
  "schema_path": "/home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/TASK_CONTROL/TASK_VOLUME_CONTROL.schema.json",
  "errors": [],
  "warnings": [],
  "verdict": "PASS"
}
```

## create_stage_checkpoint_example
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py create --task-id TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1 --stage-id S1_CONTROL_DESIGN --stage-name control_docs_and_schema --stage-type PLAN --checkpoint-status READY_FOR_REVIEW --evidence /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/TASK_VOLUME_STAGE_CHECKPOINT_REPORT.md --out /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_STAGE_CHECKPOINT.json
- stdout:
```text
{
  "schema_version": "STAGE_CHECKPOINT_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.362597Z",
  "task_id": "TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1",
  "stage_id": "S1_CONTROL_DESIGN",
  "stage_name": "control_docs_and_schema",
  "stage_type": "PLAN",
  "before_state": {
    "git_head": "72f94abf2b9e117f481ba0e5b86d606ada46ae79",
    "git_status_short": [
      "?? IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py",
      "?? IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py",
      "?? IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/",
      "?? IMPERIUM_NEW_GENERATION/TASK_CONTROL/"
    ],
    "notes": []
  },
  "after_state": {
    "git_head": "72f94abf2b9e117f481ba0e5b86d606ada46ae79",
    "git_status_short": [
      "?? IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py",
      "?? IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py",
      "?? IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/",
      "?? IMPERIUM_NEW_GENERATION/TASK_CONTROL/"
    ],
    "notes": []
  },
  "touched_files": [],
  "diff_summary": "No diff summary provided yet.",
  "evidence_links": [
    "/home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/TASK_VOLUME_STAGE_CHECKPOINT_REPORT.md"
  ],
  "warnings": [],
  "errors": [],
  "blockers": [],
  "organ_checks": {
    "STRATEGIUM_AGENT": "PASS",
    "ASTRONOMICON_AGENT": "PASS",
    "ADMINISTRATUM_AGENT": "PASS",
    "OFFICIO_AGENTIS_AGENT": "PASS",
    "INQUISITION_AGENT": "PASS",
    "MECHANICUS_AGENT": "PASS",
    "SCHOLA_IMPERIALIS_AGENT": "PASS",
    "DOCTRINARIUM_AGENT": "PASS"
  },
  "owner_decision_options": [
    "ACCEPT",
    "REQUEST_FIX",
    "CONTINUE_WITH_NOTES",
    "STOP",
    "SPLIT_REQUIRED"
  ],
  "owner_decision_required": true,
  "checkpoint_status": "READY_FOR_REVIEW",
  "notes": []
}
```

## validate_stage_checkpoint_example
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py validate --input /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_STAGE_CHECKPOINT.json
- stdout:
```text
{
  "schema_version": "STAGE_CHECKPOINT_VALIDATION_RESULT_V0_1",
  "generated_at_utc": "2026-05-19T23:55:06.423181Z",
  "input": "/home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_STAGE_CHECKPOINT.json",
  "errors": [],
  "warnings": [],
  "verdict": "PASS"
}
```

## report_stage_checkpoint_example
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py report --input /home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1/EXAMPLE_STAGE_CHECKPOINT.json
- stdout:
```text
STAGE CHECKPOINT REPORT
task_id: TASK-20260520-TASK-VOLUME-STAGE-CHECKPOINT-CONTROL-VM2-V0_1
stage: S1_CONTROL_DESIGN | control_docs_and_schema
stage_type: PLAN
checkpoint_status: READY_FOR_REVIEW
owner_decision_options:
- ACCEPT
- REQUEST_FIX
- CONTINUE_WITH_NOTES
- STOP
- SPLIT_REQUIRED
organ_checks:
- STRATEGIUM_AGENT: PASS
- ASTRONOMICON_AGENT: PASS
- ADMINISTRATUM_AGENT: PASS
- OFFICIO_AGENTIS_AGENT: PASS
- INQUISITION_AGENT: PASS
- MECHANICUS_AGENT: PASS
- SCHOLA_IMPERIALIS_AGENT: PASS
- DOCTRINARIUM_AGENT: PASS
```

## help_task_volume
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py --help
- stdout:
```text
usage: task_volume_check.py [-h] {classify,validate,report} ...

Task volume classifier and validator.

positional arguments:
  {classify,validate,report}
    classify            Classify task contract into task volume control
                        payload.
    validate            Validate task volume control JSON payload.
    report              Print human-readable report from task volume JSON.

options:
  -h, --help            show this help message and exit
```

## help_stage_builder
- returncode: 0
- argv: python3 IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py --help
- stdout:
```text
usage: stage_checkpoint_builder.py [-h] {create,validate,report} ...

Build and validate stage checkpoint payloads.

positional arguments:
  {create,validate,report}
    create              Create checkpoint skeleton JSON.
    validate            Validate checkpoint JSON payload.
    report              Print human-readable checkpoint report.

options:
  -h, --help            show this help message and exit
```

## py_compile
- returncode: 0
- argv: python3 -m py_compile IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/task_volume_check.py IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/stage_checkpoint_builder.py
