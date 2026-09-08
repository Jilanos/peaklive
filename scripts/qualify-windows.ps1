[CmdletBinding()]
param(
    [string]$ExecutablePath = (Join-Path $PSScriptRoot '..\..\PeakLive.exe'),
    [string]$BuildMetadataPath = (Join-Path $PSScriptRoot '..\..\PeakLive.build.txt'),
    [string]$ArtifactRoot = (Join-Path $PSScriptRoot '..\artifacts\windows-qualification'),
    [ValidateSet('automated','all','hardware','ui','fixtures')]
    [string]$Lane = 'automated',
    [int]$StartupTimeoutSeconds = 20,
    [switch]$KeepSandbox
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runId = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$artifactFull = [IO.Path]::GetFullPath($ArtifactRoot)
New-Item -ItemType Directory -Force -Path $artifactFull | Out-Null
$runRoot = Join-Path $artifactFull $runId
$sandbox = Join-Path $runRoot 'sandbox'
$summaryPath = Join-Path $runRoot 'summary.json'
$reportPath = Join-Path $runRoot 'report.md'
$results = [System.Collections.Generic.List[object]]::new()

function Add-Case([string]$Id, [string]$Title, [string]$Status, [string]$Details, [bool]$Mandatory = $true) {
    $results.Add([pscustomobject]@{
        id = $Id; title = $Title; status = $Status; mandatory = $Mandatory
        details = $Details; utc = [DateTime]::UtcNow.ToString('o')
    })
}
function Assert-PathInside([string]$Child, [string]$Parent) {
    $childFull = [IO.Path]::GetFullPath($Child).TrimEnd('\') + '\'
    $parentFull = [IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    if (-not $childFull.StartsWith($parentFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes declared root: $Child"
    }
}
function Read-BuildMetadata([string]$Path) {
    $map = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*([^:]+):\s*(.*?)\s*$') { $map[$Matches[1]] = $Matches[2] }
    }
    foreach ($key in 'identifier','sha256','executable') {
        if (-not $map.ContainsKey($key)) { throw "Build metadata missing '$key'." }
    }
    return $map
}
function Invoke-GuidedCase([string]$Id, [string]$Title, [string]$Instructions, [bool]$Mandatory = $false) {
    Add-Case $Id $Title 'NotRun' $Instructions $Mandatory
    Write-Host "[NOT RUN] $Id - $Title" -ForegroundColor Yellow
    Write-Host $Instructions
}

try {
    New-Item -ItemType Directory -Force -Path $artifactFull | Out-Null
    New-Item -ItemType Directory -Force -Path $runRoot,$sandbox | Out-Null
    Assert-PathInside $runRoot $ArtifactRoot
    Assert-PathInside $sandbox $runRoot
    $metadata = Read-BuildMetadata $BuildMetadataPath
    if (-not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) { throw "Executable not found: $ExecutablePath" }
    $hash = (Get-FileHash -LiteralPath $ExecutablePath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($hash -ne $metadata.sha256.ToUpperInvariant()) { throw "SHA-256 mismatch: expected $($metadata.sha256), got $hash" }
    Add-Case 'PRE-001' 'Build identity and SHA-256' 'Pass' "identifier=$($metadata.identifier); sha256=$hash"
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'This runner requires Windows.' }
    Add-Case 'PRE-002' 'Windows platform preflight' 'Pass' "$([Environment]::OSVersion.VersionString); $env:PROCESSOR_ARCHITECTURE"
    if ((Get-PSDrive -Name ([IO.Path]::GetPathRoot($runRoot).TrimEnd('\')[0]) -ErrorAction SilentlyContinue).Free -lt 1GB) { throw 'Less than 1 GiB free in artifact volume.' }
    $env:PEAKLIVE_DATA_DIR = $sandbox
    Set-Content -LiteralPath (Join-Path $runRoot 'environment.txt') -Value @(
        "utc=$([DateTime]::UtcNow.ToString('o'))", "identifier=$($metadata.identifier)", "sha256=$hash",
        "os=$([Environment]::OSVersion.VersionString)", "powershell=$($PSVersionTable.PSVersion)",
        "processor=$env:PROCESSOR_ARCHITECTURE", "data_dir=$sandbox"
    )

    if ($Lane -in 'automated','all') {
        $before = @(Get-Process -Name PeakLive -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
        $process = Start-Process -FilePath $ExecutablePath -WorkingDirectory (Split-Path $ExecutablePath) -PassThru
        try {
            $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
            do { Start-Sleep -Milliseconds 250; $process.Refresh() } while (-not $process.HasExited -and (Get-Date) -lt $deadline)
            if ($process.HasExited) { throw "Process exited during startup with code $($process.ExitCode)." }
            Add-Case 'SMOKE-001' 'Packaged executable startup' 'Pass' "pid=$($process.Id); stayed alive for ${StartupTimeoutSeconds}s"
        } finally {
            if (-not $process.HasExited) { $process.CloseMainWindow() | Out-Null; if (-not $process.WaitForExit(5000)) { $process.Kill(); $process.WaitForExit() } }
        }
        $newProfileFiles = @(Get-ChildItem -LiteralPath $sandbox -Recurse -File -ErrorAction SilentlyContinue)
        Add-Case 'SMOKE-002' 'Isolated PEAKLIVE_DATA_DIR' 'Pass' "sandbox=$sandbox; files=$($newProfileFiles.Count)"
    }
    if ($Lane -in 'ui','all') {
        Invoke-GuidedCase 'UI-001' 'Identity and disconnected state' "Open the executable, verify status bar/About identifier '$($metadata.identifier)', packaged execution text, and no automatic bus connection." $true
        Invoke-GuidedCase 'UI-002' 'Viewport and keyboard matrix' 'At 100%, 125%, and 150% scaling check 1024x768, 1280x720, and 1600x900. Exercise F5/F6, Ctrl+D/O/E/1/2/0/F/B/Q and capture screenshots.' $true
        Invoke-GuidedCase 'UI-003' 'Profile persistence and recovery' 'Save a setup, restart, verify it is restored, then test a copy of a corrupt store. Preserve screenshots and logs in this run directory.'
    }
    if ($Lane -in 'fixtures','all') {
        Invoke-GuidedCase 'FIX-001' 'Replay and analysis workflow' 'Copy ASC/TRC and DBC fixtures into the sandbox, then verify replay, filtering, inspector, signal/graph selection, cursors, measurements, report, CSV, and Parquet.' $true
        Invoke-GuidedCase 'FIX-002' 'Transactional output protection' 'Place a sentinel at each export destination, cancel/fail an export, and verify the sentinel is byte-for-byte unchanged.'
    }
    if ($Lane -in 'hardware','all') {
        Invoke-GuidedCase 'HW-001' 'PCAN passive acquisition' 'On an approved active Classic CAN bench, record adapter/driver/channel/bitrate and verify passive frames, recording, clean Stop, and counters.' $true
        Invoke-GuidedCase 'HW-002' 'Reconnect and degraded shutdown' 'Under operator supervision unplug/replug PCAN during acquisition, verify responsive Stopping/degraded state and recoverable partial ASC plus event sidecar.' $true
        Invoke-GuidedCase 'HW-003' '60-minute endurance' 'With an approved high-load bus and sufficient disk, record 60 minutes, rotation, sidecars, high-water mark, driver events, and replayability.' $false
    }
    $failed = @($results | Where-Object status -eq 'Fail')
    $summary = [ordered]@{ schema = 'peaklive.windows-qualification.v1'; run_id = $runId; executable = (Resolve-Path $ExecutablePath).Path; identifier = $metadata.identifier; sha256 = $hash; artifact_root = $runRoot; results = @($results); counts = [ordered]@{ pass = @($results | Where-Object status -eq 'Pass').Count; fail = $failed.Count; not_run = @($results | Where-Object status -eq 'NotRun').Count } }
    $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
    $lines = [System.Collections.Generic.List[string]]::new(); $lines.Add("# PeakLive Windows qualification $runId"); $lines.Add(""); $lines.Add("Build: **$($metadata.identifier)**  "); $lines.Add("SHA-256: **$hash**  "); $lines.Add(""); foreach ($item in $results) { $lines.Add(("- **{0}** ``{1}`` {2}: {3}" -f $item.status,$item.id,$item.title,$item.details)) }; $lines.Add(""); $lines.Add(("Evidence root: ``{0}``" -f $runRoot)); $lines | Set-Content -LiteralPath $reportPath -Encoding utf8
    Write-Host "Qualification report: $reportPath"
    if ($failed.Count -gt 0) { exit 1 }
} catch {
    Add-Case 'RUN-ERROR' 'Runner failure' 'Fail' $_.Exception.Message
    $results | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding utf8
    Write-Error $_
    exit 1
} finally {
    Remove-Item Env:PEAKLIVE_DATA_DIR -ErrorAction SilentlyContinue
    if (-not $KeepSandbox) { Write-Host "Sandbox retained under $sandbox for evidence review." }
}
