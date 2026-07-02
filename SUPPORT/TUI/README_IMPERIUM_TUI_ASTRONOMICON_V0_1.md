# IMPERIUM TUI — Astronomicon / Custodes / Throne Console V0.1

patch_id: `IMPERIUM-TUI-ASTRONOMICON-CUSTODES-THRONE-CONSOLE-0001`

## Purpose

Give the Owner a Russian terminal TUI for the current proven lane:

```text
Astronomicon
Custodes validation over Astronomicon
Throne Crown order over Astronomicon
```

## Aquarium law

Every callable function must show its work as terminal output.

Every action writes:

```text
SUPPORT/TUI/LOGS/<timestamp>_<action>.log
SUPPORT/TUI/RECEIPTS/<timestamp>_<action>_receipt.json
```

## Run

```powershell
pwsh SUPPORT/TUI/imperium_tui.ps1
```

Non-interactive examples:

```powershell
pwsh SUPPORT/TUI/imperium_tui.ps1 -ListActions
pwsh SUPPORT/TUI/imperium_tui.ps1 -Action status
pwsh SUPPORT/TUI/imperium_tui.ps1 -Action custodes-readout
pwsh SUPPORT/TUI/imperium_tui.ps1 -Action throne-readout
```

## Not claimed

```text
full IDE visual abstraction
visual/AAA layer resumed
Great Nine assembled
Core v1 ready
Throne self-validation
```
