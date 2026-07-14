# IMPERIUM_PHASE2_WINDOWS_PROCESS_PROBE_HARDENING_0001

Fixes the localized Windows `tasklist` decode failure exposed when the parent Python process runs in UTF-8 mode.

The observer now treats `tasklist` output as bytes and searches only for the ASCII PID token. It does not weaken the pinned-toolchain bridge, restore PATH, or change production execution routing.
