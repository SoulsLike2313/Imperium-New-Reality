# Root and Scope Policy

Active root:

`E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`

Ancient Empire root:

`E:/IMPERIUM`

Ancient Empire status:

`READ_ONLY_ARCHAEOLOGY`

Default access:

- New Reality: read/write allowed within task scope.
- Ancient Empire: no access unless task explicitly admits read-only reference.
- External roots: forbidden unless task explicitly admits them.

No permanent deletion is allowed in this task.

Quarantine moves must preserve:

- source path
- target path
- SHA256
- reason
- restore instruction
- classification

Do not mutate Ancient Empire.

Do not move active organ contracts, schemas, validators, task registry, current expected task, report bundles, or root manifests unless the task explicitly justifies and validates the move.
