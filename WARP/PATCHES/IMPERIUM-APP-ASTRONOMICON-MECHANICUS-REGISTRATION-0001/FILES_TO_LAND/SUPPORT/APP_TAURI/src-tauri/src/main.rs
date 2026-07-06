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


fn read_json_file(path: &Path) -> Option<Value> {
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str::<Value>(&text).ok()
}

fn rel_path(base: &Path, path: &Path) -> String {
    path.strip_prefix(base)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
}

fn collect_files_limited(root: &Path, limit: usize) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    let mut stack: Vec<PathBuf> = vec![root.to_path_buf()];
    while let Some(dir) = stack.pop() {
        if out.len() >= limit { break; }
        if let Ok(read) = fs::read_dir(&dir) {
            let mut entries: Vec<PathBuf> = read.flatten().map(|e| e.path()).collect();
            entries.sort();
            for path in entries {
                if out.len() >= limit { break; }
                if path.is_dir() {
                    if let Some(name) = path.file_name().and_then(|s| s.to_str()) {
                        if name == "target" || name == "node_modules" || name == "__pycache__" { continue; }
                    }
                    stack.push(path);
                } else if path.is_file() {
                    out.push(path);
                }
            }
        }
    }
    out.sort();
    out
}

fn language_for_path(path: &Path) -> &'static str {
    match path.extension().and_then(|s| s.to_str()).unwrap_or("").to_ascii_lowercase().as_str() {
        "py" => "Python",
        "ps1" | "psm1" | "psd1" => "PowerShell",
        "js" | "mjs" => "JavaScript",
        "ts" | "tsx" => "TypeScript",
        "css" => "CSS",
        "rs" => "Rust",
        "json" | "jsonl" => "JSON",
        "md" => "Markdown",
        "toml" => "TOML",
        "html" => "HTML",
        _ => "Other",
    }
}

fn push_unique(list: &mut Vec<String>, value: &str) {
    if !list.iter().any(|item| item == value) {
        list.push(value.to_string());
    }
}

fn file_line_count(path: &Path) -> usize {
    fs::read_to_string(path).map(|s| s.lines().count()).unwrap_or(0)
}

fn infer_task_class(patch_id: &str, rels: &[String]) -> String {
    let joined = format!("{} {}", patch_id, rels.join(" ")).to_ascii_uppercase();
    if joined.contains("APP_TAURI") || joined.contains("EYES") || joined.contains("CANVAS") || joined.contains("UI") || joined.contains("STYLE") {
        "UI_PRODUCT_SURFACE_OR_VISUAL_RUNTIME".to_string()
    } else if joined.contains("MECHANICUS") && (joined.contains("TOOL") || joined.contains("VALIDATOR") || joined.contains("BUILD")) {
        "MECHANICUS_TOOLING_OR_VALIDATION".to_string()
    } else if joined.contains("ASTRONOMICON") || joined.contains("INTAKE") || joined.contains("REGISTRATION") {
        "PATCH_PACK_INTAKE_AND_REGISTRATION".to_string()
    } else if joined.contains("CUSTODES") || joined.contains("THRONE") || joined.contains("LAW") || joined.contains("MATRIX") {
        "GOVERNANCE_EVIDENCE_GATE".to_string()
    } else {
        "IMPERIUM_PATCH_PACK".to_string()
    }
}

