// IMPERIUM_TAURI_COCKPIT_PATCH_REGISTRY_COMMANDS
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde_json::{json, Value};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn repo_root() -> Result<PathBuf, String> {
    let mut candidates: Vec<PathBuf> = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        candidates.push(cwd);
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            candidates.push(parent.to_path_buf());
        }
    }
    for mut dir in candidates {
        for _ in 0..12 {
            if dir.join("ORGANS").is_dir() && dir.join("WARP").is_dir() {
                return Ok(dir);
            }
            if !dir.pop() { break; }
        }
    }
    Err("repo root with ORGANS and WARP was not found".to_string())
}

fn safe_patch_id(patch_id: &str) -> bool {
    !patch_id.is_empty()
        && patch_id.len() < 160
        && patch_id.chars().all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '-' || c == '_' || c == '.')
        && !patch_id.contains("..")
        && !patch_id.contains('/')
        && !patch_id.contains('\\')
}

fn registry_path(repo: &Path) -> PathBuf {
    repo.join("SUPPORT").join("APP_TAURI").join("state").join("patch_pack_registry.json")
}

fn read_registry(repo: &Path) -> Value {
    let path = registry_path(repo);
    if path.is_file() {
        if let Ok(text) = fs::read_to_string(path) {
            if let Ok(value) = serde_json::from_str::<Value>(&text) {
                return value;
            }
        }
    }
    json!({
        "registry_id": "imperium.tauri.patch_pack_registry.v0_1",
        "registered_patch_packs": []
    })
}

fn write_registry(repo: &Path, registry: &Value) -> Result<(), String> {
    let path = registry_path(repo);
    if let Some(parent) = path.parent() { fs::create_dir_all(parent).map_err(|e| e.to_string())?; }
    let text = serde_json::to_string_pretty(registry).map_err(|e| e.to_string())? + "\n";
    fs::write(path, text).map_err(|e| e.to_string())
}

fn registered_ids(registry: &Value) -> Vec<String> {
    registry.get("registered_patch_packs")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|item| item.get("patch_id").and_then(|v| v.as_str()).map(|s| s.to_string())).collect())
        .unwrap_or_default()
}

fn patch_dir(repo: &Path, patch_id: &str) -> PathBuf {
    repo.join("WARP").join("PATCHES").join(patch_id)
}

fn find_runner(dir: &Path) -> Option<PathBuf> {
    let mut runners: Vec<PathBuf> = Vec::new();
    if let Ok(read) = fs::read_dir(dir) {
        for entry in read.flatten() {
            let path = entry.path();
            if path.is_file() {
                if let Some(name) = path.file_name().and_then(|s| s.to_str()) {
                    if name.starts_with("RUN_") && name.ends_with(".ps1") {
                        runners.push(path);
                    }
                }
            }
        }
    }
    runners.sort();
    runners.into_iter().next()
}

fn patch_pack_summary(repo: &Path, patch_id: &str, registered: bool) -> Value {
    let dir = patch_dir(repo, patch_id);
    let runner = find_runner(&dir);
    let patch_pack = dir.join("PATCH_PACK.md");
    json!({
        "patch_id": patch_id,
        "path": dir.to_string_lossy(),
        "has_runner": runner.is_some(),
        "runner": runner.as_ref().map(|p| p.to_string_lossy().to_string()),
        "has_patch_pack_md": patch_pack.is_file(),
        "registered": registered,
        "status": if registered { "REGISTERED" } else { "DISCOVERED" }
    })
}

#[tauri::command]
fn list_patch_packs() -> Result<Value, String> {
    let repo = repo_root()?;
    let registry = read_registry(&repo);
    let regs = registered_ids(&registry);
    let patches_dir = repo.join("WARP").join("PATCHES");
    let mut packs: Vec<Value> = Vec::new();
    if patches_dir.is_dir() {
        let mut ids: Vec<String> = Vec::new();
        for entry in fs::read_dir(&patches_dir).map_err(|e| e.to_string())?.flatten() {
            let path = entry.path();
            if path.is_dir() {
                if let Some(id) = path.file_name().and_then(|s| s.to_str()) {
                    if safe_patch_id(id) { ids.push(id.to_string()); }
                }
            }
        }
        ids.sort();
        ids.reverse();
        for id in ids {
            let registered = regs.iter().any(|x| x == &id);
            packs.push(patch_pack_summary(&repo, &id, registered));
        }
    }
    Ok(json!({
        "repo_root": repo.to_string_lossy(),
        "registry_path": registry_path(&repo).to_string_lossy(),
        "patch_packs": packs
    }))
}

#[tauri::command]
fn register_patch_pack(patch_id: String) -> Result<Value, String> {
    if !safe_patch_id(&patch_id) { return Err("unsafe patch_id".to_string()); }
    let repo = repo_root()?;
    let dir = patch_dir(&repo, &patch_id);
    if !dir.is_dir() { return Err(format!("patch dir not found: {}", dir.to_string_lossy())); }
    if find_runner(&dir).is_none() { return Err("patch runner RUN_*.ps1 not found".to_string()); }

    let mut registry = read_registry(&repo);
    let already = registered_ids(&registry).iter().any(|id| id == &patch_id);
    if !already {
        let entry = json!({
            "patch_id": patch_id,
            "registered_at_unix": now_unix(),
            "status": "REGISTERED",
            "source": "TAURI_COCKPIT"
        });
        if let Some(arr) = registry.get_mut("registered_patch_packs").and_then(|v| v.as_array_mut()) {
            arr.push(entry);
        } else {
            registry["registered_patch_packs"] = json!([entry]);
        }
        write_registry(&repo, &registry)?;
    }
    Ok(json!({
        "verdict": "PASS_PATCH_PACK_REGISTERED",
        "patch_id": patch_id,
        "already_registered": already,
        "registry_path": registry_path(&repo).to_string_lossy()
    }))
}

