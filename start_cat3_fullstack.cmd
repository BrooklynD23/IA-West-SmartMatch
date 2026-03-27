@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "CAT3_DIR=%ROOT_DIR%Category 3 - IA West Smart Match CRM"

call "%CAT3_DIR%\scripts\start_fullstack.cmd" %*

endlocal
