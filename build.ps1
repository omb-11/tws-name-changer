# build.ps1 - Automated build and release script for TWS Name Changer
param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = $PSScriptRoot
Set-Location $WorkspaceRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  TWS Name Changer - Windows 11 Build & Release Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Virtual Environment
$VenvPython = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found at $VenvPython. Run python -m venv .venv first."
}
Write-Host "[1/6] Using Python: $VenvPython" -ForegroundColor Green

# 2. Run Tests and Bytecode Compilation
if (-not $SkipTests) {
    Write-Host "[2/6] Running pytest test suite..." -ForegroundColor Green
    & $VenvPython -m pytest -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Pytest test suite failed with exit code $LASTEXITCODE."
    }

    Write-Host "[2b/6] Validating bytecode compilation (compileall)..." -ForegroundColor Green
    & $VenvPython -m compileall -q .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Bytecode compilation failed with exit code $LASTEXITCODE."
    }
} else {
    Write-Host "[2/6] Tests skipped by request." -ForegroundColor Yellow
}

# 3. Clean previous build artifacts
Write-Host "[3/6] Cleaning build and dist folders..." -ForegroundColor Green
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\TWSNameChanger.exe") { Remove-Item -Force "dist\TWSNameChanger.exe" }

# 4. Run PyInstaller
Write-Host "[4/6] Packaging with PyInstaller via virtual environment..." -ForegroundColor Green
& $VenvPython -m PyInstaller TWSNameChanger.spec --clean
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed with exit code $LASTEXITCODE."
}

# 5. Verify Build Artifact
$ExePath = Join-Path $WorkspaceRoot "dist\TWSNameChanger.exe"
if (-not (Test-Path $ExePath)) {
    Write-Error "Expected build artifact $ExePath was not found!"
}

$ExeItem = Get-Item $ExePath
$SizeMB = [math]::Round($ExeItem.Length / 1MB, 2)
Write-Host "[5/6] Build artifact verified: $ExePath ($SizeMB MB)" -ForegroundColor Green

# Quick startup validation
Write-Host "[5b/6] Running executable startup verification..." -ForegroundColor Green
& $VenvPython verify_exe.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Packaged executable failed verification!"
}

# 6. Check for Inno Setup compiler
Write-Host "[6/6] Checking for Inno Setup compiler (ISCC.exe)..." -ForegroundColor Green
$IsccPaths = @(
    "iscc.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$IsccFound = $null
foreach ($p in $IsccPaths) {
    if (Get-Command $p -ErrorAction SilentlyContinue) {
        $IsccFound = $p
        break
    } elseif (Test-Path $p) {
        $IsccFound = $p
        break
    }
}

if ($IsccFound) {
    Write-Host "Inno Setup found at $IsccFound. Compiling setup installer..." -ForegroundColor Green
    & $IsccFound "installer\setup.iss"
    Write-Host "Setup installer created: dist\installer\TWSNameChanger-Setup.exe" -ForegroundColor Green
} else {
    Write-Host "Inno Setup (ISCC.exe) is not installed on this system." -ForegroundColor Yellow
    Write-Host "Portable standalone executable is ready at: dist\TWSNameChanger.exe" -ForegroundColor Green
    Write-Host "To produce an installer, install Inno Setup 6 and run: iscc.exe installer\setup.iss" -ForegroundColor Yellow
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE AND VERIFIED!" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
