[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$localDir = $PSScriptRoot
$envFile = Join-Path $localDir '.env'
$composeFile = Join-Path $localDir 'compose.yaml'

if (-not (Test-Path $envFile)) {
    throw "Falta $envFile. No se puede identificar la configuracion local."
}

docker compose --env-file $envFile -f $composeFile down
