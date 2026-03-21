param(
    [string]$PythonExe = "",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 8501
)

$ErrorActionPreference = "Stop"

$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RootDir

if ([string]::IsNullOrWhiteSpace($PythonExe) -and $env:PYTHON_EXE) {
    $PythonExe = $env:PYTHON_EXE
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $candidatePaths = @(
        (Join-Path $RootDir ".venv\Scripts\python.exe"),
        (Join-Path (Split-Path -Parent $RootDir) ".venv\Scripts\python.exe")
    )
    foreach ($candidate in $candidatePaths) {
        if (Test-Path $candidate) {
            $PythonExe = $candidate
            break
        }
    }
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        Write-Host "No project virtualenv found. Creating .venv in CAT3..."
        & py -3 -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create .venv with py launcher."
        }
        $PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
        Write-Host "Installing requirements into .venv..."
        & $PythonExe -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Dependency install failed for '$PythonExe -m pip install -r requirements.txt'."
        }
    }
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $PythonExe = "python"
    }
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    Write-Error "No usable Python runtime found. Install Python 3.11+ or pass -PythonExe."
}

if ($PythonExe -ne "python" -and -not (Test-Path $PythonExe)) {
    Write-Error "Resolved python executable does not exist: '$PythonExe'"
}

Write-Host "Starting CAT3 dev backend on http://127.0.0.1:$BackendPort"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`"$PythonExe`" scripts/dev_backend.py --host 127.0.0.1 --port $BackendPort"
) | Out-Null

Write-Host "Starting Streamlit frontend on http://127.0.0.1:$FrontendPort"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`"$PythonExe`" -m streamlit run src/app.py --server.port $FrontendPort --server.address 127.0.0.1"
) | Out-Null

Write-Host "Backend and frontend launched in separate PowerShell windows."
Write-Host "Close both windows to stop all services."
