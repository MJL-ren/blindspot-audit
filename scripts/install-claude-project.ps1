param(
    [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot "skills\blindspot-audit"
. (Join-Path $PSScriptRoot "install-safety.ps1")

if (-not (Test-Path -LiteralPath $source)) {
    throw "Skill source not found: $source"
}

if (-not (Test-Path -LiteralPath $ProjectRoot)) {
    throw "Project root does not exist: $ProjectRoot"
}

$destination = Join-Path $ProjectRoot ".claude\skills"
New-Item -ItemType Directory -Force -Path $destination | Out-Null

# Replace, don't merge: an overwrite-copy leaves files that were renamed or
# deleted upstream lingering in the install, silently steering agents.
$installedPath = Join-Path $destination "blindspot-audit"
Remove-BlindspotInstallSafely -Destination $destination
Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force

Write-Host "Installed blindspot-audit skill to: $installedPath (previous install replaced)"
