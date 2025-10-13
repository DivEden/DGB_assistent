@echo off
REM Build script for Python Desktop Application
REM This script packages the application into a standalone executable

echo ========================================
echo    Python Desktop Application Builder
echo ========================================
echo.

REM Check if Python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade required packages
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build the application
echo Building application...
echo This may take a few minutes...
pyinstaller --clean build.spec

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The application has been packaged and is available in the 'dist' folder.
echo You can find the executable at: dist\PythonDesktopApp\PythonDesktopApp.exe
echo.
echo The entire 'dist\PythonDesktopApp' folder can be copied to any Windows
echo computer and run without requiring Python to be installed.
echo.

REM Ask if user wants to run the application
set /p run_app="Would you like to run the application now? (y/n): "
if /i "%run_app%"=="y" (
    echo Starting application...
    start "" "dist\PythonDesktopApp\PythonDesktopApp.exe"
)

echo.
pause