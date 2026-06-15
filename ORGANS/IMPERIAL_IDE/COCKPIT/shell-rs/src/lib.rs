#[tauri::command]
fn greet(name: &str) -> String {
    format!("Imperial IDE Cockpit v0.1 :: {}", name)
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|_app| Ok(()))
        .run(tauri::generate_context!())
        .expect("error while running Cockpit");
}
