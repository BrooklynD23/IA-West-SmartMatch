param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$SkipInstall,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RootDir

$pythonCandidates = @(
    (Join-Path $RootDir ".venv\Scripts\python.exe"),
    (Join-Path $RootDir ".venv\bin\python"),
    "python"
)

$pythonExe = $null
foreach ($candidate in $pythonCandidates) {
    if ($candidate -eq "python") {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if ($cmd) {
            $pythonExe = "python"
            break
        }
    }
    elseif (Test-Path $candidate) {
        $pythonExe = $candidate
        break
    }
}

if (-not $pythonExe) {
    Write-Error "Python not found. Install Python 3.11+ and retry."
}

$argsList = @(
    "scripts/start_fullstack.py",
    "--backend-port", "$BackendPort",
    "--frontend-port", "$FrontendPort"
)

if ($SkipInstall) { $argsList += "--skip-install" }
if ($NoBrowser) { $argsList += "--no-browser" }

& $pythonExe @argsList
