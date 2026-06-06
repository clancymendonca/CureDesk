# Start Postgres and run migrations + seed
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "==> Starting Postgres (Docker)..."
docker compose up postgres -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker failed. Start Docker Desktop and retry: pnpm setup:db"
    exit 1
}

Write-Host "Waiting for Postgres..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    docker compose exec -T postgres pg_isready -U curedesk 2>$null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    Write-Host "ERROR: Postgres did not become ready in time."
    exit 1
}

Write-Host "==> Alembic migrate..."
Push-Location services\api
alembic upgrade head
if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }

Write-Host "==> Seed database..."
python -m app.scripts.seed
Pop-Location

Write-Host "Database ready."
