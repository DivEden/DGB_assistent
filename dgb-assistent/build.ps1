# PowerShell Build Script for Python Desktop Application
# This script packages the application into a standalone executable

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Python Desktop Application Builder" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Install/upgrade required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install required packages" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Build the application
Write-Host "Building application..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
pyinstaller --clean build.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The application has been packaged and is available in the 'dist' folder." -ForegroundColor Green
Write-Host "You can find the executable at: dist\PythonDesktopApp\PythonDesktopApp.exe" -ForegroundColor Green
Write-Host ""
Write-Host "The entire 'dist\PythonDesktopApp' folder can be copied to any Windows" -ForegroundColor Green
Write-Host "computer and run without requiring Python to be installed." -ForegroundColor Green
Write-Host ""

# Ask if user wants to run the application
$runApp = Read-Host "Would you like to run the application now? (y/n)"
if ($runApp -eq "y" -or $runApp -eq "Y") {
    Write-Host "Starting application..." -ForegroundColor Yellow
    Start-Process "dist\PythonDesktopApp\PythonDesktopApp.exe"
}

Write-Host ""
Read-Host "Press Enter to exit"