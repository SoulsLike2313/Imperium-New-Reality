use super::bridge::{action_args, load_bridge_context, resolve_repo_root, snapshot_args};
use super::bridge_receipt::write_bridge_receipt;
use super::process_boundary::{
    admit_interpreter, execute_python, minimal_environment, sha256_file, MinimalEnvironment,
};
use sha2::{Digest, Sha256};
use std::ffi::{OsStr, OsString};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::Duration;

static TEST_SEQUENCE: AtomicU64 = AtomicU64::new(1);

struct TestDirectory {
    path: PathBuf,
}

impl TestDirectory {
    fn new(label: &str) -> Self {
        let sequence = TEST_SEQUENCE.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "imperium-phase4-{label}-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir_all(&path).expect("create Phase 4 test directory");
        Self { path }
    }
}

impl Drop for TestDirectory {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.path);
    }
}

fn host_environment() -> MinimalEnvironment {
    std::env::vars_os().collect()
}

fn context_and_environment() -> (super::bridge::BridgeContext, MinimalEnvironment) {
    let root = resolve_repo_root().expect("compile-time repository root");
    let context = load_bridge_context(&root).expect("admitted bridge context");
    let environment =
        minimal_environment(&host_environment(), &context.repo).expect("minimal environment");
    (context, environment)
}

fn args(values: &[&str]) -> Vec<OsString> {
    values.iter().map(OsString::from).collect()
}

fn execute_code(code: &str, extra: &[OsString]) -> super::process_boundary::ProcessOutput {
    let (context, environment) = context_and_environment();
    let mut argv = args(&["-c", code]);
    argv.extend_from_slice(extra);
    execute_python(
        &context.admission,
        &argv,
        &context.repo,
        &context.repo,
        &environment,
        Duration::from_secs(10),
    )
    .expect("admitted Python execution")
}

#[cfg(windows)]
fn process_is_terminated(pid: u32) -> bool {
    use windows_sys::Win32::Foundation::{CloseHandle, WAIT_OBJECT_0};
    use windows_sys::Win32::System::Threading::{
        OpenProcess, WaitForSingleObject, PROCESS_SYNCHRONIZE,
    };
    let handle = unsafe { OpenProcess(PROCESS_SYNCHRONIZE, 0, pid) };
    if handle.is_null() {
        return true;
    }
    let result = unsafe { WaitForSingleObject(handle, 0) };
    unsafe { CloseHandle(handle) };
    result == WAIT_OBJECT_0
}

#[test]
fn phase4_01_admitted_absolute_python_works() {
    let (context, environment) = context_and_environment();
    assert!(context.admission.configured_path.is_absolute());
    assert!(context.admission.executable_path.is_absolute());
    assert_eq!(
        context
            .admission
            .executable_path
            .file_name()
            .and_then(OsStr::to_str),
        Some("python.exe")
    );
    let output = execute_python(
        &context.admission,
        &args(&["-c", "print('ADMITTED_ABSOLUTE_PYTHON')"]),
        &context.repo,
        &context.repo,
        &environment,
        Duration::from_secs(10),
    )
    .expect("absolute Python executes");
    assert!(output.success, "{}", output.stderr);
    assert_eq!(output.stdout.trim(), "ADMITTED_ABSOLUTE_PYTHON");
}

#[test]
fn phase4_02_bare_python_is_rejected() {
    let error = admit_interpreter(Path::new("python"), &"0".repeat(64))
        .expect_err("bare Python must fail closed");
    assert!(error.contains("BARE_OR_RELATIVE_PYTHON_REJECTED"));
}

#[test]
fn phase4_03_path_hijack_is_rejected() {
    let temp = TestDirectory::new("path-hijack");
    let fake = temp.path.join("python.exe");
    fs::write(&fake, b"not an interpreter").expect("write fake Python");
    let mut parent = host_environment();
    parent.insert(OsString::from("PATH"), temp.path.clone().into_os_string());
    let root = resolve_repo_root().expect("repository root");
    let environment = minimal_environment(&parent, &root).expect("minimal environment");

    assert!(!environment.contains_key(OsStr::new("PATH")));
    let error = admit_interpreter(Path::new("python.exe"), &"0".repeat(64))
        .expect_err("PATH-resolved Python must fail closed");
    assert!(error.contains("BARE_OR_RELATIVE_PYTHON_REJECTED"));
}

#[test]
fn phase4_04_executable_hash_mismatch_is_rejected() {
    let root = resolve_repo_root().expect("repository root");
    let context = load_bridge_context(&root).expect("bridge context");
    let error = admit_interpreter(&context.admission.configured_path, &"0".repeat(64))
        .expect_err("wrong executable hash must fail closed");
    assert!(error.contains("EXECUTABLE_HASH_MISMATCH"));
}

