use super::bridge_receipt::write_bridge_receipt;
use super::process_boundary::{
    add_pinned_tool_environment, admit_interpreter, execute_python, minimal_environment,
    sha256_file, InterpreterAdmission, MinimalEnvironment, ReceiptBinding,
};
use serde::de::DeserializeOwned;
use serde::Deserialize;
use serde_json::Value;
use std::collections::BTreeSet;
use std::ffi::OsString;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::time::Duration;

const CORRIDOR_MODULE: &str = "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli";
const CAPABILITY_REGISTRY_RELATIVE: &str =
    "ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json";
const TASK_STATE_RELATIVE: &str =
    "ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/TASK_STATE.json";
const RECEIPT_RELATIVE: &str = "ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/PHASE_4_BRIDGE_RECEIPTS";
const EXPECTED_TASK_ID: &str = "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001";
const EXPECTED_WARP_ID: &str = "WARP-CORE-REFERENCE-0001";
const EXPECTED_BASE_HEAD: &str = "281c3a7c8463de7fb64473929fe0ed975f99f595";
const SNAPSHOT_TIMEOUT: Duration = Duration::from_secs(15);
const ACTION_TIMEOUT: Duration = Duration::from_secs(120);
const MAX_PAYLOAD_BYTES: usize = 128 * 1024;
const MAX_CONFIG_BYTES: u64 = 2 * 1024 * 1024;

#[derive(Deserialize)]
struct CapabilityRegistry {
    schema_version: String,
    task_id: String,
    base_head: String,
    default_policy: String,
    capabilities: Vec<CapabilityRecord>,
}

#[derive(Deserialize)]
struct CapabilityRecord {
    capability_id: String,
    #[serde(rename = "type")]
    capability_type: String,
    adapter_id: String,
    actual_effect_class: String,
    admission_state: String,
    allowed_operations: Vec<String>,
    executable_path: String,
    executable_sha256: String,
    allowed_read_roots: Vec<String>,
}

#[derive(Deserialize)]
struct TaskState {
    schema_version: String,
    task_id: String,
    base_head: String,
    branch: String,
    warp: WarpState,
}

#[derive(Deserialize)]
struct WarpState {
    warp_id: String,
    base_head: String,
    path: String,
    state: String,
}

#[derive(Clone, Debug)]
pub(crate) struct ToolAdmission {
    pub executable_path: PathBuf,
    pub sha256: String,
}

pub(crate) struct BridgeContext {
    pub repo: PathBuf,
    pub admission: InterpreterAdmission,
    pub git: ToolAdmission,
    pub pwsh: ToolAdmission,
    pub binding: ReceiptBinding,
    pub receipt_dir: PathBuf,
}

fn read_json_bounded<T: DeserializeOwned>(path: &Path) -> Result<T, String> {
    let metadata = path
        .metadata()
        .map_err(|error| format!("BRIDGE_CONFIG_METADATA_FAILED: {error}"))?;
    if !metadata.is_file() || metadata.len() == 0 || metadata.len() > MAX_CONFIG_BYTES {
        return Err("BRIDGE_CONFIG_SIZE_OR_TYPE_REJECTED".to_string());
    }
    let mut file =
        File::open(path).map_err(|error| format!("BRIDGE_CONFIG_OPEN_FAILED: {error}"))?;
    let mut bytes = Vec::with_capacity(metadata.len() as usize);
    file.read_to_end(&mut bytes)
        .map_err(|error| format!("BRIDGE_CONFIG_READ_FAILED: {error}"))?;
    serde_json::from_slice(&bytes).map_err(|error| format!("BRIDGE_CONFIG_PARSE_FAILED: {error}"))
}

fn has_corridor_contract(candidate: &Path) -> bool {
    candidate.join(".git").exists()
        && candidate
            .join("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR")
            .is_dir()
        && candidate.join(CAPABILITY_REGISTRY_RELATIVE).is_file()
        && candidate.join(TASK_STATE_RELATIVE).is_file()
}

