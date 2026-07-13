use super::windows_job::ProcessJob;
use chrono::{SecondsFormat, Utc};
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::ffi::{OsStr, OsString};
use std::fs::File;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

#[cfg(windows)]
use std::os::windows::process::CommandExt;
#[cfg(windows)]
use windows_sys::Win32::System::Threading::CREATE_NO_WINDOW;

const MAX_OUTPUT_BYTES: usize = 8 * 1024 * 1024;
const MAX_TIMEOUT: Duration = Duration::from_secs(300);
const INHERITED_ENV_KEYS: [&str; 4] = ["SystemRoot", "WINDIR", "TEMP", "TMP"];
const FIXED_ENV_KEYS: [(&str, &str); 5] = [
    ("PYTHONUTF8", "1"),
    ("PYTHONIOENCODING", "utf-8"),
    ("PYTHONDONTWRITEBYTECODE", "1"),
    ("PYTHONNOUSERSITE", "1"),
    ("NO_COLOR", "1"),
];

pub(crate) type MinimalEnvironment = BTreeMap<OsString, OsString>;

#[derive(Clone, Debug)]
pub(crate) struct InterpreterAdmission {
    pub configured_path: PathBuf,
    pub executable_path: PathBuf,
    pub sha256: String,
}

#[derive(Clone, Debug)]
pub(crate) struct ReceiptBinding {
    pub task_id: String,
    pub warp_id: String,
    pub base_head: String,
}

#[derive(Clone, Debug, Serialize)]
pub(crate) struct TerminationProof {
    pub requested: bool,
    pub method: String,
    pub job_assigned: bool,
    pub terminate_succeeded: bool,
    pub job_close_succeeded: bool,
    pub parent_reaped: bool,
    pub tree_terminated: bool,
}

#[derive(Debug)]
pub(crate) struct ProcessOutput {
    pub pid: u32,
    pub success: bool,
    pub exit_code: Option<i32>,
    pub timed_out: bool,
    pub stdout: String,
    pub stderr: String,
    pub stdout_sha256: String,
    pub stderr_sha256: String,
    pub stdout_truncated: bool,
    pub stderr_truncated: bool,
    pub stdout_utf8: bool,
    pub stderr_utf8: bool,
    pub started_at_utc: String,
    pub ended_at_utc: String,
    pub duration_ms: u128,
    pub termination: TerminationProof,
}

struct CapturedStream {
    bytes: Vec<u8>,
    sha256: String,
    truncated: bool,
}

