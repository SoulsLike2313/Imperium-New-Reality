$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$RootResolver = Join-Path $RepoRoot "ORGAN_AGENT_COMMON/root_resolution.ps1"
. $RootResolver
$RepoRoot = Resolve-NewRealityRoot -RepoRoot $RepoRoot
$Runner = Join-Path $RepoRoot "ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py"
$TransferRoot = if ($env:ADMINISTRATUM_TRANSFER_ROOT) {
    $env:ADMINISTRATUM_TRANSFER_ROOT
} else {
    Join-Path $RepoRoot "RUNS/ADMINISTRATUM_AGENT/ADMINISTRATUM_TRANSFER"
}

Set-Location $RepoRoot
$env:ADMINISTRATUM_TRANSFER_ROOT = $TransferRoot

Write-Host "Administratum-Agent PC launcher"
Write-Host "Repo root: $RepoRoot"
Write-Host "Transfer runtime: $TransferRoot"
Write-Host "Private SSH key is read only from CLI args or IMPERIUM_VM2_SSH_KEY; no key material is stored here."

python $Runner --rich shell
