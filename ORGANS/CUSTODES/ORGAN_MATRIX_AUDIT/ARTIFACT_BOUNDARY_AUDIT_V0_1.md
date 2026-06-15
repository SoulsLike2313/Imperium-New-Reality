# CUSTODES - Artifact Boundary Audit (CANDIDATE_V0_1)

Status: CANDIDATE_NOT_CANON
Destination: ORGANS/CUSTODES/ORGAN_MATRIX_AUDIT/ARTIFACT_BOUNDARY_AUDIT_V0_1.md

Custodes audits the BOUNDARY between source and payload. Custodes does not claim full Throne
authority or full semantic truth; it audits receipt quality and matrix compliance.

## Audit checklist

- [ ] No build artifacts (target/, node_modules, caches, *.rlib/*.pdb/*.dll/*.exe) tracked in source.
- [ ] No unadmitted zip outside FIXTURES/.
- [ ] No duplicate root mirrors (LEGACY_IMPORTED_ROOT_MIRROR) carrying a second copy of the body.
- [ ] Hygiene gate report and git-truth receipt are both present and schema-valid.
- [ ] STRATEGIUM cleanliness metric is recursive (v0.2), not root-only.
- [ ] PASS_WITH_WARNINGS is not summarized to the owner as a clean PASS.

## Audit verdict semantics

Custodes emits AUDIT_PASS / AUDIT_WARN / AUDIT_BLOCK on receipt and matrix quality only.
Any missing receipt is AUDIT_BLOCK. Custodes never invents authority it does not have.
