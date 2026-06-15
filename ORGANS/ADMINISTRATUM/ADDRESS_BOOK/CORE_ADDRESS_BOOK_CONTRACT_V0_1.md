# Core Address Book Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: ADMINISTRATUM

## Purpose

The core address book maps repository paths to one required organ, common support, or quarantine/questionable status before any physical cleanup.

## Rules

- One active core path has exactly one owner organ unless classified as common support.
- Common support must list supported organs and allowed use.
- Unknown paths must use UNKNOWN_WITH_REASON and remain dry-run migration candidates.
- Quarantine or questionable paths must not be used as active source without explicit salvage/admission receipt.

## Boundary

This V0.1 address book is a seed. It does not physically migrate files and does not claim complete classification of the repository.