#[tauri::command]
fn run_registered_patch_pack(patch_id: String) -> Result<Value, String> {
    if !safe_patch_id(&patch_id) { return Err("unsafe patch_id".to_string()); }
    let repo = repo_root()?;
    let registry = read_registry(&repo);
    let is_registered = registered_ids(&registry).iter().any(|id| id == &patch_id);
    if !is_registered { return Err("patch pack is not registered; register it first".to_string()); }
    let dir = patch_dir(&repo, &patch_id);
    let runner = find_runner(&dir).ok_or_else(|| "patch runner RUN_*.ps1 not found".to_string())?;
    let runner_text = fs::read_to_string(&runner).unwrap_or_default().to_lowercase();
    let blocked = ["git push", "git commit", "format-volume", "remove-item -recurse -force c:", "remove-item -recurse -force e:"];
    for pattern in blocked {
        if runner_text.contains(pattern) {
            return Err(format!("runner blocked by cockpit safety pattern: {}", pattern));
        }
    }

    let output = Command::new("pwsh")
        .arg(&runner)
        .current_dir(&repo)
        .output()
        .map_err(|e| format!("failed to run pwsh: {}", e))?;

    let ts = now_unix();
    let app_dir = repo.join("SUPPORT").join("APP_TAURI");
    let logs_dir = app_dir.join("logs");
    let receipts_dir = app_dir.join("receipts");
    fs::create_dir_all(&logs_dir).map_err(|e| e.to_string())?;
    fs::create_dir_all(&receipts_dir).map_err(|e| e.to_string())?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let exit_code = output.status.code().unwrap_or(-1);
    let log_path = logs_dir.join(format!("{}_{}_patch_run.log", ts, patch_id));
    fs::write(&log_path, format!("# STDOUT\n{}\n\n# STDERR\n{}\n", stdout, stderr)).map_err(|e| e.to_string())?;

    let verdict = if output.status.success() { "PASS_PATCH_PACK_RUN_FROM_COCKPIT" } else { "FAIL_PATCH_PACK_RUN_FROM_COCKPIT" };
    let receipt = json!({
        "receipt_id": "receipt.support_app_tauri.patch_pack_run.v0_1",
        "patch_id": patch_id,
        "runner": runner.to_string_lossy(),
        "verdict": verdict,
        "exit_code": exit_code,
        "log": log_path.to_string_lossy(),
        "generated_at_unix": ts,
        "stdout_tail": stdout.chars().rev().take(4000).collect::<String>().chars().rev().collect::<String>(),
        "stderr_tail": stderr.chars().rev().take(2000).collect::<String>().chars().rev().collect::<String>()
    });
    let receipt_path = receipts_dir.join(format!("{}_{}_patch_run_receipt.json", ts, patch_id));
    fs::write(&receipt_path, serde_json::to_string_pretty(&receipt).map_err(|e| e.to_string())? + "\n").map_err(|e| e.to_string())?;
    Ok(json!({
        "verdict": verdict,
        "patch_id": patch_id,
        "exit_code": exit_code,
        "receipt": receipt_path.to_string_lossy(),
        "log": log_path.to_string_lossy()
    }))
}

#[tauri::command]
fn get_mechanicus_language_codex() -> Result<Value, String> {
    let repo = repo_root()?;
    let path = repo.join("ORGANS").join("MECHANICUS").join("MATRICES").join("MECHANICUS_LANGUAGE_POWER_MATRIX_V0_1.json");
    let text = fs::read_to_string(&path).map_err(|e| format!("language matrix read failed: {}", e))?;
    serde_json::from_str::<Value>(&text).map_err(|e| format!("language matrix parse failed: {}", e))
}

#[tauri::command]
fn record_runtime_fps_proof(payload: Value) -> Result<Value, String> {
    let repo = repo_root()?;
    let ts = now_unix();
    let target = payload.get("target_fps").and_then(|v| v.as_f64()).unwrap_or(60.0);
    let avg = payload.get("average_fps").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let samples = payload.get("sample_count").and_then(|v| v.as_u64()).unwrap_or(0);
    let slow_ratio = payload.get("slow_frame_ratio").and_then(|v| v.as_f64()).unwrap_or(1.0);
    let verdict = if target >= 60.0 && avg >= 59.5 && samples >= 180 && slow_ratio <= 0.05 {
        "PASS_TAURI_RUNTIME_WINDOW_FPS_LOCK_PROVEN"
    } else {
        "FAIL_TAURI_RUNTIME_WINDOW_FPS_LOCK"
    };
    let receipt = json!({
        "receipt_id": "receipt.support_app_tauri.runtime_fps_proof.v0_1",
        "verdict": verdict,
        "proof_level": "RUNTIME_WINDOW_AND_WEBVIEW_FPS_LOCK",
        "payload": payload,
        "generated_at_unix": ts
    });
    let dir = repo.join("SUPPORT").join("APP_TAURI").join("receipts");
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(format!("{}_runtime_fps_proof_receipt.json", ts));
    fs::write(&path, serde_json::to_string_pretty(&receipt).map_err(|e| e.to_string())? + "\n").map_err(|e| e.to_string())?;
    Ok(json!({"verdict": verdict, "receipt": path.to_string_lossy()}))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            list_patch_packs,
            register_patch_pack,
            run_registered_patch_pack,
            get_mechanicus_language_codex,
            record_runtime_fps_proof
        ])
        .run(tauri::generate_context!())
        .expect("error while running Imperium Tauri Shell");
}