#[test]
fn phase4_05_cwd_escape_is_rejected_before_spawn() {
    let (context, environment) = context_and_environment();
    let escaped = TestDirectory::new("cwd-escape");
    let marker = escaped.path.join("should-not-exist.txt");
    let code = format!(
        "from pathlib import Path; Path({:?}).write_text('spawned')",
        marker.to_string_lossy()
    );
    let error = execute_python(
        &context.admission,
        &args(&["-c", &code]),
        &escaped.path,
        &context.repo,
        &environment,
        Duration::from_secs(10),
    )
    .expect_err("cwd escape must fail before process start");
    assert!(error.contains("CWD_ESCAPE_REJECTED"));
    assert!(!marker.exists());
}

#[test]
fn phase4_06_shell_metacharacters_remain_inert_argv() {
    let metacharacters = "one; & whoami | Write-Output PWNED && two";
    let output = execute_code(
        "import json,sys; print(json.dumps(sys.argv[1]))",
        &[OsString::from(metacharacters)],
    );
    assert!(output.success, "{}", output.stderr);
    let observed: String = serde_json::from_str(output.stdout.trim()).expect("JSON string");
    assert_eq!(observed, metacharacters);
    assert!(!output.stdout.contains("PWNED\n"));
}

#[test]
fn phase4_07_secret_like_environment_variables_are_excluded() {
    let root = resolve_repo_root().expect("repository root");
    let context = load_bridge_context(&root).expect("bridge context");
    let mut parent = host_environment();
    parent.insert(
        OsString::from("AWS_SECRET_ACCESS_KEY"),
        OsString::from("must-not-cross-boundary"),
    );
    parent.insert(
        OsString::from("GITHUB_TOKEN"),
        OsString::from("must-not-cross-boundary"),
    );
    let environment = minimal_environment(&parent, &context.repo).expect("minimal environment");
    assert!(!environment.contains_key(OsStr::new("AWS_SECRET_ACCESS_KEY")));
    assert!(!environment.contains_key(OsStr::new("GITHUB_TOKEN")));
    assert!(!environment.contains_key(OsStr::new("PATH")));
    let output = execute_python(
        &context.admission,
        &args(&[
            "-c",
            "import os,json; print(json.dumps({'aws':os.getenv('AWS_SECRET_ACCESS_KEY'),'github':os.getenv('GITHUB_TOKEN'),'path':os.getenv('PATH')}))",
        ]),
        &context.repo,
        &context.repo,
        &environment,
        Duration::from_secs(10),
    )
    .expect("minimal-environment execution");
    assert!(output.success, "{}", output.stderr);
    let observed: serde_json::Value =
        serde_json::from_str(output.stdout.trim()).expect("environment JSON");
    assert_eq!(
        observed,
        serde_json::json!({"aws": null, "github": null, "path": null})
    );
}

#[test]
fn phase4_08_stdout_and_stderr_are_captured_separately() {
    let output = execute_code(
        "import sys; sys.stdout.write('STDOUT_ONLY'); sys.stderr.write('STDERR_ONLY')",
        &[],
    );
    assert!(output.success);
    assert_eq!(output.stdout, "STDOUT_ONLY");
    assert_eq!(output.stderr, "STDERR_ONLY");
    assert_ne!(output.stdout_sha256, output.stderr_sha256);
}

#[cfg(windows)]
#[test]
fn phase4_09_timeout_kills_parent_child_and_grandchild() {
    let temp = TestDirectory::new("tree-kill");
    let parent_marker = temp.path.join("parent.pid");
    let child_marker = temp.path.join("child.pid");
    let grandchild_marker = temp.path.join("grandchild.pid");
    let grandchild_code = "import os,pathlib,sys,time; pathlib.Path(sys.argv[1]).write_text(str(os.getpid()),encoding='utf-8'); time.sleep(60)";
    let child_code = "import os,pathlib,subprocess,sys,time; pathlib.Path(sys.argv[1]).write_text(str(os.getpid()),encoding='utf-8'); subprocess.Popen([sys.executable,'-c',sys.argv[3],sys.argv[2]]); deadline=time.time()+2.5; marker=pathlib.Path(sys.argv[2]);\nwhile not marker.exists() and time.time()<deadline: time.sleep(0.01)\ntime.sleep(60)";
    let parent_code = "import os,pathlib,subprocess,sys,time; pathlib.Path(sys.argv[1]).write_text(str(os.getpid()),encoding='utf-8'); subprocess.Popen([sys.executable,'-c',sys.argv[4],sys.argv[2],sys.argv[3],sys.argv[5]]); deadline=time.time()+2.5; marker=pathlib.Path(sys.argv[3]);\nwhile not marker.exists() and time.time()<deadline: time.sleep(0.01)\nprint('TREE_READY',flush=True); time.sleep(60)";
    let (context, environment) = context_and_environment();
    let argv = vec![
        OsString::from("-c"),
        OsString::from(parent_code),
        parent_marker.clone().into_os_string(),
        child_marker.clone().into_os_string(),
        grandchild_marker.clone().into_os_string(),
        OsString::from(child_code),
        OsString::from(grandchild_code),
    ];
    let output = execute_python(
        &context.admission,
        &argv,
        &context.repo,
        &context.repo,
        &environment,
        Duration::from_secs(4),
    )
    .expect("timed process returns bounded output");
    assert!(output.timed_out);
    assert!(output.termination.job_assigned);
    assert!(output.termination.terminate_succeeded);
    assert!(output.termination.tree_terminated);
    assert!(
        parent_marker.is_file(),
        "parent marker missing: {}",
        output.stderr
    );
    assert!(
        child_marker.is_file(),
        "child marker missing: {}",
        output.stderr
    );
    assert!(
        grandchild_marker.is_file(),
        "grandchild marker missing: {}",
        output.stderr
    );
    let pids: Vec<u32> = [&parent_marker, &child_marker, &grandchild_marker]
        .iter()
        .map(|path| {
            fs::read_to_string(path)
                .expect("pid marker")
                .parse()
                .expect("numeric pid")
        })
        .collect();
    for _ in 0..100 {
        if pids.iter().all(|pid| process_is_terminated(*pid)) {
            break;
        }
        thread::sleep(Duration::from_millis(20));
    }
    assert!(
        pids.iter().all(|pid| process_is_terminated(*pid)),
        "surviving process in parent/child/grandchild chain: {pids:?}"
    );
}

