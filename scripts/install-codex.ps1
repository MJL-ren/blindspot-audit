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
    if ($env:CODEX_HOME) {
        $Destination = Join-Path $env:CODEX_HOME "skills"
    } else {
        $Destination = Join-Path $HOME ".codex\skills"
    }
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

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
