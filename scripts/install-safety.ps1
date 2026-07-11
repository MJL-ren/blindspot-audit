Set-StrictMode -Version Latest

function Test-BlindspotPathEqual {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Left,
        [Parameter(Mandatory = $true)]
        [string]$Right
    )

    return [string]::Equals(
        $Left.TrimEnd("\", "/"),
        $Right.TrimEnd("\", "/"),
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

function Remove-BlindspotInstallSafely {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Destination,
        [string]$SkillName = "blindspot-audit"
    )

    if (-not (Test-Path -LiteralPath $Destination -PathType Container)) {
        throw "Install destination is not a directory: $Destination"
    }

    $destinationProviderPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
    $destinationFull = [System.IO.Path]::GetFullPath($destinationProviderPath).TrimEnd("\", "/")
    $installedFull = [System.IO.Path]::GetFullPath((Join-Path $destinationFull $SkillName)).TrimEnd("\", "/")
    $installedParent = Split-Path -Parent $installedFull

    if (-not (Test-BlindspotPathEqual -Left $installedParent -Right $destinationFull)) {
        throw "Refusing install path outside destination: $installedFull"
    }
    if ((Split-Path -Leaf $installedFull) -ne $SkillName) {
        throw "Refusing unexpected install leaf: $installedFull"
    }
    if (-not (Test-Path -LiteralPath $installedFull)) {
        return
    }

    $rootItem = Get-Item -LiteralPath $installedFull -Force
    if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Refusing to remove reparse-point install path: $installedFull"
    }

    $resolvedDestination = (Resolve-Path -LiteralPath $destinationFull).Path.TrimEnd("\", "/")
    $resolvedInstalled = (Resolve-Path -LiteralPath $installedFull).Path.TrimEnd("\", "/")
    if (-not (Test-BlindspotPathEqual -Left (Split-Path -Parent $resolvedInstalled) -Right $resolvedDestination)) {
        throw "Resolved install path escaped destination: $resolvedInstalled"
    }

    $directories = New-Object 'System.Collections.Generic.Stack[string]'
    $directories.Push($installedFull)
    while ($directories.Count -gt 0) {
        $current = $directories.Pop()
        foreach ($child in Get-ChildItem -LiteralPath $current -Force) {
            if (($child.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Refusing to recurse through reparse point: $($child.FullName)"
            }
            if ($child.PSIsContainer) {
                $directories.Push($child.FullName)
            }
        }
    }

    Remove-Item -LiteralPath $installedFull -Recurse -Force
}
