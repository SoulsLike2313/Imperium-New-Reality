# Owner Discussion Integration Notes

Record these decisions during the task.

## Astronomicon launcher decision

A stable VM3 taskpack launcher is required.

Ownership:

- Astronomicon owns taskpack intake, TASK_ID resolver, current expected task, registered task path, route manifest, and launch-card contract.
- IDE may call the launcher later as an action, but IDE must not become the truth source.
- Mechanicus validates scripts and compatibility.
- Inquisition checks for bypass and fake-green behavior.
- Administratum stores receipts and launch history.

Future task candidate:

`TASK-NEWGEN-ASTRONOMICON-VM3-TASKPACK-LAUNCHER-AND-IDE-HANDOFF-BRIDGE-V0_1`

Expected operator command shape:

`./imperium_vm3_launch_taskpack.ps1 -Zip <zip> -TaskId <task_id>`

## Administratum continuity launcher decision

A stable continuity pack builder is also required for new Logos-Prime handoff.

Ownership:

- Administratum owns continuity pack collection, current truth, chronicle, addresses, task history, receipts, and handoff bundles.
- Officio Agentis owns Logos-Prime role-entry and Owner-facing language contract.
- Inquisition audits stale context, fake continuity, and private-data leak risk.
- Mechanicus validates hashes and scripts.
- Astronomicon contributes current task registry and next-task route.
- IDE may expose a button later, but IDE must not become the truth source.

Future task candidate:

`TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-PACK-LAUNCHER-AND-LOGOS-HANDOFF-BRIDGE-V0_1`

Expected operator command shape:

`./imperium_build_continuity_pack.ps1 -Mode LogosPrimeHandoff -IncludeLatestTask -OpenFolder`
