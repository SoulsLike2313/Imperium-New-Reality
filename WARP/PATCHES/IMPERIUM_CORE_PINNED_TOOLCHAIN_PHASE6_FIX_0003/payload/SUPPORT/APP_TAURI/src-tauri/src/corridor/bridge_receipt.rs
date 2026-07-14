use super::process_boundary::{
    environment_key_names, InterpreterAdmission, MinimalEnvironment, ProcessOutput, ReceiptBinding,
    TerminationProof,
};
use chrono::Utc;
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::ffi::OsString;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

static RECEIPT_SEQUENCE: AtomicU64 = AtomicU64::new(1);

fn hex_digest(bytes: impl AsRef<[u8]>) -> String {
    bytes
        .as_ref()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

#[derive(Serialize)]
struct ReceiptInterpreter {
    configured_path: String,
    admitted_absolute_path: String,
    sha256: String,
}

#[derive(Serialize)]
struct ReceiptEnvironment {
    profile_id: &'static str,
    admitted_keys: Vec<String>,
    path_inherited: bool,
    secret_values_recorded: bool,
}

#[derive(Serialize)]
struct ReceiptProcess {
    pid: u32,
    exit_code: Option<i32>,
    timed_out: bool,
    stdout_sha256: String,
    stderr_sha256: String,
    stdout_truncated: bool,
    stderr_truncated: bool,
    stdout_utf8: bool,
    stderr_utf8: bool,
    started_at_utc: String,
    ended_at_utc: String,
    duration_ms: u128,
    termination: TerminationProof,
}

#[derive(Serialize)]
struct ReceiptBody {
    schema_version: &'static str,
    receipt_id: String,
    task_id: String,
    warp_id: String,
    base_head: String,
    operation: String,
    interpreter: ReceiptInterpreter,
    exact_argv: Vec<String>,
    shell: bool,
    cwd: String,
    environment: ReceiptEnvironment,
    timeout_seconds: f64,
    process: ReceiptProcess,
    verdict: String,
}

pub(crate) fn write_bridge_receipt(
    receipt_dir: &Path,
    binding: &ReceiptBinding,
    operation: &str,
    admission: &InterpreterAdmission,
    args: &[OsString],
    cwd: &Path,
    environment: &MinimalEnvironment,
    timeout: Duration,
    output: &ProcessOutput,
    verdict: &str,
) -> Result<PathBuf, String> {
    if binding.task_id.is_empty()
        || binding.warp_id.is_empty()
        || binding.base_head.len() != 40
        || !binding
            .base_head
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        return Err("BRIDGE_RECEIPT_BINDING_INVALID".to_string());
    }
    if operation.is_empty() || !(verdict == "PASS_PROVEN" || verdict.starts_with("BLOCK_")) {
        return Err("BRIDGE_RECEIPT_VERDICT_OR_OPERATION_INVALID".to_string());
    }
    let mut exact_argv = vec![admission
        .executable_path
        .to_str()
        .ok_or_else(|| "BRIDGE_EXECUTABLE_PATH_NOT_UTF8".to_string())?
        .to_string()];
    for arg in args {
        exact_argv.push(
            arg.to_str()
                .ok_or_else(|| "BRIDGE_ARG_NOT_UTF8".to_string())?
                .to_string(),
        );
    }
    let sequence = RECEIPT_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    let receipt_id = format!(
        "PHASE4-BRIDGE-{}-{}-{}",
        Utc::now().timestamp_millis(),
        std::process::id(),
        sequence
    );
    let body = ReceiptBody {
        schema_version: "imperium.core_reference_corridor.rust_python_bridge_receipt.v1",
        receipt_id: receipt_id.clone(),
        task_id: binding.task_id.clone(),
        warp_id: binding.warp_id.clone(),
        base_head: binding.base_head.clone(),
        operation: operation.to_string(),
        interpreter: ReceiptInterpreter {
            configured_path: admission.configured_path.to_string_lossy().into_owned(),
            admitted_absolute_path: admission.executable_path.to_string_lossy().into_owned(),
            sha256: admission.sha256.clone(),
        },
        exact_argv,
        shell: false,
        cwd: cwd
            .canonicalize()
            .map_err(|error| format!("BRIDGE_RECEIPT_CWD_UNAVAILABLE: {error}"))?
            .to_string_lossy()
            .into_owned(),
        environment: ReceiptEnvironment {
            profile_id: "RUST_PYTHON_BRIDGE_MINIMAL_ENV_V2",
            admitted_keys: environment_key_names(environment)?,
            path_inherited: false,
            secret_values_recorded: false,
        },
        timeout_seconds: timeout.as_secs_f64(),
        process: ReceiptProcess {
            pid: output.pid,
            exit_code: output.exit_code,
            timed_out: output.timed_out,
            stdout_sha256: format!("sha256:{}", output.stdout_sha256),
            stderr_sha256: format!("sha256:{}", output.stderr_sha256),
            stdout_truncated: output.stdout_truncated,
            stderr_truncated: output.stderr_truncated,
            stdout_utf8: output.stdout_utf8,
            stderr_utf8: output.stderr_utf8,
            started_at_utc: output.started_at_utc.clone(),
            ended_at_utc: output.ended_at_utc.clone(),
            duration_ms: output.duration_ms,
            termination: output.termination.clone(),
        },
        verdict: verdict.to_string(),
    };
    let mut value = serde_json::to_value(&body)
        .map_err(|error| format!("BRIDGE_RECEIPT_SERIALIZE_FAILED: {error}"))?;
    let body_bytes = serde_json::to_vec(&value)
        .map_err(|error| format!("BRIDGE_RECEIPT_SERIALIZE_FAILED: {error}"))?;
    let receipt_hash = format!("sha256:{}", hex_digest(Sha256::digest(&body_bytes)));
    value
        .as_object_mut()
        .ok_or_else(|| "BRIDGE_RECEIPT_NOT_OBJECT".to_string())?
        .insert(
            "receipt_hash".to_string(),
            serde_json::Value::String(receipt_hash),
        );
    let mut bytes = serde_json::to_vec_pretty(&value)
        .map_err(|error| format!("BRIDGE_RECEIPT_SERIALIZE_FAILED: {error}"))?;
    bytes.push(b'\n');
    fs::create_dir_all(receipt_dir)
        .map_err(|error| format!("BRIDGE_RECEIPT_DIRECTORY_FAILED: {error}"))?;
    let final_path = receipt_dir.join(format!("{receipt_id}.json"));
    let temp_path = receipt_dir.join(format!(".{receipt_id}.tmp"));
    let write_result = (|| -> Result<(), String> {
        let mut file = OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(&temp_path)
            .map_err(|error| format!("BRIDGE_RECEIPT_CREATE_FAILED: {error}"))?;
        file.write_all(&bytes)
            .and_then(|_| file.sync_all())
            .map_err(|error| format!("BRIDGE_RECEIPT_WRITE_FAILED: {error}"))?;
        fs::rename(&temp_path, &final_path)
            .map_err(|error| format!("BRIDGE_RECEIPT_COMMIT_FAILED: {error}"))?;
        Ok(())
    })();
    if write_result.is_err() {
        let _ = fs::remove_file(&temp_path);
    }
    write_result?;
    Ok(final_path)
}
