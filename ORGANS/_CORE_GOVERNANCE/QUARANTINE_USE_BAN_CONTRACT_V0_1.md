# Quarantine Use Ban Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: INQUISITION

## Rule

No active workflow may depend on files inside SUPPORT/QUESTIONABLE_OR_QUARANTINE/ unless an explicit salvage or admission receipt exists and is referenced by the workflow.

## Violation Classes

- ACTIVE_SOURCE_USE_WITHOUT_RECEIPT
- QUARANTINE_AS_TRUTH
- SILENT_QUARANTINE_IMPORT
- UNOWNED_FILE_PROMOTED_TO_ACTIVE_USE

## Required Response

Any violation must be recorded in an Inquisition receipt and treated as BLOCK until repaired or explicitly admitted.
