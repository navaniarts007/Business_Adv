# Starts Vyapar Mitra on http://localhost:8000
# First run: creates a virtual environment and installs dependencies.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip install -r requirements.txt
}
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host "Created .env - add your GEMINI_API_KEY to enable live research." }
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
