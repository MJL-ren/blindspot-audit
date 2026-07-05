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
    $Destination = Join-Path $HOME ".claude\skills"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item -LiteralPath $source -Destination $Destination -Recurse -Force

$installedPath = Join-Path $Destination "blindspot-audit"
Write-Host "Installed blindspot-audit skill to: $installedPath"
Write-Host "This path is read by Claude Code, and also by OpenCode (Claude-compatible skill path)."
