[CmdletBinding()]
param(
    [ValidateSet('postgres', 'redis', 'backend', 'frontend')]
    [string]$Service
)

$ErrorActionPreference = 'Stop'
$localDir = $PSScriptRoot
$envFile = Join-Path $localDir '.env'
$composeFile = Join-Path $localDir 'compose.yaml'

if (-not (Test-Path $envFile)) {
    throw "Falta $envFile."
}

if ($Service) {
    docker compose --env-file $envFile -f $composeFile logs --follow $Service
} else {
    docker compose --env-file $envFile -f $composeFile logs --follow
}
