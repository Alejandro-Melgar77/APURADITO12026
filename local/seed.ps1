[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$localDir = $PSScriptRoot
$envFile = Join-Path $localDir '.env'
$composeFile = Join-Path $localDir 'compose.yaml'

if (-not (Test-Path $envFile)) {
    throw "Falta $envFile."
}

docker compose --env-file $envFile -f $composeFile exec backend python -m seeds.run_all
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Datos de demostracion cargados. Administrador: admin@apuradito.bo'
