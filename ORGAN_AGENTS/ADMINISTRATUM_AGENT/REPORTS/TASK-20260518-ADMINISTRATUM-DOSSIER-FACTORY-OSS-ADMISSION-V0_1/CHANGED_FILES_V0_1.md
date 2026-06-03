# Changed Files V0.1

## Scope classification
- `in_scope_source`: Administratum source/contracts/schemas/registry/tooling.
- `in_scope_reports`: Current task report folder.
- `in_scope_receipt`: Current task receipt.
- `runtime_only`: RUNS artifacts only, not committed.
- `preexisting_dirty`: Present before this task continuation; not reverted.

## Files changed or created
| Path | Action | Scope class | Notes |
|---|---|---|---|
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_dossier_factory.py` | add | in_scope_source | Dossier builder, verifier, OSS detect, owner PDF render. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py` | modify | in_scope_source | Added `doctor-oss`, `build-dossier`, `verify-dossier`. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/CONTRACTS/ADMINISTRATUM_DOSSIER_FACTORY_CONTRACT_V0_1.md` | add | in_scope_source | Dossier ZIP contract. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/CONTRACTS/ADMINISTRATUM_OWNER_PDF_REPORT_CONTRACT_V0_1.md` | add | in_scope_source | Owner RU PDF contract. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/CONTRACTS/ADMINISTRATUM_EVIDENCE_CAPTURE_CONTRACT_V0_1.md` | add | in_scope_source | Evidence capture safety and structure. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/CONTRACTS/ADMINISTRATUM_OSS_ADMISSION_CONTRACT_V0_1.md` | add | in_scope_source | OSS admission lifecycle rules. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/CONTRACTS/ADMINISTRATUM_BIG_OUTPUT_PACKAGING_CONTRACT_V0_1.md` | add | in_scope_source | Packaging rules for large outputs. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/SCHEMAS/ADMINISTRATUM_DOSSIER_MANIFEST_SCHEMA_V0_1.json` | add | in_scope_source | Dossier manifest schema. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/SCHEMAS/ADMINISTRATUM_OSS_TOOL_RECORD_SCHEMA_V0_1.json` | add | in_scope_source | OSS registry record schema. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/SCHEMAS/ADMINISTRATUM_EVIDENCE_INDEX_SCHEMA_V0_1.json` | add | in_scope_source | Evidence index schema. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/OSS_ADMISSION/OSS_ADMISSION_REGISTER_V0_1.json` | add | in_scope_source | Tool status matrix with fallback/risk. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/OSS_ADMISSION/OSS_CANDIDATE_MATRIX_V0_1.md` | add | in_scope_source | Human-readable candidate matrix. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/OSS_ADMISSION/OSS_ADMISSION_POLICY_V0_1.md` | add | in_scope_source | Admission policy and workflow. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/REPORTS/TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1/*` | add | in_scope_reports | Task reports. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/receipts/TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1_RECEIPT_V0_1.json` | add | in_scope_receipt | Task receipt. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py` | unchanged in this slice | preexisting_dirty | Existing local dirty state remained by Owner authorization. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/REPORTS/TASK-20260518-ADMINISTRATUM-OPERATOR-CONTRACT-TRUST-CAPSULE-V0_1/*` | unchanged in this slice | preexisting_dirty | Existing uncommitted prior task artifacts remained. |
| `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/receipts/TASK-20260518-ADMINISTRATUM-OPERATOR-CONTRACT-TRUST-CAPSULE-V0_1_RECEIPT_V0_1.json` | unchanged in this slice | preexisting_dirty | Existing uncommitted prior task artifact remained. |

