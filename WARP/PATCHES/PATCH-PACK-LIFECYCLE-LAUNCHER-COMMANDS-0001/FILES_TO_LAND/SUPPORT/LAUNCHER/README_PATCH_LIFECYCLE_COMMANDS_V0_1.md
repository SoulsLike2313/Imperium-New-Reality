# IMPERIUM LAUNCHER PATCH LIFECYCLE COMMANDS V0.1

This layer exposes Patch Pack validation as operator commands.

Examples:

```powershell
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch preflight PATCH-ID
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch scope PATCH-ID
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch smoke PATCH-ID
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch lifecycle PATCH-ID
pwsh SUPPORT/LAUNCHER/imperium.ps1 patch lifecycle-all
```

No patch execution is implemented here.
