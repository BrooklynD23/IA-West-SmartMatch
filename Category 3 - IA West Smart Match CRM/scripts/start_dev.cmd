@echo off
setlocal

set "ROOT_DIR=%~dp0.."
pushd "%ROOT_DIR%"

if "%PYTHON_EXE%"=="" set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"
if "%BACKEND_PORT%"=="" set "BACKEND_PORT=8000"
if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=8501"

if not exist "%PYTHON_EXE%" (
  echo Missing python executable at "%PYTHON_EXE%"
  echo Create the virtualenv first: py -3 -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  popd
  exit /b 1
)

echo Starting CAT3 dev backend on http://127.0.0.1:%BACKEND_PORT%
start "CAT3 Backend" cmd /k ""%PYTHON_EXE%" scripts\dev_backend.py --host 127.0.0.1 --port %BACKEND_PORT%"

echo Starting Streamlit frontend on http://127.0.0.1:%FRONTEND_PORT%
start "CAT3 Frontend" cmd /k ""%PYTHON_EXE%" -m streamlit run src\app.py --server.port %FRONTEND_PORT% --server.address 127.0.0.1"

echo Backend and frontend launched in separate terminals.
echo Close both terminals to stop all services.

popd
endlocal