#[test]
fn phase4_10_bridge_receipt_has_task_warp_and_base_bindings() {
    let temp = TestDirectory::new("receipt");
    let (context, environment) = context_and_environment();
    let argv = args(&["-c", "print('{}')"]);
    let output = execute_python(
        &context.admission,
        &argv,
        &context.repo,
        &context.repo,
        &environment,
        Duration::from_secs(10),
    )
    .expect("receipt process");
    assert!(output.success, "{}", output.stderr);
    let receipt_path = write_bridge_receipt(
        &temp.path,
        &context.binding,
        "phase4-test",
        &context.admission,
        &argv,
        &context.repo,
        &environment,
        Duration::from_secs(10),
        &output,
        "PASS_PROVEN",
    )
    .expect("write bridge receipt");
    let mut receipt: serde_json::Value =
        serde_json::from_slice(&fs::read(&receipt_path).expect("read bridge receipt"))
            .expect("parse bridge receipt");
    assert_eq!(receipt["task_id"], "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001");
    assert_eq!(receipt["warp_id"], "WARP-CORE-REFERENCE-0001");
    assert_eq!(
        receipt["base_head"],
        "281c3a7c8463de7fb64473929fe0ed975f99f595"
    );
    assert_eq!(receipt["shell"], false);
    assert_eq!(receipt["environment"]["path_inherited"], false);
    assert_eq!(receipt["environment"]["secret_values_recorded"], false);
    assert_eq!(receipt["process"]["termination"]["tree_terminated"], true);
    assert_eq!(receipt["verdict"], "PASS_PROVEN");
    let stored_hash = receipt
        .as_object_mut()
        .expect("receipt object")
        .remove("receipt_hash")
        .and_then(|value| value.as_str().map(str::to_string))
        .expect("receipt hash");
    let body = serde_json::to_vec(&receipt).expect("canonical receipt body");
    let actual_hash = format!(
        "sha256:{}",
        Sha256::digest(body)
            .iter()
            .map(|byte| format!("{byte:02x}"))
            .collect::<String>()
    );
    assert_eq!(stored_hash, actual_hash);
}

#[test]
fn snapshot_argv_is_fixed() {
    assert_eq!(
        snapshot_args(),
        [
            "-m",
            "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli",
            "ui-snapshot",
        ]
        .map(str::to_string)
    );
}

#[test]
fn action_payload_stays_in_one_argv_slot() {
    let payload = r#"{"message":"one; two && three"}"#;
    let argv = action_args("diagnostic.run", payload).expect("valid action args");
    assert_eq!(argv.len(), 7);
    assert_eq!(argv[2], "ui-action");
    assert_eq!(argv[4], "diagnostic.run");
    assert_eq!(argv[6], payload);
}

#[test]
fn action_id_rejects_shell_syntax() {
    assert!(action_args("diagnostic && whoami", "{}").is_err());
    assert!(action_args("", "{}").is_err());
}

#[test]
fn read_only_diagnostic_uses_the_fixed_corridor_action_route() {
    let argv = action_args("run_core_diagnostic", "{}").expect("diagnostic route");
    assert_eq!(argv[2], "ui-action");
    assert_eq!(argv[4], "run_core_diagnostic");
    assert_eq!(argv[6], "{}");
}

#[test]
fn admitted_interpreter_hash_matches_current_file() {
    let (context, _) = context_and_environment();
    assert_eq!(
        sha256_file(&context.admission.executable_path).expect("interpreter hash"),
        context.admission.sha256
    );
}
