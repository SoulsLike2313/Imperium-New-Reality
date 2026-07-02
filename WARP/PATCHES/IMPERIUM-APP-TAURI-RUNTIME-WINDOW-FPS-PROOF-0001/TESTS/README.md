# TESTS — IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001

Expected:

- Tauri proof-run receipt is PASS;
- frontend contains runtime FPS markers;
- Rust bridge contains runtime FPS command;
- `npm run tauri:dev` opens a window long enough to write runtime FPS receipt;
- receipt proves average FPS >= 59.5 with sample_count >= 180 and slow_frame_ratio <= 0.05.
