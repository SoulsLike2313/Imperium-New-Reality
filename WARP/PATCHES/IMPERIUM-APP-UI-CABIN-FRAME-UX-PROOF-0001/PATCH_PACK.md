# PATCH PACK — IMPERIUM-APP-UI-CABIN-FRAME-UX-PROOF-0001

status: `WARP_CANDIDATE`  
owner: `APP_PLATFORM + MECHANICUS`  
mode: `UI_LAYOUT_AND_UX_PROOF_FIX`

## Purpose

Fix the marked UI failures:

- protruding zones;
- cropped/broken view;
- too little motion;
- weak control-cabin feeling;
- still weak gothic/metal/cyber/trash-polka identity.

## Fix

- App uses a fixed viewport cabin frame instead of page-level scroll.
- Hero becomes compact.
- Navigation, main deck and Aquarium become internal cockpit zones.
- HUD uses a proper grid and ellipsis to avoid collisions.
- Organ cards are smaller and fit better.
- Aquarium becomes a dedicated bottom proof console.
- UX controls emit `UX_PROOF_MARKER` log entries.
- UI still refuses fake execution claims.

## Boundary

```text
UX proof is not execution proof.
UI renders truth; receipts prove truth.
```

## Not claimed

- final AAA polish;
- game projection runtime;
- full Patch Forge backend complete;
- Core v1 ready;
- Great Nine assembled.
