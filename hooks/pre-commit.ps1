#!/usr/bin/env pwsh
# Pre-commit hook for PowerShell — run tests before allowing a commit.
# Exit non-zero = block the commit.
#
# Install on Windows:
#   git config core.hooksPath hooks
#
# Or copy this file to .git/hooks/pre-commit (no extension needed on Windows
# if Git for Windows is configured to use PowerShell as shell).

Write-Host "🧪 Running pre-commit tests..." -ForegroundColor Cyan

$ProjectDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $ProjectDir

# Activate venv if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}
elseif (Test-Path "venv\Scripts\Activate.ps1") {
    . venv\Scripts\Activate.ps1
}
elseif (Test-Path "$env:USERPROFILE\.hermes\scripts\wend-venv\Scripts\Activate.ps1") {
    . "$env:USERPROFILE\.hermes\scripts\wend-venv\Scripts\Activate.ps1"
}
else {
    Write-Host "ℹ️  No virtual environment found. Using system Python." -ForegroundColor Yellow
}

# Ensure pytest is available
$pytest = Get-Command pytest -ErrorAction SilentlyContinue
if (-not $pytest) {
    Write-Host "📦 Installing pytest..." -ForegroundColor Yellow
    pip install -q pytest
}

Write-Host "━━━ Running solver tests ━━━" -ForegroundColor Cyan
python -m pytest tests/test_wend_solver.py -v --tb=short
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "❌ Tests FAILED — commit blocked." -ForegroundColor Red
    Write-Host "   Fix the failures above, then commit again." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All tests passed." -ForegroundColor Green
exit 0
