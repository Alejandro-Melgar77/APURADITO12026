[CmdletBinding()]
param(
    [switch]$Build,
    [switch]$Ai
)

$ErrorActionPreference = 'Stop'
$localDir = $PSScriptRoot
$envFile = Join-Path $localDir '.env'
$composeFile = Join-Path $localDir 'compose.yaml'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop no esta instalado o no esta disponible en PATH.'
}

if (-not (Test-Path $envFile)) {
    throw "Falta $envFile. Copia .env.example como .env y reemplaza LOCAL_SECRET_KEY."
}

$composeArgs = @('compose', '--env-file', $envFile, '-f', $composeFile)
if ($Ai) { $composeArgs += @('--profile', 'ai') }
$composeArgs += @('up', '--detach')
if ($Build) { $composeArgs += '--build' }

& docker @composeArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Servicios iniciados:'
Write-Host '  Frontend: http://localhost:5173'
Write-Host '  API:      http://localhost:8000/health'
Write-Host '  Docs:     http://localhost:8000/docs'
if ($Ai) {
    Write-Host '  OCR IA:   http://localhost:8011/health'
    Write-Host '  Facial:   http://localhost:8012/health'
    Write-Host '  Rutas IA: http://localhost:8013/health'
}