fn analyze_patch_pack_core(repo: &Path, patch_id: &str, register: bool) -> Result<Value, String> {
    if !safe_patch_id(patch_id) { return Err("unsafe patch_id".to_string()); }
    let dir = patch_dir(repo, patch_id);
    if !dir.is_dir() { return Err(format!("patch dir not found: {}", dir.to_string_lossy())); }

    let patch_pack_md = dir.join("PATCH_PACK.md");
    let files_to_land = dir.join("FILES_TO_LAND");
    let manifest = dir.join("PATCH_FILE_MANIFEST_SHA256.json");
    let runner = find_runner(&dir);
    let _pack_files = collect_files_limited(&dir, 900);
    let land_files = if files_to_land.is_dir() { collect_files_limited(&files_to_land, 900) } else { Vec::new() };
    let rels: Vec<String> = land_files.iter().map(|p| rel_path(&files_to_land, p)).collect();

    let mut languages: Vec<String> = Vec::new();
    for path in land_files.iter() {
        let lang = language_for_path(path);
        if lang != "Other" { push_unique(&mut languages, lang); }
    }
    languages.sort();

    let joined = format!("{} {}", patch_id, rels.join(" ")).to_ascii_uppercase();
    let touches_app = joined.contains("SUPPORT/APP_TAURI");
    let touches_ui = touches_app || joined.contains("UI") || joined.contains("EYES") || joined.contains("CANVAS") || joined.contains("CSS") || joined.contains("MAIN.JS");
    let touches_rust = languages.iter().any(|x| x == "Rust");
    let touches_js = languages.iter().any(|x| x == "JavaScript" || x == "TypeScript");
    let touches_css = languages.iter().any(|x| x == "CSS");
    let touches_python = languages.iter().any(|x| x == "Python");
    let touches_powershell = languages.iter().any(|x| x == "PowerShell");
    let task_class = infer_task_class(patch_id, &rels);

    let mut toolchains: Vec<Value> = Vec::new();
    if touches_python { toolchains.push(json!({"toolchain":"Python", "mode":"validator_builder_receipt", "proof":"py_compile + validator receipt"})); }
    if touches_powershell { toolchains.push(json!({"toolchain":"PowerShell", "mode":"Owner-host WARP runner", "proof":"pwsh 7.6.2 runner"})); }
    if touches_js { toolchains.push(json!({"toolchain":"Node/Vite", "mode":"frontend build", "proof":"npm run build"})); }
    if touches_css { toolchains.push(json!({"toolchain":"CSS", "mode":"UI skin/module law", "proof":"no-monolith + visual/fidelity proof required"})); }
    if touches_rust { toolchains.push(json!({"toolchain":"Rust/Tauri", "mode":"backend command surface", "proof":"cargo check"})); }
    if languages.iter().any(|x| x == "JSON") { toolchains.push(json!({"toolchain":"JSON", "mode":"evidence/contract/matrix", "proof":"json parse + schema/semantic validator"})); }

    let main_js_lines = file_line_count(&repo.join("SUPPORT/APP_TAURI/src/main.js"));
    let css_lines = file_line_count(&repo.join("SUPPORT/APP_TAURI/src/styles.css"));
    let patch_touches_main_js = rels.iter().any(|p| p == "SUPPORT/APP_TAURI/src/main.js");
    let patch_touches_styles = rels.iter().any(|p| p == "SUPPORT/APP_TAURI/src/styles.css");
    let monolith_risk = if patch_touches_main_js || patch_touches_styles || main_js_lines > 420 || css_lines > 950 {
        "HIGH_REQUIRES_MODULE_DECOMPOSITION"
    } else if touches_ui {
        "MEDIUM_UI_SURFACE_REQUIRES_NODE_BOUNDARIES"
    } else {
        "LOW_NON_UI_PATCH"
    };

    let mut required_validators: Vec<String> = vec!["patch_pack_shape_smoke".to_string(), "no_control_chars".to_string(), "json_parse".to_string()];
    if touches_python { required_validators.push("python_py_compile".to_string()); }
    if touches_powershell { required_validators.push("pwsh_runner_exit_code".to_string()); }
    if touches_js { required_validators.push("npm_run_build".to_string()); }
    if touches_rust { required_validators.push("cargo_check".to_string()); }
    if touches_ui { required_validators.push("ui_reference_fidelity_or_screenshot_proof".to_string()); required_validators.push("runtime_fps_proof".to_string()); }

    let mut missing_capabilities: Vec<String> = Vec::new();
    if touches_ui { missing_capabilities.push("UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI".to_string()); }
    if joined.contains("EYES") || joined.contains("CANVAS") || joined.contains("GAME") { missing_capabilities.push("GAME_OR_CANVAS_RUNTIME_CAPABILITY_NOT_FULLY_INVENTORIED".to_string()); }
    if patch_touches_main_js || patch_touches_styles { missing_capabilities.push("APP_TAURI_MONOLITH_DECOMPOSITION_REQUIRED".to_string()); }

    let visual_stack = if touches_ui {
        json!({
            "required": true,
            "stack": ["Tauri WebView", "JavaScript/TypeScript components", "CSS tokens/modules", "Rust command bridge", "FPS receipt", "screenshot/reference fidelity proof"],
            "eyes_canvas_candidate": joined.contains("EYES") || joined.contains("CANVAS"),
            "law": "visual output is product surface, not proof; proof stays in receipts/reports"
        })
    } else {
        json!({"required": false, "stack": [], "law": "non-UI patch"})
    };

    let dependency_impact = json!({
        "zones": [
            {"zone":"WARP/PATCHES", "impact":"patch form and runner lifecycle", "touched": rels.iter().any(|p| p.starts_with("WARP/PATCHES"))},
            {"zone":"SUPPORT/APP_TAURI/src/main.js", "impact":"frontend room/state/event surface; split into nodes when growth continues", "touched": patch_touches_main_js, "line_count_now": main_js_lines},
            {"zone":"SUPPORT/APP_TAURI/src/styles.css", "impact":"visual skin/token surface; split into style modules when growth continues", "touched": patch_touches_styles, "line_count_now": css_lines},
            {"zone":"SUPPORT/APP_TAURI/src-tauri/src/main.rs", "impact":"backend command bridge; any change requires cargo check", "touched": rels.iter().any(|p| p == "SUPPORT/APP_TAURI/src-tauri/src/main.rs")},
            {"zone":"ORGANS/MECHANICUS", "impact":"machine truth and toolchain verdicts", "touched": rels.iter().any(|p| p.starts_with("ORGANS/MECHANICUS"))},
            {"zone":"ORGANS/ASTRONOMICON", "impact":"intake and registration truth", "touched": rels.iter().any(|p| p.starts_with("ORGANS/ASTRONOMICON"))}
        ],
        "cascade_rule": "A node change does not imply global rewrite; it identifies dependent nodes that must be revalidated."
    });

    let tool_admission_summary = read_json_file(&repo.join("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json"));
    let current_truth_index = read_json_file(&repo.join("ORGANS/MECHANICUS/MATRICES/MECHANICUS_CURRENT_TRUTH_INDEX_V0_1.json"));

    let astronomicon = json!({
        "organ_id": "ASTRONOMICON",
        "verdict": if patch_pack_md.is_file() && files_to_land.is_dir() && runner.is_some() { "REGISTERABLE_PATCH_PACK" } else { "BLOCKED_DIRTY_OR_INCOMPLETE_PACK" },
        "checks": {
            "patch_id_safe": true,
            "patch_dir_exists": dir.is_dir(),
            "patch_pack_md_exists": patch_pack_md.is_file(),
            "files_to_land_exists": files_to_land.is_dir(),
            "manifest_exists": manifest.is_file(),
            "runner_exists": runner.is_some(),
            "land_file_count": land_files.len()
        },
        "meaning": "Astronomicon registers patch intent and shape, then asks Mechanicus for machine verdict."
    });

    let mechanicus = json!({
        "organ_id": "MECHANICUS",
        "verdict": if missing_capabilities.is_empty() { "MECHANICUS_ACCEPTS_DRY_VALIDATION_PATH" } else { "MECHANICUS_ACCEPTS_WITH_VISIBLE_DEBT" },
        "task_class": task_class,
        "languages": languages,
        "toolchains": toolchains,
        "required_validators": required_validators,
        "monolith_risk": monolith_risk,
        "visual_stack": visual_stack,
        "dependency_impact": dependency_impact,
        "missing_capabilities": missing_capabilities,
        "real_execution": "BLOCKED_BY_POLICY",
        "tool_admission": tool_admission_summary.unwrap_or(json!({"status":"TOOL_ADMISSION_SUMMARY_NOT_FOUND_ON_THIS_HOST"})),
        "current_truth_index_seen": current_truth_index.is_some(),
        "meaning": "Mechanicus recommends stack and validators; it does not execute or crown the patch."
    });

    let summary = json!({
        "summary_id": "imperium.app.astronomicon_mechanicus.patch_registration_summary.v0_1",
        "patch_id": patch_id,
        "registered": register,
        "generated_at_unix": now_unix(),
        "repo_root": repo.to_string_lossy(),
        "astronomicon": astronomicon,
        "mechanicus": mechanicus,
        "next_complex_trial_task": {
            "task_id": "IMPERIUM-APP-EYES-CANVAS-DAILY-OPERATIONS-0001",
            "task_class": "UI_PRODUCT_SURFACE_OR_VISUAL_RUNTIME",
            "goal": "Integrate an Eyes/Canvas room into daily app operation so the Owner can watch a new path point appear in real time.",
            "expected_languages": ["JavaScript/TypeScript", "CSS", "Rust/Tauri", "JSON", "Python", "PowerShell", "Markdown"],
            "expected_mechanicus_pressure": ["visual_stack_planning", "monolith_control", "node_boundary_map", "dependency_impact", "fps_and_fidelity_proof"]
        }
    });
    Ok(summary)
}

