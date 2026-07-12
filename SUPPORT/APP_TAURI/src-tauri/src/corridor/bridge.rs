use serde_json::Value;
use std::ffi::OsStr;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::{Command, ExitStatus, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const CORRIDOR_MODULE: &str = "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli";
const ROOT_TIMEOUT: Duration = Duration::from_secs(5);
const SNAPSHOT_TIMEOUT: Duration = Duration::from_secs(15);
const ACTION_TIMEOUT: Duration = Duration::from_secs(120);
const MAX_OUTPUT_BYTES: usize = 8 * 1024 * 1024;
const MAX_PAYLOAD_BYTES: usize = 128 * 1024;

#[derive(Clone, Copy)]
enum FixedProgram {
    Git,
    Python,
}

impl FixedProgram {
    fn executable(self) -> &'static str {
        match self {
            Self::Git => "git",
            Self::Python => "python",
        }
    }
}

struct CapturedStream {
    bytes: Vec<u8>,
    truncated: bool,
}

struct FixedOutput {
    status: ExitStatus,
    stdout: String,
    stderr: String,
}

fn read_stream_bounded<R: Read>(mut stream: R) -> io::Result<CapturedStream> {
    let mut bytes = Vec::new();
    let mut truncated = false;
    let mut buffer = [0_u8; 8192];
    loop {
        let count = stream.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        let remaining = MAX_OUTPUT_BYTES.saturating_sub(bytes.len());
        let retained = remaining.min(count);
        bytes.extend_from_slice(&buffer[..retained]);
        truncated |= retained < count;
    }
    Ok(CapturedStream { bytes, truncated })
}

fn join_capture(
    handle: thread::JoinHandle<io::Result<CapturedStream>>,
    name: &str,
) -> Result<CapturedStream, String> {
    handle
        .join()
        .map_err(|_| format!("{name} capture thread panicked"))?
        .map_err(|error| format!("failed to read {name}: {error}"))
}

fn run_fixed<I, S>(
    program: FixedProgram,
    args: I,
    cwd: &Path,
    timeout: Duration,
) -> Result<FixedOutput, String>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    let mut command = Command::new(program.executable());
    command
        .args(args)
        .current_dir(cwd)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if matches!(program, FixedProgram::Python) {
        command
            .env("PYTHONDONTWRITEBYTECODE", "1")
            .env("PYTHONNOUSERSITE", "1");
    }

    let mut child = command.spawn().map_err(|error| {
        format!(
            "failed to start fixed {} command: {error}",
            program.executable()
        )
    })?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "stdout pipe missing".to_string())?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "stderr pipe missing".to_string())?;
    let stdout_reader = thread::spawn(move || read_stream_bounded(stdout));
    let stderr_reader = thread::spawn(move || read_stream_bounded(stderr));

    let deadline = Instant::now() + timeout;
    let status = loop {
        if let Some(status) = child
            .try_wait()
            .map_err(|error| format!("failed to poll fixed command: {error}"))?
        {
            break status;
        }
        if Instant::now() >= deadline {
            let _ = child.kill();
            let _ = child.wait();
            let _ = join_capture(stdout_reader, "stdout");
            let _ = join_capture(stderr_reader, "stderr");
            return Err(format!(
                "fixed {} command exceeded {} seconds",
                program.executable(),
                timeout.as_secs()
            ));
        }
        thread::sleep(Duration::from_millis(20));
    };

    let stdout = join_capture(stdout_reader, "stdout")?;
    let stderr = join_capture(stderr_reader, "stderr")?;
    if stdout.truncated || stderr.truncated {
        return Err(format!(
            "fixed {} command exceeded the {} byte output limit",
            program.executable(),
            MAX_OUTPUT_BYTES
        ));
    }

    Ok(FixedOutput {
        status,
        stdout: String::from_utf8(stdout.bytes)
            .map_err(|_| "fixed command stdout was not UTF-8".to_string())?,
        stderr: String::from_utf8(stderr.bytes)
            .map_err(|_| "fixed command stderr was not UTF-8".to_string())?,
    })
}

