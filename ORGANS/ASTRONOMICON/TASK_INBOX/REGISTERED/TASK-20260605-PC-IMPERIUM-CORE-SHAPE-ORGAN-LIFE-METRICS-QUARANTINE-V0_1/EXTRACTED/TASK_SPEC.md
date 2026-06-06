# TASK SPEC

Task ID: `TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1`

## Mission

Create the first strict Imperium core governance foundation for repository shape, 9 organ life zones, support classification, quarantine ban, machine-readable metrics, matrices, and core self-validation.

This task is executed on the PC contour.

The goal is not to physically migrate the whole repository. The goal is to give Imperium machine-checkable authority over repository shape before any large cleanup happens.

## Strategic doctrine

The repository must become a machine-checkable organism, not a pile of useful files.

Every active core artifact must be classified as one of:

1. Owned by exactly one of the 9 organs.
2. Common support that serves organs but is not itself an organ.
3. Questionable or quarantine material, banned from active use until admitted by explicit salvage receipt.

## Required 9 organs

- ADMINISTRATUM
- ASTRONOMICON
- CUSTODES
- DOCTRINARIUM
- INQUISITION
- MECHANICUS
- OFFICIO_AGENTIS
- SCHOLA_IMPERIALIS
- STRATEGIUM

Throne is not part of this 9-organ core. Throne remains protected future laptop-only scope.

## Target repository shape model

The target model is:

```text
ORGANS/
  _CORE_GOVERNANCE/
  ADMINISTRATUM/
  ASTRONOMICON/
  CUSTODES/
  DOCTRINARIUM/
  INQUISITION/
  MECHANICUS/
  OFFICIO_AGENTIS/
  SCHOLA_IMPERIALIS/
  STRATEGIUM/

SUPPORT/
  COMMON_IMPERIUM_SUPPORT/
  QUESTIONABLE_OR_QUARANTINE/
```

This task may create the governance and support structure, but must not mass-move existing files. Migration must be dry-run only.

## Organ life zone model

Each organ must have or be mapped toward a single life zone containing its identity, memory, rules, metrics, matrices, schemas, templates, validators, receipts, post-work behavior, learning hooks, and self-checks.

Create reusable contracts, schemas, and templates that define this zone.

## Required work zones

Create or update only relevant zones:

```text
ORGANS/_CORE_GOVERNANCE/
ORGANS/_CORE_GOVERNANCE/SCHEMAS/
ORGANS/_CORE_GOVERNANCE/TEMPLATES/
ORGANS/_CORE_GOVERNANCE/TOOLS/
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/
ORGANS/STRATEGIUM/METRICS/
ORGANS/SCHOLA_IMPERIALIS/LEARNING/
ORGANS/INQUISITION/QUARANTINE_POLICY/
ORGANS/CUSTODES/ORGAN_LIFE_AUDIT/
SUPPORT/COMMON_IMPERIUM_SUPPORT/
SUPPORT/QUESTIONABLE_OR_QUARANTINE/
REPORTS/TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1/
```

## Required artifacts

### Core governance

```text
ORGANS/_CORE_GOVERNANCE/CORE_SHAPE_CONTRACT_V0_1.md
ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json
ORGANS/_CORE_GOVERNANCE/ORGAN_LIFE_ZONE_CONTRACT_V0_1.md
ORGANS/_CORE_GOVERNANCE/SUPPORT_ZONE_CONTRACT_V0_1.md
ORGANS/_CORE_GOVERNANCE/QUARANTINE_USE_BAN_CONTRACT_V0_1.md
ORGANS/_CORE_GOVERNANCE/CORE_SELF_VALIDATION_CONTRACT_V0_1.md
```

### Schemas

```text
ORGANS/_CORE_GOVERNANCE/SCHEMAS/organ_card.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/organ_life_receipt.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/support_classification.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/quarantine_item.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/core_file_ownership_entry.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/core_self_validation_report.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/organ_metric.schema.json
ORGANS/_CORE_GOVERNANCE/SCHEMAS/organ_matrix.schema.json
```

### Templates

```text
ORGANS/_CORE_GOVERNANCE/TEMPLATES/ORGAN_CARD_TEMPLATE.json
ORGANS/_CORE_GOVERNANCE/TEMPLATES/ORGAN_LIFE_RECEIPT_TEMPLATE.json
ORGANS/_CORE_GOVERNANCE/TEMPLATES/SUPPORT_CLASSIFICATION_TEMPLATE.json
ORGANS/_CORE_GOVERNANCE/TEMPLATES/QUARANTINE_ITEM_TEMPLATE.json
ORGANS/_CORE_GOVERNANCE/TEMPLATES/CORE_ALERT_TEMPLATE.json
```

