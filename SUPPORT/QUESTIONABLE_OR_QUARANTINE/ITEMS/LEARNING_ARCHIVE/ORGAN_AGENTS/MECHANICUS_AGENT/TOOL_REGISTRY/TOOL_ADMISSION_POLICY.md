# TOOL ADMISSION POLICY

## Core rules

- No random installs.
- No package manager installs without explicit Owner gate.
- Availability must be evidenced by command output and receipts.
- Missing tool is WARN/KNOWN_NOT_INSTALLED, not automatic blocker.
- Security tools report only; no auto-delete or destructive cleanup.

## Admission flow

1. Read candidate list and owner/consumer scope.
2. Probe VM2 with safe read-only version commands.
3. Consume PC snapshot if supplied through Administratum intake.
4. Assign status per tool: pc_status, vm2_status, combined_status.
5. Write tool card and index entries.
6. Run registry validation check before commit.

## Install proposal flow

If installation is needed, produce recommendation only:

- why installation is needed;
- owner organ and consumer organs;
- install command proposal (not executed);
- evidence required after install;
- rollback/disable note.
