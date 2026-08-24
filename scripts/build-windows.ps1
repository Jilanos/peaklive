$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/"
}

function Invoke-NativeStep {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-NativeStep "uv sync" { uv sync --all-extras }
Invoke-NativeStep "ruff" { uv run ruff check . }
Invoke-NativeStep "pytest" { uv run python -m pytest }
Invoke-NativeStep "pyinstaller" { uv run python -m PyInstaller --noconfirm --clean peaklive.spec }

Write-Host "PeakLive executable: $PWD\dist\PeakLive.exe"
