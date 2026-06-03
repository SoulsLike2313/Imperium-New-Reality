# Owner Decision Note

The Owner wants taskpack registration to become an Astronomicon Skill, not a fragile pasted command and not only a VM3-specific helper.

Desired operator flow:

Open Astronomicon TUI -> choose Register Taskpack -> select ZIP -> choose contour PC, VM3 or VM2 -> Astronomicon performs registration and shows launch instructions.

For VM2 and VM3 the successful registration must open a terminal on the target VM with a clear launch card and copyable `start task` message.

The future IDE may call the same Skill, but the source of truth remains Astronomicon.
