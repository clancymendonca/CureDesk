# Download real ML datasets for CureDesk
param(
    [switch]$All,
    [switch]$IncludeLarge,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$kaggleJson = Join-Path $env:USERPROFILE ".kaggle\kaggle.json"
$hasEnv = $env:KAGGLE_USERNAME -and $env:KAGGLE_KEY
$hasFile = Test-Path $kaggleJson

if (-not $All) {
    if (-not $hasEnv -and -not $hasFile) {
        Write-Host "ERROR: Kaggle credentials not found."
        Write-Host "  Set KAGGLE_USERNAME and KAGGLE_KEY, or place kaggle.json in $kaggleJson"
        Write-Host "  Create API token: https://www.kaggle.com/settings -> Create New Token"
        exit 1
    }
} elseif (-not $hasEnv -and -not $hasFile) {
    Write-Host "WARNING: Kaggle credentials not found - Kaggle datasets will fail."
    Write-Host "  Set KAGGLE_USERNAME/KAGGLE_KEY or place kaggle.json in $kaggleJson"
}

Write-Host "==> Installing download dependencies..."
pip install -r ml/requirements-download.txt
if ($LASTEXITCODE -ne 0) { exit 1 }

$dlArgs = @()
if ($All) {
    $dlArgs += "--all"
} else {
    $dlArgs += "--legacy"
}
if ($IncludeLarge) {
    $dlArgs += "--include-large"
}
if ($Force) {
    $dlArgs += "--force"
}

Write-Host "==> Downloading ML datasets..."
python ml/scripts/download_all.py @dlArgs
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "ML data ready under ml/data/"
if (Test-Path "ml/data/manifest.json") {
    Write-Host "Manifest: ml/data/manifest.json"
}
