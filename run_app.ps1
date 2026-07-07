$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    throw "Virtual environment not found at .venv\Scripts\Activate.ps1"
}

& ".venv\Scripts\Activate.ps1"
streamlit run app.py
