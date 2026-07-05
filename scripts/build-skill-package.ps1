Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
python (Join-Path $PSScriptRoot "build-skill-package.py") --repo-root $repoRoot