#[tauri::command]
fn analyze_patch_pack_organ_summary(patch_id: String) -> Result<Value, String> {
    let repo = repo_root()?;
    analyze_patch_pack_core(&repo, &patch_id, false)
}

#[tauri::command]
fn register_patch_pack_with_organs(patch_id: String) -> Result<Value, String> {
    let repo = repo_root()?;
    let summary = analyze_patch_pack_core(&repo, &patch_id, true)?;
    let mut registry = read_registry(&repo);
    let already = registered_ids(&registry).iter().any(|id| id == &patch_id);
    let entry = json!({
        "patch_id": patch_id,
        "registered_at_unix": now_unix(),
        "status": "REGISTERED_BY_ASTRONOMICON_WITH_MECHANICUS_SUMMARY",
        "source": "TAURI_ASTRONOMICON_ROOM",
        "organ_summary": summary
    });
    if let Some(arr) = registry.get_mut("registered_patch_packs").and_then(|v| v.as_array_mut()) {
        arr.retain(|item| item.get("patch_id").and_then(|v| v.as_str()) != Some(patch_id.as_str()));
        arr.push(entry);
    } else {
        registry["registered_patch_packs"] = json!([entry]);
    }
    write_registry(&repo, &registry)?;
    Ok(json!({
        "verdict": "PASS_ASTRONOMICON_REGISTERED_MECHANICUS_SUMMARY_READY",
        "patch_id": patch_id,
        "already_registered": already,
        "registry_path": registry_path(&repo).to_string_lossy(),
        "organ_summary": summary
    }))
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
            analyze_patch_pack_organ_summary,
            register_patch_pack_with_organs,
            get_mechanicus_language_codex,
            record_runtime_fps_proof
        ])
        .run(tauri::generate_context!())
        .expect("error while running Imperium Tauri Shell");
}