### Tools

```text
ORGANS/_CORE_GOVERNANCE/TOOLS/core_shape_self_checker_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/core_file_classifier_dry_run_v0_1.py
ORGANS/_CORE_GOVERNANCE/TOOLS/organ_life_validator_v0_1.py
```

The tools must be lightweight, script-first, and runnable on PC without network access.

### Administratum address book

```text
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/CORE_ADDRESS_BOOK_CONTRACT_V0_1.md
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/core_address_book_seed.json
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/file_ownership_map_seed.json
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/support_zone_map_seed.json
ORGANS/ADMINISTRATUM/ADDRESS_BOOK/unclassified_files_report.json
```

### Metrics and matrices

```text
ORGANS/STRATEGIUM/METRICS/IMPERIUM_METRICS_REGISTRY_V0_1.md
ORGANS/STRATEGIUM/METRICS/organ_self_sufficiency_metric.json
ORGANS/STRATEGIUM/METRICS/context_locality_metric.json
ORGANS/STRATEGIUM/METRICS/script_first_ratio_metric.json
ORGANS/STRATEGIUM/METRICS/servitor_load_reduction_metric.json
ORGANS/STRATEGIUM/METRICS/quarantine_pressure_metric.json
ORGANS/STRATEGIUM/METRICS/learning_capture_rate_metric.json
ORGANS/STRATEGIUM/METRICS/known_alert_prevention_metric.json
```

### Aggressive organ learning

```text
ORGANS/SCHOLA_IMPERIALIS/LEARNING/AGGRESSIVE_ORGAN_LEARNING_CONTRACT_V0_1.md
ORGANS/SCHOLA_IMPERIALIS/LEARNING/known_alert_to_preventive_rule_matrix.json
ORGANS/SCHOLA_IMPERIALIS/LEARNING/schola_learning_capture_validator_v0_1.py
```

### Inquisition quarantine policy

```text
ORGANS/INQUISITION/QUARANTINE_POLICY/ACTIVE_USE_OF_QUARANTINE_BAN_V0_1.md
ORGANS/INQUISITION/QUARANTINE_POLICY/quarantine_violation_matrix.json
ORGANS/INQUISITION/QUARANTINE_POLICY/unowned_file_alert_matrix.json
```

### Custodes organ life audit

```text
ORGANS/CUSTODES/ORGAN_LIFE_AUDIT/ORGAN_LIFE_AUDIT_CONTRACT_V0_1.md
ORGANS/CUSTODES/ORGAN_LIFE_AUDIT/custodes_organ_life_audit_matrix.json
```

### Support zones

```text
SUPPORT/COMMON_IMPERIUM_SUPPORT/README.md
SUPPORT/COMMON_IMPERIUM_SUPPORT/SUPPORT_ADDRESS_POLICY.md
SUPPORT/QUESTIONABLE_OR_QUARANTINE/README.md
SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_POLICY.md
SUPPORT/QUESTIONABLE_OR_QUARANTINE/QUARANTINE_INDEX.json
```

## Tool behavior requirements

`core_shape_self_checker_v0_1.py` must inspect the current repo and output a JSON report with:

- exact 9 organ existence status;
- support zone existence status;
- quarantine zone existence status;
- unexpected top-level or governance-relevant folders;
- unclassified or questionable candidates, if reasonably detectable;
- organ life minimum-field checks;
- alerts;
- verdict: PASS, PASS_WITH_WARNINGS, or BLOCK.

`core_file_classifier_dry_run_v0_1.py` must not move or delete files. It must only produce a dry-run classification report.

`organ_life_validator_v0_1.py` must validate organ life zones against the V0.1 contract and schema expectations.

## Enhanced Ghost Evolve

Mode: ULTIMATE_ORGAN_TEACHING_ARCHITECTURE_FIRST.

The Servitor must convert manual architectural intent into durable organ knowledge:

- contracts;
- matrices;
- schemas;
- templates;
- validators;
- receipts;
- alerts;
- metrics;
- address book seed;
- next migration route.

Any repeated manual intervention pattern must become a Schola lesson candidate or preventive rule.

## Servitor boundaries

The Servitor may draft, implement, validate, and report.

The Servitor must not:

- mass move the repository;
- delete legacy material;
- claim full cleanup;
- claim full semantic core validation;
- use quarantine as active source;
- implement Throne;
- overwrite active organ authority.

## Closure

Close through current post-work bundle V0.2 standards. Commit and normal non-force push are required if accepted changes are produced.

Final owner-facing summary must be Russian through OFFICIO authority. Machine artifacts must be English UTF8 NO_BOM.
