param(
    [string]$ProjectRoot = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

$sourceDir = Join-Path $ProjectRoot "pic"
$targetDir = Join-Path $ProjectRoot "android\app\src\main\res\drawable-nodpi"

if (-not (Test-Path $sourceDir)) {
    throw "Asset directory not found: $sourceDir"
}

New-Item -ItemType Directory -Force $targetDir | Out-Null

$assets = @(
    @{ Source = "background.png"; Target = "background.png" },
    @{ Source = "qizi0.png"; Target = "qizi0.png" },
    @{ Source = "qizi1.png"; Target = "qizi1.png" }
)

foreach ($asset in $assets) {
    $source = Join-Path $sourceDir $asset.Source
    $target = Join-Path $targetDir $asset.Target
    if (-not (Test-Path $source)) {
        throw "Asset file not found: $source"
    }
    Copy-Item -Force $source $target
    Write-Host "Synced $($asset.Source) -> android/app/src/main/res/drawable-nodpi/$($asset.Target)"
}
