param(
    [string]$Destination
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot "skills\blindspot-audit"

if (-not (Test-Path -LiteralPath $source)) {
    throw "Skill source not found: $source"
}

if (-not $Destination) {
    $Destination = Join-Path $HOME ".agents\skills"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$destinationPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination).TrimEnd("\", "/")

# Replace, don't merge: an overwrite-copy leaves files that were renamed or
# deleted upstream lingering in the install, silently steering agents.
$installedPath = Join-Path $Destination "blindspot-audit"
if (Test-Path -LiteralPath $installedPath) {
    $resolved = (Resolve-Path -LiteralPath $installedPath).Path
    if ((Split-Path -Leaf $resolved) -ne "blindspot-audit") {
        throw "Refusing to remove unexpected path: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
Copy-Item -LiteralPath $source -Destination $Destination -Recurse -Force

Write-Host "Installed blindspot-audit skill to: $installedPath (previous install replaced)"

$legacyDestinations = @((Join-Path $HOME ".codex\skills"))
if ($env:CODEX_HOME) {
    $legacyDestinations += Join-Path $env:CODEX_HOME "skills"
}

$seenLegacyPaths = @{}
foreach ($legacyDestination in $legacyDestinations) {
    $legacyDestinationPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($legacyDestination).TrimEnd("\", "/")
    if ($legacyDestinationPath -ieq $destinationPath -or $seenLegacyPaths.ContainsKey($legacyDestinationPath)) {
        continue
    }
    $seenLegacyPaths[$legacyDestinationPath] = $true

    $legacyInstalledPath = Join-Path $legacyDestinationPath "blindspot-audit"
    if (Test-Path -LiteralPath $legacyInstalledPath -PathType Container) {
        Write-Warning "Legacy Codex skill copy found at: $legacyInstalledPath. Current Codex uses ~/.agents/skills by default, and same-name copies can both appear. This installer does not delete legacy copies; remove or migrate it manually after confirming the new install."
    }
}
