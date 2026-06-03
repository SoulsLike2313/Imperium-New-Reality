# Contour Router Contract

Supported contours for v0.1:

- PC.
- VM3.
- VM2.

## PC route

Run local intake/resolver in the current repo.

## VM3 route

Use a route config. Preferred current route is SSH alias `imperium-vm3` if present on PC. Do not hardcode private key material. Use paths and aliases only.

## VM2 route

Use a route config. If no verified route exists in the current repo/operator environment, produce a route-missing receipt and do not claim live success.

## Sync rule

Remote contours must be synced to the accepted current origin/master HEAD before registration. Use safe fast-forward behavior where possible. If registry conflicts occur, stop and require explicit resolution rather than silently overwriting.

## Receipt rule

Every route attempt must write:

- contour id.
- route config used.
- sync state.
- intake receipt path.
- resolver receipt path.
- launch-card state.
- verdict.
