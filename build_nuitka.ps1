param(
    [string]$PythonExe = "C:\Users\admin\.conda\envs\envs2\python.exe",
    [string]$OutputDir = ".\dist",
    [switch]$OneFile,
    [switch]$LowMemory,
    [switch]$EnableConsole,
    [switch]$SkipStartupSelfCheck,
    [int]$Jobs = 0
)

$ErrorActionPreference = "Stop"

# Keep this script ASCII-only so Windows PowerShell 5.1 can parse it without a UTF-8 BOM.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Join-Path $env:TEMP "VsingerReversi_nuitka"
$StageDir = Join-Path $BuildRoot "source"
$EntryScript = Join-Path $StageDir "tk_run.py"

if ($ProjectRoot -cmatch '[^\x00-\x7F]') {
    throw "Project path contains non-ASCII characters. Rename or move the project to an English-only path before Nuitka build: $ProjectRoot"
}

if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    $ResolvedOutputDir = $OutputDir
} else {
    $ResolvedOutputDir = Join-Path $ProjectRoot $OutputDir
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $StageDir -Force | Out-Null
New-Item -ItemType Directory -Path $ResolvedOutputDir -Force | Out-Null

$files = @(
    "core.py",
    "tk_ui.py",
    "tk_run.py"
)

foreach ($file in $files) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $file) -Destination (Join-Path $StageDir $file) -Force
}

$picSource = Join-Path $ProjectRoot "pic"
$picTarget = Join-Path $StageDir "pic"
if (Test-Path -LiteralPath $picSource) {
    Copy-Item -LiteralPath $picSource -Destination $picTarget -Recurse -Force
}

& $PythonExe $EntryScript --self-check-imports
if ($LASTEXITCODE -ne 0) {
    throw "Tkinter import self-check failed."
}

$consoleMode = "disable"
if ($EnableConsole) {
    $consoleMode = "force"
}

$nuitkaArgs = @(
    "-m", "nuitka",
    "--standalone",
    "--assume-yes-for-downloads",
    "--windows-console-mode=$consoleMode",
    "--enable-plugin=tk-inter",
    "--noinclude-pytest-mode=nofollow",
    "--noinclude-unittest-mode=nofollow",
    "--noinclude-IPython-mode=nofollow",
    "--output-dir=$ResolvedOutputDir",
    "--output-filename=VsingerReversi.exe"
)

if (Test-Path -LiteralPath $picTarget) {
    $nuitkaArgs += "--include-data-dir=$picTarget=pic"
}

if ($OneFile) {
    $nuitkaArgs += "--onefile"
}

if ($LowMemory) {
    $nuitkaArgs += "--low-memory"
}

if ($Jobs -gt 0) {
    $nuitkaArgs += "--jobs=$Jobs"
}

$nuitkaArgs += $EntryScript

& $PythonExe @nuitkaArgs
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka build failed."
}

if (-not $SkipStartupSelfCheck) {
    $exePath = Join-Path $ResolvedOutputDir "tk_run.dist\VsingerReversi.exe"
    if ($OneFile) {
        $exePath = Join-Path $ResolvedOutputDir "VsingerReversi.exe"
    }
    if (Test-Path -LiteralPath $exePath) {
        Write-Host "Generated: $exePath"
    } else {
        Write-Host "Build finished, but EXE was not found at expected path: $exePath"
    }
}
