# Astronomicon PC Launch

Status: `CANON_ACTIVE_PC_LAUNCH_NOTE`
Task: `TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1`

Use this note when a local operator or IDE panel needs a stable PC entrypoint.

## Commands

From the repository root:

```powershell
python ORGANS\ASTRONOMICON\SKILLS\TASKPACK_REGISTRATION_SKILL\astronomicon_taskpack_registration_skill_v0_1.py --discovery-smoke
```

From any working directory inside the repository:

```powershell
powershell -ExecutionPolicy Bypass -File ORGANS\ASTRONOMICON\run_astronomicon_pc.ps1 --discovery-smoke
```

The launcher resolves the repository root before invoking the registration skill. PC discovery must not require VM2, VM3, or remote contour routing.
