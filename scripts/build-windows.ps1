$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/"
}

uv sync --all-extras
uv run ruff check .
uv run pytest
uv run pyinstaller --noconfirm --clean peaklive.spec

Write-Host "PeakLive executable: $PWD\dist\PeakLive.exe"
