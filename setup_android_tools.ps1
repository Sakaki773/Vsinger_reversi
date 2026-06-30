param(
    [string]$ProjectRoot = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

$toolsDir = Join-Path $ProjectRoot ".android-tools"
$downloadsDir = Join-Path $toolsDir "downloads"
$jdkDir = Join-Path $toolsDir "jdk"
$gradleDir = Join-Path $toolsDir "gradle"
$sdkRoot = Join-Path $toolsDir "android-sdk"
$cmdlineRoot = Join-Path $sdkRoot "cmdline-tools"
$cmdlineLatest = Join-Path $cmdlineRoot "latest"

$jdkUrl = "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.zip"
$gradleVersion = "9.2.1"
$gradleUrl = "https://services.gradle.org/distributions/gradle-$gradleVersion-bin.zip"
$cmdlineUrl = "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip"

New-Item -ItemType Directory -Force $downloadsDir, $jdkDir, $gradleDir, $sdkRoot, $cmdlineRoot | Out-Null

function Download-FileIfMissing {
    param(
        [string]$Url,
        [string]$Path
    )

    if ((Test-Path $Path) -and (Test-ZipArchive $Path)) {
        Write-Host "Using cached download: $Path"
        return
    }

    if (Test-Path $Path) {
        Write-Host "Removing incomplete download: $Path"
        Remove-Item -Force $Path
    }

    Write-Host "Downloading: $Url"
    $systemCurl = Join-Path $env:WINDIR "System32\curl.exe"
    $curl = if (Test-Path $systemCurl) { $systemCurl } else { (Get-Command curl.exe -ErrorAction SilentlyContinue).Source }
    if ($null -ne $curl) {
        & $curl --fail --location --retry 5 --retry-delay 3 --output $Path $Url
    } else {
        Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path
    }

    if (-not (Test-ZipArchive $Path)) {
        throw "Downloaded archive is not a valid zip: $Path"
    }
}

function Expand-ZipFresh {
    param(
        [string]$ZipPath,
        [string]$TargetDir
    )

    if (Test-Path $TargetDir) {
        Remove-Item -Recurse -Force $TargetDir
    }
    New-Item -ItemType Directory -Force $TargetDir | Out-Null
    Expand-Archive -Force -Path $ZipPath -DestinationPath $TargetDir
}

function Test-ZipArchive {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return $false
    }
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
        $zip.Dispose()
        return $true
    } catch {
        return $false
    }
}

function Get-FirstChildDirectory {
    param([string]$Path)
    return Get-ChildItem -Path $Path -Directory | Select-Object -First 1
}

$jdkZip = Join-Path $downloadsDir "temurin-17-jdk.zip"
$gradleZip = Join-Path $downloadsDir "gradle-$gradleVersion-bin.zip"
$cmdlineZip = Join-Path $downloadsDir "commandlinetools-win-latest.zip"

if (-not (Test-Path (Join-Path $jdkDir "bin\java.exe"))) {
    Download-FileIfMissing $jdkUrl $jdkZip
    $jdkExtract = Join-Path $toolsDir "jdk-extract"
    Expand-ZipFresh $jdkZip $jdkExtract
    $jdkHome = Get-FirstChildDirectory $jdkExtract
    if ($null -eq $jdkHome) {
        throw "JDK archive did not contain a top-level directory."
    }
    if (Test-Path $jdkDir) {
        Remove-Item -Recurse -Force $jdkDir
    }
    Move-Item -Path $jdkHome.FullName -Destination $jdkDir
    Remove-Item -Recurse -Force $jdkExtract
}

if (-not (Test-Path (Join-Path $gradleDir "bin\gradle.bat"))) {
    Download-FileIfMissing $gradleUrl $gradleZip
    $gradleExtract = Join-Path $toolsDir "gradle-extract"
    Expand-ZipFresh $gradleZip $gradleExtract
    $gradleHome = Get-FirstChildDirectory $gradleExtract
    if ($null -eq $gradleHome) {
        throw "Gradle archive did not contain a top-level directory."
    }
    if (Test-Path $gradleDir) {
        Remove-Item -Recurse -Force $gradleDir
    }
    Move-Item -Path $gradleHome.FullName -Destination $gradleDir
    Remove-Item -Recurse -Force $gradleExtract
}

if (-not (Test-Path (Join-Path $cmdlineLatest "bin\sdkmanager.bat"))) {
    Download-FileIfMissing $cmdlineUrl $cmdlineZip
    $cmdlineExtract = Join-Path $toolsDir "cmdline-extract"
    Expand-ZipFresh $cmdlineZip $cmdlineExtract
    $inner = Join-Path $cmdlineExtract "cmdline-tools"
    if (-not (Test-Path $inner)) {
        throw "Android command line tools archive layout was not recognized."
    }
    if (Test-Path $cmdlineLatest) {
        Remove-Item -Recurse -Force $cmdlineLatest
    }
    New-Item -ItemType Directory -Force $cmdlineRoot | Out-Null
    Move-Item -Path $inner -Destination $cmdlineLatest
    Remove-Item -Recurse -Force $cmdlineExtract
}

$env:JAVA_HOME = $jdkDir
$env:ANDROID_HOME = $sdkRoot
$env:ANDROID_SDK_ROOT = $sdkRoot
$env:Path = "$(Join-Path $jdkDir 'bin');$(Join-Path $gradleDir 'bin');$(Join-Path $cmdlineLatest 'bin');$(Join-Path $sdkRoot 'platform-tools');$env:Path"

$sdkManager = Join-Path $cmdlineLatest "bin\sdkmanager.bat"

Write-Host "Accepting Android SDK licenses."
1..100 | ForEach-Object { "y" } | & $sdkManager --sdk_root=$sdkRoot --licenses

Write-Host "Installing Android SDK packages."
& $sdkManager --sdk_root=$sdkRoot `
    "platform-tools" `
    "platforms;android-36" `
    "build-tools;36.0.0"

Write-Host "Android local tools are ready."
Write-Host "JAVA_HOME=$jdkDir"
Write-Host "ANDROID_SDK_ROOT=$sdkRoot"
Write-Host "Gradle=$(Join-Path $gradleDir 'bin\gradle.bat')"