fn git_root_from(candidate: &Path) -> Result<PathBuf, String> {
    let output = run_fixed(
        FixedProgram::Git,
        ["rev-parse", "--show-toplevel"],
        candidate,
        ROOT_TIMEOUT,
    )?;
    if !output.status.success() {
        return Err(format!(
            "git root resolution failed: {}",
            output.stderr.trim()
        ));
    }
    let root = PathBuf::from(output.stdout.trim());
    if !root.is_dir() {
        return Err("git returned a non-directory repository root".to_string());
    }
    if !root
        .join("ORGANS")
        .join("MECHANICUS")
        .join("CORE_REFERENCE_CORRIDOR")
        .is_dir()
    {
        return Err("git root does not contain the corridor backend package".to_string());
    }
    Ok(root)
}

fn resolve_repo_root() -> Result<PathBuf, String> {
    let mut candidates = vec![PathBuf::from(env!("CARGO_MANIFEST_DIR"))];
    if let Ok(cwd) = std::env::current_dir() {
        candidates.push(cwd);
    }

    let mut errors = Vec::new();
    for candidate in candidates {
        match git_root_from(&candidate) {
            Ok(root) => return Ok(root),
            Err(error) => errors.push(error),
        }
    }
    Err(format!(
        "corridor repository root is unavailable through git: {}",
        errors.join(" | ")
    ))
}

fn snapshot_args() -> Vec<String> {
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

fn action_args(action_id: &str, payload_json: &str) -> Result<Vec<String>, String> {
    if !valid_action_id(action_id) {
        return Err("corridor action id contains unsupported characters".to_string());
    }
    if payload_json.len() > MAX_PAYLOAD_BYTES {
        return Err(format!(
            "corridor action payload exceeds {} bytes",
            MAX_PAYLOAD_BYTES
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

fn run_corridor_cli(repo: &Path, args: Vec<String>, timeout: Duration) -> Result<Value, String> {
    let output = run_fixed(FixedProgram::Python, args, repo, timeout)?;
    if !output.status.success() {
        let detail = output.stderr.trim();
        return Err(if detail.is_empty() {
            format!("corridor CLI exited with {}", output.status)
        } else {
            format!("corridor CLI exited with {}: {detail}", output.status)
        });
    }
    serde_json::from_str(output.stdout.trim())
        .map_err(|error| format!("corridor CLI returned invalid JSON: {error}"))
}

#[tauri::command]
pub fn corridor_ui_snapshot() -> Result<Value, String> {
    let repo = resolve_repo_root()?;
    run_corridor_cli(&repo, snapshot_args(), SNAPSHOT_TIMEOUT)
}

#[tauri::command]
pub fn corridor_ui_action(action_id: String, payload: Value) -> Result<Value, String> {
    if !payload.is_object() {
        return Err("corridor action payload must be a JSON object".to_string());
    }
    let payload_json = serde_json::to_string(&payload)
        .map_err(|error| format!("failed to encode corridor action payload: {error}"))?;
    let repo = resolve_repo_root()?;
    run_corridor_cli(
        &repo,
        action_args(&action_id, &payload_json)?,
        ACTION_TIMEOUT,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snapshot_argv_is_fixed() {
        assert_eq!(
            snapshot_args(),
            ["-m", CORRIDOR_MODULE, "ui-snapshot"].map(str::to_string)
        );
    }

    #[test]
    fn action_payload_stays_in_one_argv_slot() {
        let payload = r#"{"message":"one; two && three"}"#;
        let args = action_args("diagnostic.run", payload).expect("valid action args");
        assert_eq!(args.len(), 7);
        assert_eq!(args[2], "ui-action");
        assert_eq!(args[4], "diagnostic.run");
        assert_eq!(args[6], payload);
    }

    #[test]
    fn action_id_rejects_shell_syntax() {
        assert!(action_args("diagnostic && whoami", "{}").is_err());
        assert!(action_args("", "{}").is_err());
    }
}
