@echo off
setlocal

set "ROOT_DIR=%~dp0.."
pushd "%ROOT_DIR%"

set "PYTHON_EXE="
if exist "%ROOT_DIR%\.venv\Scripts\python.exe" set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"
if "%PYTHON_EXE%"=="" if exist "%ROOT_DIR%\.venv\bin\python" set "PYTHON_EXE=%ROOT_DIR%\.venv\bin\python"
if "%PYTHON_EXE%"=="" set "PYTHON_EXE=python"

if /I "%PYTHON_EXE%"=="python" (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python not found. Install Python 3.11+ and retry.
    popd
    exit /b 1
  )
) else (
  if not exist "%PYTHON_EXE%" (
    echo Python not found at "%PYTHON_EXE%". Install Python 3.11+ and retry.
    popd
    exit /b 1
  )
)

"%PYTHON_EXE%" scripts\start_fullstack.py %*
set "EXIT_CODE=%ERRORLEVEL%"

popd
endlocal & exit /b %EXIT_CODE%
