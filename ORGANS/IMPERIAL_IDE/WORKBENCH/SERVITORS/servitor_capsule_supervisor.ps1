[CmdletBinding()]
param([switch]$Smoke)

$payload = [ordered]@{
    status = if ($Smoke) { 'PASS_WITH_WARNINGS' } else { 'BLOCKED' }
    component = 'SERVITOR_CAPSULE_SUPERVISOR_CANDIDATE'
    persistent_background_daemon = $false
    real_execution_enabled = $false
    process_started = $false
    reason = 'Persistent capsule supervision requires a future owner-approved execution gate.'
}
$payload | ConvertTo-Json
if (-not $Smoke) { exit 2 }
