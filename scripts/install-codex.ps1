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
Copy-Item -LiteralPath $source -Destination $Destination -Recurse -Force

$installedPath = Join-Path $Destination "blindspot-audit"
Write-Host "Installed blindspot-audit skill to: $installedPath"

