[CmdletBinding()]
param(
    [switch]$SplitPerAbi,
    [switch]$Clean,
    [string]$ApiBaseUrl = '',
    [string]$WsViajesUrl = ''
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if ($Clean) {
    & flutter clean
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$buildArgs = @('build', 'apk', '--release')
if ($SplitPerAbi) { $buildArgs += '--split-per-abi' }
if ($ApiBaseUrl) { $buildArgs += "--dart-define=API_BASE_URL=$ApiBaseUrl" }
if ($WsViajesUrl) { $buildArgs += "--dart-define=WS_VIAJES_URL=$WsViajesUrl" }

& flutter @buildArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$outputDir = Join-Path $PSScriptRoot 'build\app\outputs\flutter-apk'
$releaseApks = Get-ChildItem -Path $outputDir -Filter '*-release.apk' -File
if (-not $releaseApks) {
    throw "No se encontró ningún APK de release en $outputDir."
}

foreach ($apk in $releaseApks) {
    $targetName = if ($SplitPerAbi) {
        $abi = $apk.BaseName -replace '^app-', '' -replace '-release$', ''
        "APURADITO-$abi.apk"
    } else {
        'APURADITO.apk'
    }
    Copy-Item -LiteralPath $apk.FullName -Destination (Join-Path $outputDir $targetName) -Force
    Write-Host "APK generado: $(Join-Path $outputDir $targetName)"
}
