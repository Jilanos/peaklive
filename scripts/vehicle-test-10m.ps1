[CmdletBinding()]
param(
    [string]$ExecutablePath = (Join-Path $PSScriptRoot '..\..\PeakLive.exe'),
    [string]$BuildMetadataPath = (Join-Path $PSScriptRoot '..\..\PeakLive.build.txt'),
    [string]$ArtifactRoot = (Join-Path $PSScriptRoot '..\artifacts\vehicle-10m'),
    [ValidateSet('plan','interactive')]
    [string]$Mode = 'plan',
    [ValidateSet(125,250,500,1000)]
    [int]$Bitrate = 500
)

$ErrorActionPreference = 'Stop'
$duration = [TimeSpan]::FromMinutes(10)
$runId = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$artifactFull = [IO.Path]::GetFullPath($ArtifactRoot)
$runRoot = Join-Path $artifactFull $runId
$sandbox = Join-Path $runRoot 'sandbox'
$metricsPath = Join-Path $runRoot 'peaklive-metrics.jsonl'
$results = [System.Collections.Generic.List[object]]::new()
$process = $null

function Add-Result([string]$Id, [string]$Title, [string]$Status, [string]$Details) {
    $results.Add([pscustomobject]@{ id=$Id; title=$Title; status=$Status; details=$Details; utc=[DateTime]::UtcNow.ToString('o') })
}
function Read-Metadata([string]$Path) {
    $map=@{}; foreach ($line in Get-Content -LiteralPath $Path) { if ($line -match '^\s*([^:]+):\s*(.*?)\s*$') { $map[$Matches[1]]=$Matches[2] } }
    foreach ($key in 'identifier','sha256') { if (-not $map.ContainsKey($key)) { throw "Build metadata missing '$key'." } }
    $map
}
function Check-Time([DateTime]$Deadline, [string]$Phase) {
    $remaining = $Deadline - (Get-Date)
    if ($remaining.TotalSeconds -le 0) { throw "10-minute deadline exceeded before phase '$Phase'." }
    return [Math]::Max(1, [int]$remaining.TotalSeconds)
}
function Ask-Checkpoint([string]$Id, [string]$Title, [string]$Instructions, [int]$BudgetSeconds, [DateTime]$Deadline) {
    $remaining=Check-Time $Deadline $Title
    Write-Host "[$Id | ${BudgetSeconds}s budget | ${remaining}s remaining] $Title" -ForegroundColor Cyan
    Write-Host $Instructions
    if ($Mode -eq 'plan') { Add-Result $Id $Title 'NotRun' "Planned; budget=${BudgetSeconds}s; remaining=${remaining}s"; return }
    $status=(Read-Host 'Status [P]ass/[F]ail/[N]otRun').Trim().ToUpperInvariant()
    if ($status -notin 'P','F','N') { $status='N' }
    $mapped=@{ P='Pass'; F='Fail'; N='NotRun' }[$status]
    Add-Result $Id $Title $mapped "budget=${BudgetSeconds}s; remaining=${remaining}s; $Instructions"
}

