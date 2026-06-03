Set-StrictMode -Version Latest

$script:NewRealityRoot = [System.IO.Path]::GetFullPath("E:\IMPERIUM_NEW_GENERATION_NEW_REALITY")
$script:AncientEmpireRoot = [System.IO.Path]::GetFullPath("E:\IMPERIUM")
$script:MarkerFiles = @("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")

function Normalize-RootPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
}

function Test-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )
    $resolvedPath = Normalize-RootPath $Path
    $resolvedRoot = Normalize-RootPath $Root
    return ($resolvedPath -eq $resolvedRoot) -or $resolvedPath.StartsWith($resolvedRoot + [System.IO.Path]::DirectorySeparatorChar)
}

function Test-NewRealityRoot {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $resolved = Normalize-RootPath $RepoRoot
    if ($resolved -eq (Normalize-RootPath $script:AncientEmpireRoot)) {
        throw "Ancient Empire root is not an active New Reality root: $resolved"
    }
    if (-not (Test-PathUnderRoot -Path $resolved -Root $script:NewRealityRoot)) {
        throw "Root is outside New Reality boundary: $resolved"
    }
    foreach ($marker in $script:MarkerFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $resolved $marker) -PathType Leaf)) {
            throw "Root is missing required marker file: $marker"
        }
    }
    $epochPath = Join-Path $resolved "EPOCH_MANIFEST.json"
    $epoch = Get-Content -Raw -Encoding UTF8 -LiteralPath $epochPath | ConvertFrom-Json
    if ([string]$epoch.epoch -ne "NEW_REALITY") {
        throw "Epoch manifest does not declare NEW_REALITY"
    }
    if ($epoch.active_root) {
        $declared = Normalize-RootPath ([string]$epoch.active_root)
        if ($declared -ne $resolved) {
            throw "Epoch manifest active_root mismatch: $declared != $resolved"
        }
    }
    return $resolved
}

function Find-NewRealityRoot {
    param([string]$StartPath = (Get-Location).Path)

    $cursor = Get-Item -LiteralPath $StartPath -ErrorAction Stop
    if (-not $cursor.PSIsContainer) {
        $cursor = $cursor.Directory
    }
    while ($null -ne $cursor) {
        $candidate = $cursor.FullName
        $allMarkers = $true
        foreach ($marker in $script:MarkerFiles) {
            if (-not (Test-Path -LiteralPath (Join-Path $candidate $marker) -PathType Leaf)) {
                $allMarkers = $false
                break
            }
        }
        if ($allMarkers) {
            return Test-NewRealityRoot -RepoRoot $candidate
        }
        $cursor = $cursor.Parent
    }
    throw "Could not discover New Reality root from $StartPath"
}

function Resolve-NewRealityRoot {
    param(
        [string]$RepoRoot = "",
        [string]$StartPath = (Get-Location).Path
    )

    if ($RepoRoot) {
        return Test-NewRealityRoot -RepoRoot $RepoRoot
    }
    if ($env:IMPERIUM_NEW_REALITY_ROOT) {
        return Test-NewRealityRoot -RepoRoot $env:IMPERIUM_NEW_REALITY_ROOT
    }
    return Find-NewRealityRoot -StartPath $StartPath
}

function Test-GitFieldSanity {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $text = $Value.Trim()
    if (-not $text) {
        return $false
    }
    if ($text -match "[`r`n]") {
        return $false
    }
    if ($text -match "(?i)(usage:|options:|show this help|fatal:|error:|powershell|parameter)") {
        return $false
    }
    if ($Name -in @("git_head", "head") -and $text -notmatch "^[0-9a-f]{40}$") {
        return $false
    }
    if ($Name -in @("git_branch", "branch") -and $text -notmatch "^[A-Za-z0-9._/\-]+$") {
        return $false
    }
    return $true
}

function Get-NewRealityGitTruth {
    param([string]$RepoRoot = "")

    $root = Resolve-NewRealityRoot -RepoRoot $RepoRoot
    $head = (git -C $root rev-parse HEAD).Trim()
    $branch = (git -C $root branch --show-current).Trim()
    $status = (git -C $root status --short) -join "`n"
    return [pscustomobject]@{
        git_head = $head
        git_branch = $branch
        git_status_short = $status
        git_head_sane = Test-GitFieldSanity -Name "git_head" -Value $head
        git_branch_sane = Test-GitFieldSanity -Name "git_branch" -Value $branch
    }
}
