# IMPERIUM ROOTS — адаптивный резолвер зон по алиасам (PowerShell).
# Приоритет: ENV IMPERIUM_<ALIAS> > imperium.roots.json > встроенный дефолт.
Set-StrictMode -Version Latest

$script:ImperiumRootsSchema = 'imperium.roots.v0_1'
$script:ImperiumRootsConfigName = 'imperium.roots.json'
$script:ImperiumRootsDefaults = @{
    REALITY = 'E:\IMPERIUM_REALITY'
    WARP    = 'E:\IMPERIUM_WARP'
    HARNESS = 'E:\IMPERIUM_HARNESS'
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
    $map = @{}
    if ($p) {
        try {
            $data = Get-Content -LiteralPath $p -Raw | ConvertFrom-Json
            if ($data -and ($data.PSObject.Properties.Name -contains 'aliases') -and $data.aliases) {
                foreach ($prop in $data.aliases.PSObject.Properties) { $map[$prop.Name.ToUpper()] = [string]$prop.Value }
            }
        } catch {}
    }
    return [pscustomobject]@{ Path = $p; Map = $map }
}

function Get-ImperiumRoot {
    param([Parameter(Mandatory)][string]$Alias)
    $a = $Alias.ToUpper()
    $envVal = [System.Environment]::GetEnvironmentVariable("IMPERIUM_$a")
    if ($envVal) { return $envVal }
    $cfg = Get-ImperiumRootsConfig
    if ($cfg.Map.ContainsKey($a)) { return $cfg.Map[$a] }
    if ($script:ImperiumRootsDefaults.ContainsKey($a)) { return $script:ImperiumRootsDefaults[$a] }
    throw "Unknown imperium root alias: $Alias"
}

function Resolve-ImperiumPath {
    param([Parameter(Mandatory)][string]$Path)
    if (-not $Path.StartsWith('@')) { return $Path }
    $rest = $Path.Substring(1)
    $idx = $rest.IndexOfAny([char[]]@('/', '\'))
    if ($idx -lt 0) { return (Get-ImperiumRoot $rest) }
    $alias = $rest.Substring(0, $idx)
    $remainder = $rest.Substring($idx + 1)
    return (Join-Path (Get-ImperiumRoot $alias) $remainder)
}

function Show-ImperiumRoots {
    $cfg = Get-ImperiumRootsConfig
    Write-Host "schema_version: $script:ImperiumRootsSchema"
    Write-Host "config_file   : $(if($cfg.Path){$cfg.Path}else{'(none — ENV/defaults)'})"
    Write-Host ('-' * 56)
    $names = New-Object System.Collections.Generic.SortedSet[string]
    foreach ($k in $script:ImperiumRootsDefaults.Keys) { [void]$names.Add($k) }
    foreach ($k in $cfg.Map.Keys) { [void]$names.Add($k) }
    foreach ($a in $names) {
        $envVal = [System.Environment]::GetEnvironmentVariable("IMPERIUM_$a")
        if ($envVal) { $src = "env:IMPERIUM_$a"; $val = $envVal }
        elseif ($cfg.Map.ContainsKey($a)) { $src = 'config'; $val = $cfg.Map[$a] }
        else { $src = 'default'; $val = $script:ImperiumRootsDefaults[$a] }
        Write-Host ("  @{0,-10} = {1,-32} [{2}]" -f $a, $val, $src)
    }
}

Export-ModuleMember -Function Get-ImperiumRoot, Resolve-ImperiumPath, Show-ImperiumRoots, Get-ImperiumRootsConfigPath
