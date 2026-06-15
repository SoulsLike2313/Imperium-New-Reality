# Admission contract discovery notes

During the previous launch sequence, several blocks were observed and should be preserved as successful protections:

- Missing root MANIFEST.json was blocked.
- Missing or incomplete MANIFEST.language_and_encoding_policy was blocked.
- Missing MANIFEST.organs route with all 8 organs was blocked.
- Unregistered TASK_ID resolution was blocked.
- A valid 8-organ taskpack passed admission and resolved with warnings.

This task must convert these events into regression fixtures and learning cards. Future taskpack builders should generate admission-ready ZIPs using this contract before the Owner receives a launch command.