pub(crate) fn resolve_repo_root() -> Result<PathBuf, String> {
    let manifest = Path::new(env!("CARGO_MANIFEST_DIR"))
        .canonicalize()
        .map_err(|error| format!("BRIDGE_MANIFEST_ROOT_UNAVAILABLE: {error}"))?;
    for candidate in manifest.ancestors() {
        if has_corridor_contract(candidate) {
            return candidate
                .canonicalize()
                .map_err(|error| format!("BRIDGE_REPOSITORY_CANONICALIZE_FAILED: {error}"));
        }
    }
    Err("BRIDGE_COMPILE_TIME_REPOSITORY_NOT_ADMITTED".to_string())
}


fn admit_system_tool(
    registry: &CapabilityRegistry,
    repo: &Path,
    capability_id: &str,
    allowed_names: &[&str],
    required_operation: &str,
) -> Result<ToolAdmission, String> {
    let matches: Vec<&CapabilityRecord> = registry
        .capabilities
        .iter()
        .filter(|record| record.capability_id == capability_id)
        .collect();
    if matches.len() != 1 {
        return Err(format!("BRIDGE_{capability_id}_ADMISSION_AMBIGUOUS"));
    }
    let record = matches[0];
    if record.capability_type != "SYSTEM_EXECUTABLE"
        || record.adapter_id != "PINNED_EXECUTABLE_V0_1"
        || record.actual_effect_class != "READ_ONLY"
        || record.admission_state != "ACTIVE"
        || !record.allowed_operations.iter().any(|item| item == required_operation)
    {
        return Err(format!("BRIDGE_{capability_id}_CONTRACT_REJECTED"));
    }
    let configured = Path::new(&record.executable_path);
    if !configured.is_absolute() {
        return Err(format!("BRIDGE_{capability_id}_PATH_NOT_ABSOLUTE"));
    }
    let executable = configured
        .canonicalize()
        .map_err(|error| format!("BRIDGE_{capability_id}_PATH_UNAVAILABLE: {error}"))?;
    let name = executable
        .file_name()
        .and_then(|item| item.to_str())
        .ok_or_else(|| format!("BRIDGE_{capability_id}_FILENAME_UNKNOWN"))?;
    if !allowed_names.iter().any(|allowed| name.eq_ignore_ascii_case(allowed)) {
        return Err(format!("BRIDGE_{capability_id}_FILENAME_REJECTED"));
    }
    if record.executable_sha256.len() != 64
        || !record
            .executable_sha256
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(format!("BRIDGE_{capability_id}_HASH_INVALID"));
    }
    if sha256_file(&executable)? != record.executable_sha256.to_ascii_lowercase() {
        return Err(format!("BRIDGE_{capability_id}_HASH_MISMATCH"));
    }
    let mut repo_read_admitted = false;
    for allowed in &record.allowed_read_roots {
        let allowed = Path::new(allowed)
            .canonicalize()
            .map_err(|error| format!("BRIDGE_{capability_id}_READ_ROOT_UNKNOWN: {error}"))?;
        repo_read_admitted |= allowed == repo;
    }
    if !repo_read_admitted {
        return Err(format!("BRIDGE_{capability_id}_READ_SCOPE_REJECTED"));
    }
    Ok(ToolAdmission {
        executable_path: executable,
        sha256: record.executable_sha256.to_ascii_lowercase(),
    })
}