fn hex_digest(bytes: impl AsRef<[u8]>) -> String {
    bytes
        .as_ref()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

pub(crate) fn sha256_file(path: &Path) -> Result<String, String> {
    let mut file =
        File::open(path).map_err(|error| format!("BRIDGE_EXECUTABLE_UNREADABLE: {error}"))?;
    let mut hasher = Sha256::new();
    let mut buffer = [0_u8; 64 * 1024];
    loop {
        let count = file
            .read(&mut buffer)
            .map_err(|error| format!("BRIDGE_EXECUTABLE_HASH_FAILED: {error}"))?;
        if count == 0 {
            break;
        }
        hasher.update(&buffer[..count]);
    }
    Ok(hex_digest(hasher.finalize()))
}

pub(crate) fn admit_interpreter(
    configured_path: &Path,
    expected_sha256: &str,
) -> Result<InterpreterAdmission, String> {
    if !configured_path.is_absolute() {
        return Err("BRIDGE_BARE_OR_RELATIVE_PYTHON_REJECTED".to_string());
    }
    let filename = configured_path
        .file_name()
        .and_then(OsStr::to_str)
        .ok_or_else(|| "BRIDGE_PYTHON_FILENAME_UNKNOWN".to_string())?;
    if !filename.eq_ignore_ascii_case("python.exe") {
        return Err("BRIDGE_NON_PYTHON_EXECUTABLE_REJECTED".to_string());
    }
    if expected_sha256.len() != 64 || !expected_sha256.bytes().all(|byte| byte.is_ascii_hexdigit())
    {
        return Err("BRIDGE_EXECUTABLE_HASH_INVALID".to_string());
    }
    let executable_path = configured_path
        .canonicalize()
        .map_err(|error| format!("BRIDGE_PYTHON_PATH_UNAVAILABLE: {error}"))?;
    if !executable_path.is_file() {
        return Err("BRIDGE_PYTHON_PATH_NOT_FILE".to_string());
    }
    let actual_sha256 = sha256_file(&executable_path)?;
    if !actual_sha256.eq_ignore_ascii_case(expected_sha256) {
        return Err("BRIDGE_EXECUTABLE_HASH_MISMATCH".to_string());
    }
    Ok(InterpreterAdmission {
        configured_path: configured_path.to_path_buf(),
        executable_path,
        sha256: actual_sha256,
    })
}

fn find_environment_value(parent: &MinimalEnvironment, requested: &str) -> Option<OsString> {
    parent.iter().find_map(|(key, value)| {
        key.to_str()
            .filter(|name| name.eq_ignore_ascii_case(requested))
            .map(|_| value.clone())
    })
}

pub(crate) fn minimal_environment(
    parent: &MinimalEnvironment,
    worktree: &Path,
) -> Result<MinimalEnvironment, String> {
    let worktree = worktree
        .canonicalize()
        .map_err(|error| format!("BRIDGE_WORKTREE_UNAVAILABLE: {error}"))?;
    let mut environment = MinimalEnvironment::new();
    for key in INHERITED_ENV_KEYS {
        if let Some(value) = find_environment_value(parent, key) {
            environment.insert(OsString::from(key), value);
        }
    }
    let windows_root = environment
        .get(OsStr::new("SystemRoot"))
        .cloned()
        .or_else(|| environment.get(OsStr::new("WINDIR")).cloned())
        .ok_or_else(|| "BRIDGE_SYSTEM_ROOT_NOT_ADMITTED".to_string())?;
    environment
        .entry(OsString::from("SystemRoot"))
        .or_insert_with(|| windows_root.clone());
    environment
        .entry(OsString::from("WINDIR"))
        .or_insert(windows_root);
    let temp = std::env::temp_dir().into_os_string();
    environment
        .entry(OsString::from("TEMP"))
        .or_insert_with(|| temp.clone());
    environment.entry(OsString::from("TMP")).or_insert(temp);
    for (key, value) in FIXED_ENV_KEYS {
        environment.insert(OsString::from(key), OsString::from(value));
    }
    environment.insert(
        OsString::from("IMPERIUM_ACTIVE_WORKTREE"),
        worktree.into_os_string(),
    );
    Ok(environment)
}

pub(crate) fn environment_key_names(
    environment: &MinimalEnvironment,
) -> Result<Vec<String>, String> {
    let allowed: Vec<&str> = INHERITED_ENV_KEYS
        .into_iter()
        .chain(FIXED_ENV_KEYS.into_iter().map(|(key, _)| key))
        .chain(std::iter::once("IMPERIUM_ACTIVE_WORKTREE"))
        .collect();
    let mut names = Vec::new();
    for key in environment.keys() {
        let name = key
            .to_str()
            .ok_or_else(|| "BRIDGE_ENVIRONMENT_KEY_NOT_UTF8".to_string())?;
        if !allowed.iter().any(|allowed| name == *allowed) {
            return Err(format!("BRIDGE_ENVIRONMENT_KEY_NOT_ADMITTED: {name}"));
        }
        names.push(name.to_string());
    }
    names.sort();
    Ok(names)
}

fn read_stream_bounded<R: Read>(mut stream: R) -> io::Result<CapturedStream> {
    let mut bytes = Vec::new();
    let mut hasher = Sha256::new();
    let mut truncated = false;
    let mut buffer = [0_u8; 8192];
    loop {
        let count = stream.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        hasher.update(&buffer[..count]);
        let remaining = MAX_OUTPUT_BYTES.saturating_sub(bytes.len());
        let retained = remaining.min(count);
        bytes.extend_from_slice(&buffer[..retained]);
        truncated |= retained < count;
    }
    Ok(CapturedStream {
        bytes,
        sha256: hex_digest(hasher.finalize()),
        truncated,
    })
}

fn join_capture(
    handle: thread::JoinHandle<io::Result<CapturedStream>>,
    name: &str,
) -> Result<CapturedStream, String> {
    handle
        .join()
        .map_err(|_| format!("BRIDGE_{name}_CAPTURE_THREAD_PANICKED"))?
        .map_err(|error| format!("BRIDGE_{name}_CAPTURE_FAILED: {error}"))
}

fn wait_child_bounded(
    child: &mut std::process::Child,
    timeout: Duration,
) -> Option<std::process::ExitStatus> {
    let deadline = Instant::now() + timeout;
    loop {
        match child.try_wait() {
            Ok(Some(status)) => return Some(status),
            Ok(None) if Instant::now() < deadline => {
                thread::sleep(Duration::from_millis(10));
            }
            _ => return None,
        }
    }
}

pub(crate) fn execute_python(
    admission: &InterpreterAdmission,
    args: &[OsString],
    cwd: &Path,
    allowed_cwd: &Path,
    environment: &MinimalEnvironment,
    timeout: Duration,
) -> Result<ProcessOutput, String> {
    if timeout.is_zero() || timeout > MAX_TIMEOUT {
        return Err("BRIDGE_TIMEOUT_NOT_ADMITTED".to_string());
    }
    if sha256_file(&admission.executable_path)? != admission.sha256 {
        return Err("BRIDGE_EXECUTABLE_HASH_CHANGED_BEFORE_SPAWN".to_string());
    }
    let cwd = cwd
        .canonicalize()
        .map_err(|error| format!("BRIDGE_CWD_UNAVAILABLE: {error}"))?;
    let allowed_cwd = allowed_cwd
        .canonicalize()
        .map_err(|error| format!("BRIDGE_ALLOWED_CWD_UNAVAILABLE: {error}"))?;
    if cwd != allowed_cwd {
        return Err("BRIDGE_CWD_ESCAPE_REJECTED".to_string());
    }
    let _environment_keys = environment_key_names(environment)?;
    let mut job = ProcessJob::new()?;
    let mut command = Command::new(&admission.executable_path);
    command
        .args(args)
        .current_dir(&cwd)
        .env_clear()
        .envs(environment)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(windows)]
    command.creation_flags(CREATE_NO_WINDOW);

    let started_at_utc = Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true);
    let started = Instant::now();
    let mut child = command
        .spawn()
        .map_err(|error| format!("BRIDGE_PYTHON_SPAWN_FAILED: {error}"))?;
    if let Err(error) = job.assign(&child) {
        let _ = child.kill();
        let _ = child.wait();
        let _ = job.close();
        return Err(error);
    }
    let pid = child.id();
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "BRIDGE_STDOUT_PIPE_MISSING".to_string())?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "BRIDGE_STDERR_PIPE_MISSING".to_string())?;
    let stdout_reader = thread::spawn(move || read_stream_bounded(stdout));
    let stderr_reader = thread::spawn(move || read_stream_bounded(stderr));

    let deadline = Instant::now() + timeout;
    let mut timed_out = false;
    let mut timeout_terminate_succeeded = true;
    let mut status = loop {
        match child.try_wait() {
            Ok(Some(status)) => break Some(status),
            Ok(None) if Instant::now() >= deadline => {
                timed_out = true;
                timeout_terminate_succeeded = job.terminate();
                break None;
            }
            Ok(None) => thread::sleep(Duration::from_millis(10)),
            Err(error) => {
                let _ = job.terminate();
                let _ = job.close();
                let _ = child.kill();
                let _ = wait_child_bounded(&mut child, Duration::from_secs(2));
                return Err(format!("BRIDGE_PROCESS_POLL_FAILED: {error}"));
            }
        }
    };

    let terminate_succeeded = if timed_out {
        timeout_terminate_succeeded
    } else {
        true
    };
    let job_close_succeeded = job.close();
    if timed_out {
        status = wait_child_bounded(&mut child, Duration::from_secs(5));
        if status.is_none() {
            let _ = child.kill();
            status = wait_child_bounded(&mut child, Duration::from_secs(2));
        }
    }
    let parent_reaped = status.is_some();
    let tree_terminated = terminate_succeeded && parent_reaped && job_close_succeeded;
    let termination = TerminationProof {
        requested: timed_out,
        method: if timed_out {
            "WINDOWS_JOB_OBJECT_TERMINATE".to_string()
        } else {
            "WINDOWS_JOB_OBJECT_CLOSE_KILL_REMAINDER".to_string()
        },
        job_assigned: true,
        terminate_succeeded,
        job_close_succeeded,
        parent_reaped,
        tree_terminated,
    };
    let stdout = join_capture(stdout_reader, "STDOUT")?;
    let stderr = join_capture(stderr_reader, "STDERR")?;
    let stdout_text = String::from_utf8(stdout.bytes.clone());
    let stderr_text = String::from_utf8(stderr.bytes.clone());
    let stdout_utf8 = stdout_text.is_ok();
    let stderr_utf8 = stderr_text.is_ok();
    let exit_success = status.as_ref().is_some_and(|value| value.success());
    let success = exit_success
        && !timed_out
        && !stdout.truncated
        && !stderr.truncated
        && stdout_utf8
        && stderr_utf8
        && tree_terminated;
    Ok(ProcessOutput {
        pid,
        success,
        exit_code: status.and_then(|value| value.code()),
        timed_out,
        stdout: stdout_text
            .unwrap_or_else(|error| String::from_utf8_lossy(error.as_bytes()).into_owned()),
        stderr: stderr_text
            .unwrap_or_else(|error| String::from_utf8_lossy(error.as_bytes()).into_owned()),
        stdout_sha256: stdout.sha256,
        stderr_sha256: stderr.sha256,
        stdout_truncated: stdout.truncated,
        stderr_truncated: stderr.truncated,
        stdout_utf8,
        stderr_utf8,
        started_at_utc,
        ended_at_utc: Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true),
        duration_ms: started.elapsed().as_millis(),
        termination,
    })
}
