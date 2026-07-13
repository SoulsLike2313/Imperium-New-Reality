use std::io;

#[cfg(windows)]
use std::os::windows::io::AsRawHandle;
#[cfg(windows)]
use windows_sys::Win32::Foundation::{CloseHandle, HANDLE};
#[cfg(windows)]
use windows_sys::Win32::System::JobObjects::{
    AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
    SetInformationJobObject, TerminateJobObject, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
};

const TIMEOUT_EXIT_CODE: u32 = 0xE000_0004;

#[cfg(windows)]
pub(crate) struct ProcessJob {
    handle: HANDLE,
}

#[cfg(not(windows))]
pub(crate) struct ProcessJob;

#[cfg(windows)]
impl ProcessJob {
    pub(crate) fn new() -> Result<Self, String> {
        let handle = unsafe { CreateJobObjectW(std::ptr::null(), std::ptr::null()) };
        if handle.is_null() {
            return Err(format!(
                "BRIDGE_JOB_CREATE_FAILED: {}",
                io::Error::last_os_error()
            ));
        }
        let mut limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION::default();
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        let configured = unsafe {
            SetInformationJobObject(
                handle,
                JobObjectExtendedLimitInformation,
                &limits as *const _ as *const core::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            )
        };
        if configured == 0 {
            let error = io::Error::last_os_error();
            unsafe { CloseHandle(handle) };
            return Err(format!("BRIDGE_JOB_CONFIGURE_FAILED: {error}"));
        }
        Ok(Self { handle })
    }

    pub(crate) fn assign(&self, child: &std::process::Child) -> Result<(), String> {
        let process_handle = child.as_raw_handle() as HANDLE;
        if unsafe { AssignProcessToJobObject(self.handle, process_handle) } == 0 {
            return Err(format!(
                "BRIDGE_JOB_ASSIGN_FAILED: {}",
                io::Error::last_os_error()
            ));
        }
        Ok(())
    }

    pub(crate) fn terminate(&self) -> bool {
        unsafe { TerminateJobObject(self.handle, TIMEOUT_EXIT_CODE) != 0 }
    }

    pub(crate) fn close(&mut self) -> bool {
        if self.handle.is_null() {
            return true;
        }
        let handle = std::mem::replace(&mut self.handle, std::ptr::null_mut());
        unsafe { CloseHandle(handle) != 0 }
    }
}

#[cfg(windows)]
impl Drop for ProcessJob {
    fn drop(&mut self) {
        let _ = self.close();
    }
}

#[cfg(not(windows))]
impl ProcessJob {
    pub(crate) fn new() -> Result<Self, String> {
        Err("BRIDGE_WINDOWS_JOB_OBJECT_REQUIRED".to_string())
    }

    pub(crate) fn assign(&self, _child: &std::process::Child) -> Result<(), String> {
        Err("BRIDGE_WINDOWS_JOB_OBJECT_REQUIRED".to_string())
    }

    pub(crate) fn terminate(&self) -> bool {
        false
    }

    pub(crate) fn close(&mut self) -> bool {
        false
    }
}
