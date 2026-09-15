[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateRange(0, [int]::MaxValue)]
    [int]$Shard,
    [Parameter(Mandatory)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$ShardCount
)

<#!
.SYNOPSIS
Runs each Windows pytest module in a separate interpreter for CI.

.DESCRIPTION
PySide native teardown can retain process-global state across modules on the
hosted Windows runner.  Running one module per interpreter preserves every
test while preventing that state from deadlocking the following module.
#>

$ErrorActionPreference = 'Stop'

$testFiles = Get-ChildItem -LiteralPath tests -Filter 'test_*.py' -File |
    Sort-Object -Property Name
$python = Join-Path $PWD '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    throw "Expected the uv-synchronised interpreter at $python."
}
if ($Shard -ge $ShardCount) {
    throw "Shard $Shard is outside the configured count of $ShardCount."
}

for ($index = $Shard; $index -lt $testFiles.Count; $index += $ShardCount) {
    $testFile = $testFiles[$index]
    $resultFile = "test-results-$($testFile.BaseName).xml"
    Write-Host "::group::pytest $($testFile.Name)"
    try {
        & $python -m pytest $testFile.FullName -vv -ra `
            "--junitxml=$resultFile" `
            -o faulthandler_timeout=120 `
            -o faulthandler_exit_on_timeout=true
        if ($LASTEXITCODE -ne 0) {
            throw "pytest failed for $($testFile.Name) with exit code $LASTEXITCODE."
        }
    }
    finally {
        Write-Host '::endgroup::'
    }
}
