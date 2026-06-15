# Dual Patch Rule V0.1

Every future implementation patch should carry a Mechanicus/Data Atlas layer.

## Required fields in future patch manifests

- product_change
- mechanicus_change
- data_atlas_change
- languages_used
- tools_registered
- validation_commands
- owner_visible_effect
- source_repo_writes
- evidence_outputs

## Minimal compliance

A patch is acceptable if it either:

1. adds/updates a tool passport, or
2. explains why no new tool/language/passport is required.

## Forbidden pattern

A patch must not introduce a new script/tool/language silently.
