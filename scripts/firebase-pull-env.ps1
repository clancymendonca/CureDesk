# Pull Firebase web SDK config into client .env files via Firebase CLI
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$WebAppId = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command firebase -ErrorAction SilentlyContinue)) {
    $firebase = "npx --yes firebase-tools@13.29.1"
} else {
    $firebase = "firebase"
}

Write-Host "==> Firebase login (browser) if needed..."
Invoke-Expression "$firebase login"

Write-Host "==> Using project $ProjectId"
Invoke-Expression "$firebase use $ProjectId"

if (-not $WebAppId) {
    Write-Host "Listing web apps..."
    Invoke-Expression "$firebase apps:list WEB --project $ProjectId"
    $WebAppId = Read-Host "Enter Web App ID (from list above)"
}

Write-Host "==> Fetching SDK config..."
$jsonRaw = Invoke-Expression "$firebase apps:sdkconfig WEB $WebAppId --project $ProjectId --json"
$json = $jsonRaw | ConvertFrom-Json
$cfg = $json.result.sdkConfig

$webEnv = @"
NEXT_PUBLIC_FIREBASE_API_KEY=$($cfg.apiKey)
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$($cfg.authDomain)
NEXT_PUBLIC_FIREBASE_PROJECT_ID=$($cfg.projectId)
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$($cfg.storageBucket)
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$($cfg.messagingSenderId)
NEXT_PUBLIC_FIREBASE_APP_ID=$($cfg.appId)
NEXT_PUBLIC_API_URL=http://localhost:8000
"@

$mobileEnv = @"
EXPO_PUBLIC_FIREBASE_API_KEY=$($cfg.apiKey)
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=$($cfg.authDomain)
EXPO_PUBLIC_FIREBASE_PROJECT_ID=$($cfg.projectId)
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=$($cfg.storageBucket)
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$($cfg.messagingSenderId)
EXPO_PUBLIC_FIREBASE_APP_ID=$($cfg.appId)
EXPO_PUBLIC_API_URL=http://localhost:8000
"@

New-Item -ItemType Directory -Force -Path apps\web | Out-Null
New-Item -ItemType Directory -Force -Path apps\mobile | Out-Null
Set-Content -Path apps\web\.env.local -Value $webEnv -Encoding utf8
Set-Content -Path apps\mobile\.env -Value $mobileEnv -Encoding utf8

Write-Host "Wrote apps/web/.env.local and apps/mobile/.env"
Write-Host ""
Write-Host "Service account for API (run separately):"
Write-Host "  gcloud iam service-accounts keys create firebase-sa.json --iam-account=firebase-adminsdk-XXXX@$ProjectId.iam.gserviceaccount.com"
Write-Host "  Then set FIREBASE_SERVICE_ACCOUNT_JSON in services/api/.env to that file path"
