use chrono::Utc;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
struct ActionResult {
    action_id: String,
    exit_code: i32,
    stdout: String,
    stderr: String,
    app_log: String,
    receipt: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct PackRequestResult {
    request: String,
    receipt: String,
}

fn sanitize_id(value: &str) -> String {
    value
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '-' || c == '_' || c == '.' {
                c
            } else {
                '_'
            }
        })
        .collect()
}

fn repo_root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let mut cur = exe.as_path();
    for _ in 0..12 {
        if let Some(parent) = cur.parent() {
            if parent.join("ORGANS").exists() && parent.join("WARP").exists() {
                return Ok(parent.to_path_buf());
            }
            cur = parent;
        }
    }

    if let Ok(cwd) = std::env::current_dir() {
        let candidates = [
            cwd.clone(),
            cwd.join(".."),
            cwd.join("..").join(".."),
            cwd.join("..").join("..").join(".."),
            cwd.join("..").join("..").join("..").join(".."),
        ];
        for c in candidates {
            let p = c.canonicalize().unwrap_or(c);
            if p.join("ORGANS").exists() && p.join("WARP").exists() {
                return Ok(p);
            }
        }
    }

    Err(format!("repo root not found for app {}", app.package_info().name))
}

fn read_json(path: &Path) -> Value {
    let text = fs::read_to_string(path).unwrap_or_else(|_| "{}".to_string());
    serde_json::from_str(&text).unwrap_or_else(|_| json!({}))
}

fn rel(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
}

fn ensure_dir(path: &Path) -> Result<(), String> {
    fs::create_dir_all(path).map_err(|e| e.to_string())
}

fn write_json(path: &Path, value: &Value) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        ensure_dir(parent)?;
    }
    let text = serde_json::to_string_pretty(value).map_err(|e| e.to_string())?;
    fs::write(path, format!("{text}\n")).map_err(|e| e.to_string())
}

fn proof_xp_from_state(state: &Value) -> i64 {
    let mut xp: i64 = 0;
    if state.get("astronomicon_chain_ok").and_then(|v| v.as_bool()) == Some(true) {
        xp += 100;
    }
    if state.get("stage_integrates_local_crown").and_then(|v| v.as_bool()) == Some(true) {
        xp += 100;
    }
    if let Some(scores) = state.get("crown_aware_scores").and_then(|v| v.as_object()) {
        for key in [
            "red_team_score",
            "blue_team_score",
            "custodes_organ_validators_score",
            "throne_organ_validators_score",
            "trust_proven_score",
            "rule_validated_score",
            "tui_launcher_presence_score",
            "throne_confirmed_score",
        ] {
            xp += scores.get(key).and_then(|v| v.as_f64()).unwrap_or(0.0) as i64;
        }
        if scores
            .get("organ_assembled_score")
            .and_then(|v| v.as_f64())
            .unwrap_or(999.0)
            == 0.0
        {
            xp += 25;
        }
    }
    xp
}

fn clean_streak(root: &Path) -> i64 {
    let mut count = 0;
    let receipt_dirs = [
        "SUPPORT/TUI/RECEIPTS",
        "SUPPORT/APP/RECEIPTS",
        "SUPPORT/APP_TAURI/receipts",
        "ORGANS/ASTRONOMICON/RECEIPTS",
        "ORGANS/CUSTODES/RECEIPTS",
        "ORGANS/THRONE/RECEIPTS",
    ];
    let mut files: Vec<PathBuf> = vec![];
    for d in receipt_dirs {
        let p = root.join(d);
        if let Ok(entries) = fs::read_dir(p) {
            for e in entries.flatten() {
                let path = e.path();
                if path.extension().and_then(|x| x.to_str()) == Some("json") {
                    files.push(path);
                }
            }
        }
    }
    files.sort_by_key(|p| fs::metadata(p).and_then(|m| m.modified()).ok());
    files.reverse();
    for p in files.into_iter().take(80) {
        let j = read_json(&p);
        let ok = if let Some(code) = j.get("exit_code").and_then(|v| v.as_i64()) {
            code == 0
        } else if let Some(verdict) = j.get("verdict").and_then(|v| v.as_str()) {
            verdict.starts_with("PASS")
        } else if let Some(errors) = j.get("errors").and_then(|v| v.as_array()) {
            errors.is_empty()
        } else {
            false
        };
        if ok {
            count += 1;
        } else {
            break;
        }
    }
    count
}

#[tauri::command]
fn read_imperium_state(app: tauri::AppHandle) -> Result<Value, String> {
    let root = repo_root(&app)?;
    let mut state = read_json(&root.join("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json"));
    let xp = proof_xp_from_state(&state);
    let streak = clean_streak(&root);
    state["proof_xp"] = json!(xp + (streak * 5).min(100));
    state["clean_streak"] = json!(streak);
    state["tauri_shell"] = json!("IMPERIUM_TAURI_SHELL_FOUNDATION");
    Ok(state)
}