try {
    New-Item -ItemType Directory -Force -Path $artifactFull,$runRoot,$sandbox | Out-Null
    if (-not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) { throw "Executable not found: $ExecutablePath" }
    $metadata=Read-Metadata $BuildMetadataPath
    $hash=(Get-FileHash -LiteralPath $ExecutablePath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($hash -ne $metadata.sha256.ToUpperInvariant()) { throw "SHA-256 mismatch: expected $($metadata.sha256), got $hash" }
    $deadline=(Get-Date).Add($duration)
    $env:PEAKLIVE_DATA_DIR=$sandbox
    $env:PEAKLIVE_QUALIFICATION_METRICS=$metricsPath
    Set-Content -LiteralPath (Join-Path $runRoot 'environment.txt') -Value @(
        "run_id=$runId", "identifier=$($metadata.identifier)", "sha256=$hash", "bitrate_kbit=$Bitrate",
        "deadline_local=$deadline", "metrics=$metricsPath", "safety=receive-only; passive listen-only; no transmit"
    )
    Add-Result 'V10-001' 'Build/hash and vehicle safety preflight' 'Pass' "identifier=$($metadata.identifier); sha256=$hash; bitrate=$Bitrate; hard deadline=$deadline"
    if ($Mode -eq 'plan') {
        Write-Host 'PLAN ONLY: no executable launched and no vehicle bus action performed.' -ForegroundColor Yellow
    } else {
        $process=Start-Process -FilePath $ExecutablePath -WorkingDirectory (Split-Path $ExecutablePath) -PassThru
        Add-Result 'V10-002' 'Packaged executable launch' 'Pass' "pid=$($process.Id); sandbox=$sandbox"
    }
    Ask-Checkpoint 'V10-003' 'Connect passively' 'Secure the vehicle, select the adapter/channel and declared bitrate, choose passive listen-only, and verify the bus indicator reaches Running. Do not transmit.' 60 $deadline
    Ask-Checkpoint 'V10-004' 'Capture active traffic' 'Observe incoming frames and counters for two minutes. Start recording if safe; note frame rate, errors, and capture path.' 120 $deadline
    Ask-Checkpoint 'V10-005' 'Stop and preserve evidence' 'Press Stop. Confirm the window remains responsive, state reaches Stopped (or documented degraded), and ASC plus event sidecar/partial files exist.' 60 $deadline
    Ask-Checkpoint 'V10-006' 'Replay captured output' 'Open the just-created ASC/TRC copy, replay it, and confirm frame count/order is plausible. Do not overwrite the live capture.' 120 $deadline
    Ask-Checkpoint 'V10-007' 'Load DBC and inspect signals' 'Load one approved DBC, select a decoded signal, inspect a frame and graph, and record decode status/unit.' 90 $deadline
    Ask-Checkpoint 'V10-008' 'Export a bounded result' 'Set a short A-B/window range and export CSV and Parquet to the sandbox. Verify files are readable and no pre-existing sentinel changed.' 60 $deadline
    Ask-Checkpoint 'V10-009' 'Close and collect evidence' 'Close PeakLive cleanly. Record counters, state text, errors, capture paths, screenshots, and any partial artifacts in this run directory.' 60 $deadline
    Check-Time $deadline 'final evidence write'
    $failed=@($results | Where-Object status -eq 'Fail')
    $summary=[ordered]@{ schema='peaklive.vehicle-10m.v1'; run_id=$runId; duration_limit_seconds=600; identifier=$metadata.identifier; sha256=$hash; bitrate_kbit=$Bitrate; artifact_root=$runRoot; results=@($results); counts=[ordered]@{ pass=@($results|Where-Object status -eq 'Pass').Count; fail=$failed.Count; not_run=@($results|Where-Object status -eq 'NotRun').Count } }
    $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runRoot 'summary.json') -Encoding utf8
    $lines=[System.Collections.Generic.List[string]]::new(); $lines.Add("# PeakLive vehicle test (10 minutes) $runId"); $lines.Add(""); $lines.Add("Build: **$($metadata.identifier)**  "); $lines.Add("SHA-256: **$hash**  "); $lines.Add("Bitrate: **$Bitrate kbit/s**; safety: **passive receive-only, no transmit**"); $lines.Add(""); foreach ($item in $results) { $lines.Add(("- **{0}** `{1}` {2}: {3}" -f $item.status,$item.id,$item.title,$item.details)) }; $lines.Add(""); $lines.Add("Evidence root: ``$runRoot``"); $lines | Set-Content -LiteralPath (Join-Path $runRoot 'report.md') -Encoding utf8
    if ($failed.Count -gt 0) { exit 1 }
} catch {
    Add-Result 'V10-ERROR' '10-minute runner failure' 'Fail' $_.Exception.Message
    if (Test-Path $runRoot) { $results | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runRoot 'summary.json') -Encoding utf8 }
    Write-Error $_
    exit 1
} finally {
    if ($process -and -not $process.HasExited) { $process.CloseMainWindow() | Out-Null; if (-not $process.WaitForExit(5000)) { $process.Kill(); $process.WaitForExit() } }
    Remove-Item Env:PEAKLIVE_DATA_DIR -ErrorAction SilentlyContinue
    Remove-Item Env:PEAKLIVE_QUALIFICATION_METRICS -ErrorAction SilentlyContinue
    Write-Host "Vehicle test evidence: $runRoot"
}
