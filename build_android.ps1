param(
    [ValidateSet("Debug", "Release")]
    [string]$Variant = "Debug",
    [switch]$SkipAssetSync
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$androidDir = Join-Path $projectRoot "android"
$localToolsDir = Join-Path $projectRoot ".android-tools"
$localJdkDir = Join-Path $localToolsDir "jdk"
$localGradle = Join-Path $localToolsDir "gradle\bin\gradle.bat"
$localSdkRoot = Join-Path $localToolsDir "android-sdk"
$localSdkManager = Join-Path $localSdkRoot "cmdline-tools\latest\bin\sdkmanager.bat"

if (-not (Test-Path $androidDir)) {
    throw "Android project directory not found: $androidDir"
}

if (Test-Path (Join-Path $localJdkDir "bin\java.exe")) {
    $env:JAVA_HOME = $localJdkDir
    $env:Path = "$(Join-Path $localJdkDir 'bin');$env:Path"
}

if (Test-Path $localSdkManager) {
    $env:ANDROID_HOME = $localSdkRoot
    $env:ANDROID_SDK_ROOT = $localSdkRoot
    $env:Path = "$(Join-Path $localSdkRoot 'platform-tools');$env:Path"
}

$task = if ($Variant -eq "Release") { "assembleRelease" } else { "assembleDebug" }
$wrapper = Join-Path $androidDir "gradlew.bat"
$gradleCommand = $null

if (Test-Path $wrapper) {
    $gradleCommand = $wrapper
} elseif (Test-Path $localGradle) {
    $gradleCommand = $localGradle
} else {
    $systemGradle = Get-Command gradle -ErrorAction SilentlyContinue
    if ($null -ne $systemGradle) {
        $gradleCommand = "gradle"
    }
}

if ($null -eq $gradleCommand) {
    Write-Host "Android build tools are not ready."
    Write-Host "Missing: android/gradlew.bat, local .android-tools Gradle, or system gradle command."
    Write-Host "Fix: run .\setup_android_tools.ps1, open android/ with Android Studio, or install Gradle and ensure 'gradle -v' works."
    Write-Host "Python envs such as envs2 do not provide Android build tools."
    exit 1
}

if (-not $SkipAssetSync) {
    powershell -ExecutionPolicy Bypass -File (Join-Path $projectRoot "sync_android_assets.ps1") -ProjectRoot $projectRoot
}

Push-Location $androidDir
try {
    if ($gradleCommand -eq $wrapper -or $gradleCommand -eq $localGradle) {
        & $gradleCommand $task
    } else {
        & $gradleCommand $task
    }
} finally {
    Pop-Location
}

$apkDir = Join-Path $androidDir "app\build\outputs\apk\$($Variant.ToLowerInvariant())"
Write-Host "Build finished. APK output directory: $apkDir"
