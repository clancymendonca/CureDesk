# Full local setup via CLI
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== CureDesk CLI Setup ==="

Write-Host "`n[1/4] Python API dependencies..."
pip install -r services/api/requirements.txt -q
pip install -r ml/requirements.txt -q

Write-Host "`n[2/4] ML train (GPU if available)..."
python ml/train_symptoms.py

Write-Host "`n[3/4] Database..."
& "$PSScriptRoot\setup-db.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Skip DB if Docker is off — run 'pnpm setup:db' after starting Docker Desktop."
}

Write-Host "`n[4/4] Node dependencies..."
if (Get-Command pnpm -ErrorAction SilentlyContinue) {
    pnpm install
} else {
    npx pnpm@9.15.0 install
}

Write-Host "`n=== Done ==="
Write-Host "Start API:  pnpm api:dev"
Write-Host "Start web:  pnpm dev:web"
Write-Host "Firebase:   pnpm setup:firebase -- -ProjectId YOUR_PROJECT_ID"