pub(crate) fn load_bridge_context(repo: &Path) -> Result<BridgeContext, String> {
    let repo = repo
        .canonicalize()
        .map_err(|error| format!("BRIDGE_REPOSITORY_UNAVAILABLE: {error}"))?;
    if !has_corridor_contract(&repo) {
        return Err("BRIDGE_REPOSITORY_CONTRACT_MISSING".to_string());
    }
    let registry: CapabilityRegistry = read_json_bounded(&repo.join(CAPABILITY_REGISTRY_RELATIVE))?;
    if registry.schema_version != "imperium.core_reference_corridor.capability_registry.v0_1"
        || registry.default_policy != "DENY"
        || registry.task_id != EXPECTED_TASK_ID
        || registry.base_head != EXPECTED_BASE_HEAD
    {
        return Err("BRIDGE_CAPABILITY_REGISTRY_BINDING_REJECTED".to_string());
    }

    let python_capabilities: Vec<&CapabilityRecord> = registry
        .capabilities
        .iter()
        .filter(|record| record.capability_type == "PYTHON_MODULE")
        .collect();
    if python_capabilities.is_empty() {
        return Err("BRIDGE_PYTHON_ADMISSION_MISSING".to_string());
    }
    let identities: BTreeSet<(&str, &str)> = python_capabilities
        .iter()
        .map(|record| {
            (
                record.executable_path.as_str(),
                record.executable_sha256.as_str(),
            )
        })
        .collect();
    if identities.len() != 1 {
        return Err("BRIDGE_PYTHON_ADMISSION_AMBIGUOUS".to_string());
    }
    let diagnostic_matches: Vec<&CapabilityRecord> = python_capabilities
        .iter()
        .copied()
        .filter(|record| record.capability_id == "CORE_DIAGNOSTIC")
        .collect();
    if diagnostic_matches.len() != 1 {
        return Err("BRIDGE_DIAGNOSTIC_ADMISSION_AMBIGUOUS".to_string());
    }
    let diagnostic = diagnostic_matches[0];
    if diagnostic.adapter_id != "FIXED_ARGV_PYTHON_MODULE_V0_1"
        || diagnostic.actual_effect_class != "READ_ONLY"
    {
        return Err("BRIDGE_DIAGNOSTIC_ADAPTER_REJECTED".to_string());
    }
    let mut repo_read_admitted = false;
    for allowed in &diagnostic.allowed_read_roots {
        let allowed = Path::new(allowed)
            .canonicalize()
            .map_err(|error| format!("BRIDGE_ALLOWED_READ_ROOT_UNKNOWN: {error}"))?;
        repo_read_admitted |= allowed == repo;
    }
    if !repo_read_admitted {
        return Err("BRIDGE_REPOSITORY_READ_SCOPE_REJECTED".to_string());
    }
    let admission = admit_interpreter(
        Path::new(&diagnostic.executable_path),
        &diagnostic.executable_sha256,
    )?;
    let git = admit_system_tool(
        &registry,
        &repo,
        "CORE_GIT",
        &["git.exe", "git"],
        "repository_read",
    )?;
    let pwsh = admit_system_tool(
        &registry,
        &repo,
        "CORE_PWSH",
        &["pwsh.exe", "pwsh"],
        "version_probe",
    )?;

    let state: TaskState = read_json_bounded(&repo.join(TASK_STATE_RELATIVE))?;
    if state.schema_version != "imperium.core_reference_corridor.task_state.v0_1"
        || state.task_id != registry.task_id
        || state.task_id != EXPECTED_TASK_ID
        || state.base_head != registry.base_head
        || state.base_head != EXPECTED_BASE_HEAD
        || state.branch != "servitor/imperium-core-reference-corridor-0001"
        || state.warp.warp_id != EXPECTED_WARP_ID
        || state.warp.base_head != EXPECTED_BASE_HEAD
        || state.warp.state != "ACTIVE"
    {
        return Err("BRIDGE_TASK_WARP_BASE_BINDING_REJECTED".to_string());
    }
    let warp_path = Path::new(&state.warp.path)
        .canonicalize()
        .map_err(|error| format!("BRIDGE_WARP_PATH_UNKNOWN: {error}"))?;
    if warp_path != repo {
        return Err("BRIDGE_WARP_PATH_MISMATCH".to_string());
    }
    Ok(BridgeContext {
        repo: repo.clone(),
        admission,
        git,
        pwsh,
        binding: ReceiptBinding {
            task_id: state.task_id,
            warp_id: state.warp.warp_id,
            base_head: state.base_head,
        },
        receipt_dir: repo.join(RECEIPT_RELATIVE),
    })
}

pub(crate) fn snapshot_args() -> Vec<String> {
    vec![
        "-m".to_string(),
        CORRIDOR_MODULE.to_string(),
        "ui-snapshot".to_string(),
    ]
}

fn valid_action_id(action_id: &str) -> bool {
    !action_id.is_empty()
        && action_id.len() <= 128
        && action_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'_' | b'-' | b'.' | b':'))
}

