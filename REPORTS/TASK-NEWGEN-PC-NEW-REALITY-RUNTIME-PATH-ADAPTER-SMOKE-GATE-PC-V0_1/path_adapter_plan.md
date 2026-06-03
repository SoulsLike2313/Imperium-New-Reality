# Path Adapter Plan

Task ID: $TaskId

## Current Root Truth

- Active root: E:/IMPERIUM_NEW_GENERATION_NEW_REALITY
- Ancient reference root: E:/IMPERIUM (read-only reference)
- Generic IMPERIUM_NEW_GENERATION text is not automatically external because it is part of the New Reality root name and internal history.

## Scan Result

- Direct external path matches: 2135
- Runtime-critical script/tool candidates: 15
- Machine config/registry candidates: 47
- Historical/doc references: 38
- Historical/report references: 310
- Taskpack/route history references: 0

## First Adapter Boundary

Patch only runtime script/tool defaults that point to E:/IMPERIUM, E:\IMPERIUM, E:/IMPERIUM_CONTEXT, or E:\IMPERIUM_CONTEXT.
Reports, old taskpacks, receipt transcripts, and archaeology records stay unchanged unless a future task explicitly authorizes historical migration.

## Runtime Candidates

- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_
- $_

## Adapter Rule

1. Resolve New Reality root from $env:IMPERIUM_NEW_REALITY_ROOT when set.
2. Otherwise resolve via git rev-parse --show-toplevel from the script location or current directory.
3. Accept explicit --repo-root / -RepoRoot override only if the resolved path stays under E:/IMPERIUM_NEW_GENERATION_NEW_REALITY.
4. Treat Ancient Empire as read-only salvage source requiring SALVAGE_REQUEST.
