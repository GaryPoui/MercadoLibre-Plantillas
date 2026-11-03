param([int]$Port = 8765, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskPython = Join-Path $taskRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Creá .venv con Python 3.12 e instalá requirements.txt. Ver README.md.'
}
Set-Location -LiteralPath $taskRoot
if (-not $NoBrowser) {
    Start-Process "http://127.0.0.1:$Port"
}
& $taskPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
