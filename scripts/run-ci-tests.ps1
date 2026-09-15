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

foreach ($testFile in $testFiles) {
    $resultFile = "test-results-$($testFile.BaseName).xml"
    Write-Host "::group::pytest $($testFile.Name)"
    try {
        & uv run python -m pytest $testFile.FullName -vv -ra `
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
