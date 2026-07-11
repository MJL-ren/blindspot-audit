param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\install-safety.ps1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot "skills\blindspot-audit"
$targetProviderPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($TargetPath)
$target = [System.IO.Path]::GetFullPath($targetProviderPath).TrimEnd("\", "/")
$targetParent = Split-Path -Parent $target
$targetLeaf = Split-Path -Leaf $target

if ($targetLeaf -ne "blindspot-audit-testing") {
    throw "Testing skill target must end with blindspot-audit-testing: $target"
}
if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "Canonical skill source is missing: $source"
}
if (-not (Test-Path -LiteralPath $targetParent -PathType Container)) {
    New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
}

Remove-BlindspotInstallSafely -Destination $targetParent -SkillName $targetLeaf
New-Item -ItemType Directory -Path $target -Force | Out-Null

$sourceFull = [System.IO.Path]::GetFullPath($source).TrimEnd("\", "/")
foreach ($file in Get-ChildItem -LiteralPath $sourceFull -File -Recurse -Force) {
    if ($file.Extension -eq ".pyc" -or $file.FullName -match "[\\/]__pycache__[\\/]") {
        continue
    }
    $relative = $file.FullName.Substring($sourceFull.Length).TrimStart("\", "/")
    $destination = Join-Path $target $relative
    $destinationParent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationParent -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
    }
    Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$skillPath = Join-Path $target "SKILL.md"
$skillText = [System.IO.File]::ReadAllText($skillPath)
$namePattern = [regex]::new('(?m)^name: blindspot-audit\s*$')
$descriptionPattern = [regex]::new('(?m)^description: "')
if (-not $namePattern.IsMatch($skillText) -or -not $descriptionPattern.IsMatch($skillText)) {
    throw "Canonical SKILL.md frontmatter could not be adapted for testing."
}
$skillText = $namePattern.Replace($skillText, 'name: blindspot-audit-testing', 1)
$skillText = $descriptionPattern.Replace(
    $skillText,
    'description: "Pre-release testing copy. Use only when explicitly invoked as $blindspot-audit-testing. ',
    1
)
[System.IO.File]::WriteAllText($skillPath, $skillText, $utf8NoBom)

$openAiPath = Join-Path $target "agents\openai.yaml"
$openAiText = [System.IO.File]::ReadAllText($openAiPath)
$replacements = @{
    '(?m)^  display_name:.*$' = '  display_name: "Blindspot Audit - Testing"'
    '(?m)^  short_description:.*$' = '  short_description: "Pre-release copy for explicit project audit testing."'
    '(?m)^  default_prompt:.*$' = '  default_prompt: "Use $blindspot-audit-testing to run the requested testing audit on this project."'
}
foreach ($entry in $replacements.GetEnumerator()) {
    $pattern = [regex]::new($entry.Key)
    if (-not $pattern.IsMatch($openAiText)) {
        throw "Canonical agents/openai.yaml is missing a required interface field."
    }
    $openAiText = $pattern.Replace($openAiText, $entry.Value, 1)
}
[System.IO.File]::WriteAllText($openAiPath, $openAiText, $utf8NoBom)

Write-Output "Synced testing skill: $target"
Write-Output "Identity overrides: blindspot-audit-testing / Blindspot Audit - Testing"
