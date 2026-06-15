# READONLY NO-DIRTY BLUEPRINT

## Rule

Read-only commands must not change tracked repository state.

## Allowed outputs

- stdout;
- ignored runtime receipt path;
- explicitly invoked smoke report path.

## Forbidden for read-only

- modifying tracked report receipts;
- rewriting committed summaries;
- changing task registries;
- staging files;
- creating untracked report artifacts.

## Required smoke

Capture git status before and after running read-only commands.
The tracked file diff must not change.
