const MAIN_SOURCE: &str = include_str!("../main.rs");

fn invoke_commands() -> Vec<&'static str> {
    let marker = "invoke_handler(tauri::generate_handler![";
    let start = MAIN_SOURCE.find(marker).expect("invoke handler missing") + marker.len();
    let end = MAIN_SOURCE[start..]
        .find("])")
        .map(|offset| start + offset)
        .expect("invoke handler is not closed");
    MAIN_SOURCE[start..end]
        .split(',')
        .map(str::trim)
        .filter(|entry| !entry.is_empty())
        .map(|entry| entry.rsplit("::").next().expect("command name"))
        .collect()
}

#[test]
fn thin_ide_invoke_surface_is_corridor_only() {
    assert_eq!(
        invoke_commands(),
        vec!["corridor_ui_snapshot", "corridor_ui_action"]
    );
}

#[test]
fn legacy_mutating_commands_have_no_tauri_wrapper_or_handler_entry() {
    let registered = invoke_commands();
    let normalized = MAIN_SOURCE.replace("\r\n", "\n");
    for command in [
        "register_patch_pack",
        "register_patch_pack_with_organs",
        "record_runtime_fps_proof",
        "initialize_imperium_core_update",
    ] {
        assert!(!registered.contains(&command));
        assert!(!normalized.contains(&format!("#[tauri::command]\nfn {command}(")));
    }
}
