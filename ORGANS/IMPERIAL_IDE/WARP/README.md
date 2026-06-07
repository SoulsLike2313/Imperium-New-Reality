# WARP Hot Development Zone

WARP is an isolated development candidate under the Imperial IDE. Kernel files
are read-only baselines; generated artifacts, event logs, and manifests stay in
the ignored `runtime/` directory.

The release gate may produce `release_manifest.json`. It cannot apply changes
to the kernel, promote files, or bypass a future owner gate.

Use `ORGANS/IMPERIAL_IDE/run_warp_zone.ps1 -Command smoke` for validation.