pub(crate) fn action_args(action_id: &str, payload_json: &str) -> Result<Vec<String>, String> {
    if !valid_action_id(action_id) {
        return Err("BRIDGE_ACTION_ID_REJECTED".to_string());
    }
    if payload_json.len() > MAX_PAYLOAD_BYTES {
        return Err(format!(
            "BRIDGE_ACTION_PAYLOAD_EXCEEDS_{MAX_PAYLOAD_BYTES}_BYTES"
        ));
    }
    Ok(vec![
        "-m".to_string(),
        CORRIDOR_MODULE.to_string(),
        "ui-action".to_string(),
        "--action-id".to_string(),
        action_id.to_string(),
        "--payload-json".to_string(),
        payload_json.to_string(),
    ])
}

fn host_environment() -> MinimalEnvironment {
    std::env::vars_os().collect()
}

fn output_block_verdict(output: &super::process_boundary::ProcessOutput) -> &'static str {
    if !output.termination.tree_terminated {
        "BLOCK_PROCESS_TREE_TERMINATION_UNPROVEN"
    } else if output.timed_out {
        "BLOCK_TIMEOUT"
    } else if output.stdout_truncated || output.stderr_truncated {
        "BLOCK_OUTPUT_LIMIT"
    } else if !output.stdout_utf8 || !output.stderr_utf8 {
        "BLOCK_OUTPUT_NOT_UTF8"
    } else {
        "BLOCK_PROCESS_EXIT"
    }
}

fn run_corridor_cli(
    repo: &Path,
    args: Vec<String>,
    timeout: Duration,
    operation: &str,
) -> Result<Value, String> {
    let context = load_bridge_context(repo)?;
    let mut environment = minimal_environment(&host_environment(), &context.repo)?;
    environment.insert(
        OsString::from("IMPERIUM_PINNED_TOOLCHAIN_REQUIRED"),
        OsString::from("1"),
    );
    add_pinned_tool_environment(
        &mut environment,
        "IMPERIUM_GIT_EXECUTABLE",
        "IMPERIUM_GIT_SHA256",
        &context.git.executable_path,
        &context.git.sha256,
    )?;
    add_pinned_tool_environment(
        &mut environment,
        "IMPERIUM_PWSH_EXECUTABLE",
        "IMPERIUM_PWSH_SHA256",
        &context.pwsh.executable_path,
        &context.pwsh.sha256,
    )?;
    let os_args: Vec<OsString> = args.iter().map(OsString::from).collect();
    let output = execute_python(
        &context.admission,
        &os_args,
        &context.repo,
        &context.repo,
        &environment,
        timeout,
    )?;
    let parsed: Result<Value, String> = if output.success {
        serde_json::from_str::<Value>(output.stdout.trim())
            .map_err(|error| format!("BRIDGE_INVALID_JSON: {error}"))
    } else {
        Err("BRIDGE_PROCESS_OUTPUT_BLOCKED".to_string())
    };
    let verdict = if !output.success {
        output_block_verdict(&output)
    } else if parsed.is_err() {
        "BLOCK_INVALID_JSON"
    } else {
        "PASS_PROVEN"
    };
    let receipt = write_bridge_receipt(
        &context.receipt_dir,
        &context.binding,
        operation,
        &context.admission,
        &os_args,
        &context.repo,
        &environment,
        timeout,
        &output,
        verdict,
    )?;
    if !output.success {
        let detail = output.stderr.trim();
        return Err(format!(
            "{verdict}: exit={:?}; stderr={detail}; receipt={}",
            output.exit_code,
            receipt.display()
        ));
    }
    parsed.map_err(|error| format!("{error}; receipt={}", receipt.display()))
}

#[tauri::command]
pub fn corridor_ui_snapshot() -> Result<Value, String> {
    let repo = resolve_repo_root()?;
    run_corridor_cli(&repo, snapshot_args(), SNAPSHOT_TIMEOUT, "ui-snapshot")
}

#[tauri::command]
pub fn corridor_ui_action(action_id: String, payload: Value) -> Result<Value, String> {
    if !payload.is_object() {
        return Err("BRIDGE_ACTION_PAYLOAD_NOT_OBJECT".to_string());
    }
    let payload_json = serde_json::to_string(&payload)
        .map_err(|error| format!("BRIDGE_ACTION_PAYLOAD_ENCODE_FAILED: {error}"))?;
    let repo = resolve_repo_root()?;
    let operation = format!("ui-action:{action_id}");
    run_corridor_cli(
        &repo,
        action_args(&action_id, &payload_json)?,
        ACTION_TIMEOUT,
        &operation,
    )
}
