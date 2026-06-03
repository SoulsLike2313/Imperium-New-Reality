# ARSENAL INTAKE PROTOCOL V0.1

## Intake Flow
1. Register capability as a card in `CATEGORIES/<CATEGORY>/`.
2. Assign initial status:
- `CANDIDATE` for unknown/unverified tools or practices;
- `SANDBOX` for locally testable bounded capability;
- `CANON` only with evidence/receipt;
- `QUARANTINE` for unsafe or unclear assets;
- `REJECTED` for denied capability.
3. Link source and trust/license note.
4. Define validation commands and expected receipts.
5. Add card reference into `REGISTRY/arsenal_registry_v0_1.json`.
6. If pending validation, add item into `REGISTRY/intake_queue_v0_1.json`.

## Validation Discipline
1. Run `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_foundation_v0_1.py`.
2. Ensure all cards pass required-field and category checks.
3. Ensure no `CANON` card is missing evidence path.
4. Ensure no runtime/generated junk is committed under Arsenal foundation paths.

## Non-Goals For Foundation V0.1
1. Mass installation of external tools.
2. Network provisioning.
3. Runtime cockpit/UI rebuild.
4. Claiming production readiness for non-validated external stacks.
