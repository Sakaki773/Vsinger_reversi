param(
    [ValidateSet("Debug", "Release")]
    [string]$Variant = "Debug",
    [switch]$SkipAssetSync
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$androidDir = Join-Path $projectRoot "android"

if (-not (Test-Path $androidDir)) {
    throw "未找到 Android 工程目录：$androidDir"
}

if (-not $SkipAssetSync) {
    powershell -ExecutionPolicy Bypass -File (Join-Path $projectRoot "sync_android_assets.ps1") -ProjectRoot $projectRoot
}

$task = if ($Variant -eq "Release") { "assembleRelease" } else { "assembleDebug" }
$wrapper = Join-Path $androidDir "gradlew.bat"

Push-Location $androidDir
try {
    if (Test-Path $wrapper) {
        & $wrapper $task
    } else {
        $gradle = Get-Command gradle -ErrorAction SilentlyContinue
        if ($null -eq $gradle) {
            throw "未找到 gradlew.bat 或系统 gradle。请先用 Android Studio 打开 android/ 工程并生成/使用 Gradle，或安装 Gradle 后重试。"
        }
        & gradle $task
    }
} finally {
    Pop-Location
}

$apkDir = Join-Path $androidDir "app\build\outputs\apk\$($Variant.ToLowerInvariant())"
Write-Host "构建完成。APK 输出目录：$apkDir"
