# IMPERIUM ROOTS v0_2 — переносимый резолвер зон по алиасам (PowerShell, любая машина).
Set-StrictMode -Version Latest
$script:ImperiumRootsSchema = 'imperium.roots.v0_2'
$script:ImperiumRootsConfigName = 'imperium.roots.json'
$script:ImperiumRootsCanon = @('REALITY', 'WARP', 'HARNESS')
$script:ImperiumRootsDefaults = @{ REALITY = 'E:\IMPERIUM_REALITY'; WARP = 'E:\IMPERIUM_WARP'; HARNESS = 'E:\IMPERIUM_HARNESS' }

function Get-ImperiumAutoBase {
    # Якорь ТОЛЬКО на точных именах зон, чтобы папка пака (IMPERIUM_PORTABILITY_PACK) не стала базой.
    $zones = @('IMPERIUM_REALITY', 'IMPERIUM_WARP', 'IMPERIUM_HARNESS')
    $cur = $PSScriptRoot
    while ($cur) {
        $name = Split-Path $cur -Leaf
        if ($name -and ($zones -contains $name.ToUpper())) { return (Split-Path $cur -Parent) }
        $parent = Split-Path $cur -Parent
        if ($parent -eq $cur -or [string]::IsNullOrEmpty($parent)) { return $null }
        $cur = $parent
    }
    return $null
}

function Get-ImperiumRootsConfigPath {
    $cands = New-Object System.Collections.Generic.List[string]
    if ($env:IMPERIUM_ROOTS) { $cands.Add($env:IMPERIUM_ROOTS) }
    $cands.Add((Join-Path $PSScriptRoot $script:ImperiumRootsConfigName))
    if ($env:ProgramData) { $cands.Add((Join-Path (Join-Path $env:ProgramData 'Imperium') $script:ImperiumRootsConfigName)) }
    $cur = (Get-Location).Path
    while ($cur) {
        $cands.Add((Join-Path (Join-Path $cur '.imperium') 'roots.json'))
        $parent = Split-Path $cur -Parent
        if ($parent -eq $cur -or [string]::IsNullOrEmpty($parent)) { break }
        $cur = $parent
    }
    foreach ($c in $cands) { if ($c -and (Test-Path -LiteralPath $c -PathType Leaf)) { return $c } }
    return $null
}

function Get-ImperiumRootsConfig {
    $p = Get-ImperiumRootsConfigPath
    $map = @{}; $base = $null
    if ($p) {
        try {
            $data = Get-Content -LiteralPath $p -Raw | ConvertFrom-Json
            if ($data) {
                if (($data.PSObject.Properties.Name -contains 'base') -and $data.base) { $base = [string]$data.base }
                if (($data.PSObject.Properties.Name -contains 'aliases') -and $data.aliases) {
                    foreach ($pr in $data.aliases.PSObject.Properties) { $map[$pr.Name.ToUpper()] = [string]$pr.Value }
                }
            }
        } catch {}
    }
    return [pscustomobject]@{ Path = $p; Map = $map; Base = $base }
}

function Get-ImperiumBase {
    $cfg = Get-ImperiumRootsConfig
    if ($cfg.Base) { return [pscustomobject]@{ Value = $cfg.Base; Source = 'config.base' } }
    if ($env:IMPERIUM_HOME) { return [pscustomobject]@{ Value = $env:IMPERIUM_HOME; Source = 'env:IMPERIUM_HOME' } }
    $auto = Get-ImperiumAutoBase
    if ($auto) { return [pscustomobject]@{ Value = $auto; Source = 'auto' } }
    $drive = Split-Path $PSScriptRoot -Qualifier
    if ($drive) { return [pscustomobject]@{ Value = "$drive\"; Source = 'fallback' } }
    return [pscustomobject]@{ Value = 'E:\'; Source = 'fallback' }
}

function Get-ImperiumRoot {
    param([Parameter(Mandatory)][string]$Alias)
    $a = $Alias.ToUpper()
    $envVal = [System.Environment]::GetEnvironmentVariable("IMPERIUM_$a")
    if ($envVal) { return $envVal }
    $cfg = Get-ImperiumRootsConfig
    $b = Get-ImperiumBase; $base = $b.Value
    if ($cfg.Map.ContainsKey($a)) { return (($cfg.Map[$a] -replace '\{BASE\}', $base) -replace '\{HOME\}', $base) }
    if (($script:ImperiumRootsCanon -contains $a) -and ($b.Source -ne 'fallback')) { return (Join-Path $base "IMPERIUM_$a") }
    if ($a -eq 'REALITY') {
        try { $top = (& git rev-parse --show-toplevel 2>$null); if ($top) { return $top.Trim() } } catch {}
    }
    if ($script:ImperiumRootsCanon -contains $a) { return (Join-Path $base "IMPERIUM_$a") }
    if ($script:ImperiumRootsDefaults.ContainsKey($a)) { return $script:ImperiumRootsDefaults[$a] }
    throw "Unknown imperium root alias: $Alias"
}

function Resolve-ImperiumPath {
    param([Parameter(Mandatory)][string]$Path)
    if (-not $Path.StartsWith('@')) { return $Path }
    $rest = $Path.Substring(1)
    $idx = $rest.IndexOfAny([char[]]@('/', '\'))
    if ($idx -lt 0) { return (Get-ImperiumRoot $rest) }
    return (Join-Path (Get-ImperiumRoot $rest.Substring(0, $idx)) $rest.Substring($idx + 1))
}

function Show-ImperiumRoots {
    $cfg = Get-ImperiumRootsConfig; $b = Get-ImperiumBase
    Write-Host "schema_version: $script:ImperiumRootsSchema"
    Write-Host "config_file   : $(if($cfg.Path){$cfg.Path}else{'(none — ENV/auto)'})"
    Write-Host "base          : $($b.Value)  [$($b.Source)]"
    Write-Host ('-' * 60)
    $names = New-Object System.Collections.Generic.SortedSet[string]
    foreach ($k in $script:ImperiumRootsCanon) { [void]$names.Add($k) }
    foreach ($k in $cfg.Map.Keys) { [void]$names.Add($k) }
    foreach ($a in $names) { Write-Host ("  @{0,-10} = {1}" -f $a, (Get-ImperiumRoot $a)) }
}

Export-ModuleMember -Function Get-ImperiumRoot, Resolve-ImperiumPath, Show-ImperiumRoots, Get-ImperiumBase, Get-ImperiumAutoBase, Get-ImperiumRootsConfigPath
