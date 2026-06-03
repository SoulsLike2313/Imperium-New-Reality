# Task Specification

## Task ID

`TASK-NEWGEN-PC-NEW-REALITY-SELF-FIX-CLEAN-DEV-ENV-SERVITOR-CONTROL-MECHANICUS-SKILL-ARSENAL-AND-REPO-STERILIZATION-PC-V0_1`

## Purpose

Perform a large but controlled self-fix pass inside New Reality.

The goal is to make New Reality more reliable, sterile, measurable, and organ-operational before VM2/VM3 sync, Throne adaptation, Codex CLI bridge, or broad Mechanicus expansion.

This task must improve:

1. New Reality development environment cleanliness.
2. Repository classification and quarantine discipline.
3. Agent-side control over any Servitor model.
4. Evidence bundle and final closure proof discipline.
5. Mechanicus Skill/API/tool candidate storage.
6. Inquisition and Speculum reinforcement feedback loop.
7. Root/scope safety and Ancient Empire isolation.
8. Remote/tree/bundle validation reliability.

## Background

Recent reviews found that New Reality is operational and remote-proven, but still needs stronger evidence packaging, reusable closure gates, agent-side Servitor control, and repository sterilization.

Known issues to address:

- Some final closure evidence may be adjacent to bundles instead of included in a replayable index.
- Owner-facing runtime language drift was visible and not enforced by organ-side control.
- New Reality needs a clean active root and quarantine discipline.
- Mechanicus skill/tool/API candidate storage needs a first structured form.
- Inquisition and Speculum should generate three reinforcement proposals after reviews.
- No uncontrolled broad rewrite or external install spree is allowed.
- Ancient Empire must stay read-only archaeology unless explicit salvage admission exists.

## Required Stages

### Stage 0: Preflight and evidence boundary

- Resolve New Reality root through the existing root resolver.
- Verify remote URL, branch, HEAD, and clean/dirty state.
- Verify Ancient Empire is not active runtime.
- Read recent report/review context from New Reality reports if available.
- Record `preflight_truth_receipt.json`.

### Stage 1: Repo inventory and classification

Scan New Reality and classify files into:

- `ACTIVE_CORE`
- `ACTIVE_REPORTS`
- `CANDIDATE_REVIEW`
- `QUARANTINE`
- `DO_NOT_TOUCH`

Do not delete anything.

Produce:

- `repo_inventory.json`
- `classification_decision_ledger.json`
- `active_core_manifest.json`
- `active_reports_manifest.json`
- `candidate_review_manifest.json`
- `do_not_touch_manifest.json`

### Stage 2: Quarantine sterile cleanup

Move clearly stale/generated/runtime/duplicate/non-active files out of active paths into a quarantine location inside New Reality, preserving hashes and restore paths.

Default quarantine root:

`QUARANTINE/REPO_STERILIZATION/<TASK_ID>/`

Produce:

- `quarantine_manifest.json`
- `moved_files_receipt.json`
- `restore_instructions.md`

Only move files that are safe by evidence. If uncertain, classify as `CANDIDATE_REVIEW`, not quarantine.

### Stage 3: Servitor control chain

Create or strengthen a model-agnostic Servitor control chain.

This must apply to Codex, Claude, local LLM, or any future Servitor.

Organs must control Servitor behavior; Owner must not be the runtime correction layer.

Create:

- `ORGANS/OFFICIO_AGENTIS/CONTRACTS/servitor_runtime_control_contract_v0_1.md`
- `ORGANS/ASTRONOMICON/CONTRACTS/launch_context_injection_contract_v0_1.md`
- `ORGANS/INQUISITION/MATRICES/servitor_compliance_matrix_v0_1.json`
- `SCHEMAS/servitor_control_chain_receipt.schema.json`
- a sample `servitor_control_chain_receipt.json` in this task report.

The receipt must disclose if any behavior correction came from Owner manual intervention instead of organ-side control.

### Stage 4: Mechanicus Skill/API/tool arsenal storage

Create or strengthen Mechanicus candidate storage without uncontrolled installs.

Create:

- `ORGANS/MECHANICUS/ARSENAL/SKILL_CANDIDATES/`
- `ORGANS/MECHANICUS/ARSENAL/API_CANDIDATES/`
- `ORGANS/MECHANICUS/ARSENAL/TOOL_CANDIDATES/`
- `ORGANS/MECHANICUS/ARSENAL/CANONIZATION_POLICY.md`
- `SCHEMAS/mechanicus_candidate_card.schema.json`

Seed candidate cards for at least:

- Graphify
- SearXNG
- Crawl4AI
- Public APIs registry
- State-machine discipline / XState pattern study
- Wasmer sandbox candidate
- Antares / database visibility candidate

Each card must include:

- candidate id
- type
- purpose
- owner organ
- first safe use case
- risk
- install/admission mode
- receipt requirements
- canonization rule: candidate can become canon only after 10 successful cycles.

### Stage 5: Evidence bundle index and final closure packager

Implement or define a reusable evidence index / final proof packaging standard.

Create:

- `TOOLS/EVIDENCE/`
- `SCHEMAS/evidence_index.schema.json`
- `SCHEMAS/final_closure_proof_receipt.schema.json`
- `DOCS/EVIDENCE_BUNDLE_INDEX_AND_FINAL_PROOF_PACKAGER_V0_1.md`

If time allows, implement a small script:

- `TOOLS/EVIDENCE/build_evidence_index_v0_1.py`

The index must record:

- task id
- final HEAD
- remote HEAD
- bundle path
- bundle sha256
- required receipts present/missing
- self-reference limitation statement
- reviewer gaps
- next gate.

### Stage 6: Inquisition and Speculum reinforcement loop

Create the rule that every Inquisition or Speculum review must provide exactly three reinforcement proposals:

1. Skill/API/tool candidate.
2. Matrix/gate improvement.
3. Cost/context/output optimization.

Create:

- `ORGANS/INQUISITION/CONTRACTS/review_reinforcement_proposals_contract_v0_1.md`
- `ORGANS/SPECULUM/CONTRACTS/review_reinforcement_proposals_contract_v0_1.md`
- `SCHEMAS/reinforcement_proposal.schema.json`

### Stage 7: Validation and proof

Run existing New Reality validators plus any new validators created by this task.

Required checks:

- root resolution PASS
- remote URL PASS
- local HEAD equals origin/master after push
- worktree clean after final push
- Ancient Empire not mutated
- no forbidden broad deletion
- quarantine hashes valid
- report bundle exists and has SHA256
- final closure proof receipt exists
- machine artifacts have no BOM and no Cyrillic unless explicitly Officio owner-runtime localization artifact

### Stage 8: Commit, push, and final answer

Commit and push to New Reality remote.

Final answer must use required 4-part format:

1. Step name
2. Step verdict
3. Commit links / identifiers with labels
4. 3-4 concise Owner comments in Russian

Final answer must include:

- report bundle path
- bundle SHA256
- final local HEAD
- remote HEAD verification
- key caps or self-reference limit if any.
