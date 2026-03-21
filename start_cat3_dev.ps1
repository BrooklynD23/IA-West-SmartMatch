$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Cat3Script = Join-Path $RootDir "Category 3 - IA West Smart Match CRM\scripts\start_dev.ps1"

& powershell -ExecutionPolicy Bypass -File $Cat3Script @args
