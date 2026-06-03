# Tool State Protocol Draft

## Purpose

Track tools without confusing advisory reference, installed tool, verified tool, and canon capability.

## Required states

- `REFERENCE_ONLY`
- `CONSIDERED`
- `INSTALLED_SANDBOX`
- `VERIFIED_SANDBOX`
- `APPROVED_CANON`
- `REJECTED`
- `DEPRECATED`

## Rules

- Advisory mention is not installation.
- Installed is not verified.
- Verified is not canon.
- Canon requires Owner approval and receipts.