#[tauri::command]
fn run_imperium_action(app: tauri::AppHandle, action_id: String) -> Result<ActionResult, String> {
    let allowed = [
        "status",
        "astronomicon-advice",
        "astronomicon-redblue",
        "astronomicon-hardening",
        "custodes-audit",
        "throne-crown-order",
        "throne-readout",
        "custodes-readout",
        "score-refresh-guidance",
    ];
    if !allowed.contains(&action_id.as_str()) {
        return Err(format!("action not allowed in Tauri shell foundation: {action_id}"));
    }

    let root = repo_root(&app)?;
    let tui = root.join("SUPPORT/TUI/imperium_tui.py");
    if !tui.exists() {
        return Err(format!("missing TUI backend: {}", rel(&tui, &root)));
    }

    let output = Command::new("python")
        .current_dir(&root)
        .arg(&tui)
        .arg("--repo-root")
        .arg(&root)
        .arg("--action")
        .arg(&action_id)
        .output()
        .map_err(|e| e.to_string())?;

    let exit_code = output.status.code().unwrap_or(-1);
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();

    let stamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
    let safe = sanitize_id(&action_id);
    let log_path = root.join("SUPPORT/APP_TAURI/logs").join(format!("{stamp}_{safe}.log"));
    let receipt_path = root.join("SUPPORT/APP_TAURI/receipts").join(format!("{stamp}_{safe}_receipt.json"));

    ensure_dir(log_path.parent().unwrap())?;
    fs::write(
        &log_path,
        format!("ACTION: {action_id}\nEXIT: {exit_code}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n"),
    )
    .map_err(|e| e.to_string())?;

    let receipt = json!({
        "receipt_id": format!("receipt.tauri.action.{stamp}.{safe}"),
        "verdict": if exit_code == 0 { "PASS_TAURI_ACTION_AQUARIUM_RUN" } else { "FAIL_TAURI_ACTION_AQUARIUM_RUN" },
        "action_id": action_id,
        "exit_code": exit_code,
        "app_log": rel(&log_path, &root),
        "generated_at_utc": Utc::now().to_rfc3339(),
        "errors": if exit_code == 0 { json!([]) } else { json!(["action exit code non-zero"]) },
        "warnings": json!(["Tauri v0.1 action output is collected, streaming events come in a later patch"])
    });
    write_json(&receipt_path, &receipt)?;

    Ok(ActionResult {
        action_id,
        exit_code,
        stdout,
        stderr,
        app_log: rel(&log_path, &root),
        receipt: rel(&receipt_path, &root),
    })
}

#[tauri::command]
fn create_pack_request(
    app: tauri::AppHandle,
    kind: String,
    pack_id: String,
    title: String,
    target_organ: String,
) -> Result<PackRequestResult, String> {
    let root = repo_root(&app)?;
    let stamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
    let safe = sanitize_id(&pack_id);
    let req_path = root
        .join("SUPPORT/APP_TAURI/receipts")
        .join(format!("{stamp}_{kind}_{safe}_request.json"));
    let receipt_path = root
        .join("SUPPORT/APP_TAURI/receipts")
        .join(format!("{stamp}_{kind}_{safe}_receipt.json"));

    let request = json!({
        "request_id": format!("tauri.pack_request.{stamp}.{safe}"),
        "kind": kind,
        "pack_id": pack_id,
        "title": title,
        "target_organ": target_organ,
        "status": "TAURI_APP_REQUEST_DRAFT_NOT_CANONICAL_REGISTRATION",
        "generated_at_utc": Utc::now().to_rfc3339(),
        "boundary": [
            "This is a Tauri app-level request draft.",
            "It does not claim canonical Astronomicon/Administratum registration."
        ]
    });
    write_json(&req_path, &request)?;

    let receipt = json!({
        "receipt_id": format!("receipt.tauri.pack_request.{stamp}.{safe}"),
        "verdict": "PASS_TAURI_PACK_REQUEST_DRAFTED",
        "request": rel(&req_path, &root),
        "generated_at_utc": Utc::now().to_rfc3339(),
        "errors": [],
        "warnings": ["not canonical registration"]
    });
    write_json(&receipt_path, &receipt)?;

    Ok(PackRequestResult {
        request: rel(&req_path, &root),
        receipt: rel(&receipt_path, &root),
    })
}

#[tauri::command]
fn read_eyes_contract(app: tauri::AppHandle) -> Result<Value, String> {
    let root = repo_root(&app)?;
    Ok(read_json(&root.join("SUPPORT/APP_TAURI/contracts/IMPERIUM_EYES_ROOM_CONTRACT_V0_1.json")))
}

#[tauri::command]
fn read_seed_core_contract(app: tauri::AppHandle) -> Result<Value, String> {
    let root = repo_root(&app)?;
    Ok(read_json(&root.join("SUPPORT/APP_TAURI/contracts/IMPERIUM_SEED_CORE_CONTRACT_DRAFT_V0_1.json")))
}

#[tauri::command]
fn app_selftest(app: tauri::AppHandle) -> Result<Value, String> {
    let root = repo_root(&app)?;
    Ok(json!({
        "verdict": "PASS_IMPERIUM_TAURI_APP_SELFTEST",
        "repo_root": root.to_string_lossy(),
        "tui_exists": root.join("SUPPORT/TUI/imperium_tui.py").exists(),
        "readout_exists": root.join("ORGANS/THRONE/REPORTS/POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json").exists(),
        "eyes_contract_exists": root.join("SUPPORT/APP_TAURI/contracts/IMPERIUM_EYES_ROOM_CONTRACT_V0_1.json").exists(),
        "seed_core_contract_exists": root.join("SUPPORT/APP_TAURI/contracts/IMPERIUM_SEED_CORE_CONTRACT_DRAFT_V0_1.json").exists(),
        "not_claimed": [
            "packaged exe installer",
            "Eyes embedded",
            "auto-updater active",
            "Great Nine assembled",
            "Core v1 ready"
        ]
    }))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            read_imperium_state,
            run_imperium_action,
            create_pack_request,
            read_eyes_contract,
            read_seed_core_contract,
            app_selftest
        ])
        .run(tauri::generate_context!())
        .expect("error while running Imperium Tauri application");
}

fn main() {
    run();
}
