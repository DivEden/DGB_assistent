@echo off
REM DGB Assistent Installation Script
REM Installerer DGB Assistent så det kan findes i Windows Start Menu

echo ========================================
echo    DGB Assistent Installation
echo ========================================
echo.

REM Check for administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo FEJL: Dette script skal køres som Administrator
    echo Højreklik på scriptet og vælg "Kør som administrator"
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\Program Files\DGB Assistent
echo Opretter installation mappe: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Kopierer DGB-Assistent.exe...
copy "dist\DGB-Assistent.exe" "%INSTALL_DIR%\DGB-Assistent.exe" /Y
if %errorlevel% neq 0 (
    echo FEJL: Kunne ikke kopiere executable
    pause
    exit /b 1
)

REM Create Start Menu shortcut for all users
set STARTMENU_DIR=C:\ProgramData\Microsoft\Windows\Start Menu\Programs
echo Opretter Start Menu genvej...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_DIR%\DGB Assistent.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\DGB-Assistent.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'DGB Assistent - Billedbehandling og Museum Organisering'; $Shortcut.Save()}"

REM Create Desktop shortcut (optional)
set /p desktop="Vil du have en Desktop genvej? (j/n): "
if /i "%desktop%"=="j" (
    echo Opretter Desktop genvej...
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Desktop = [Environment]::GetFolderPath('CommonDesktop'); $Shortcut = $WshShell.CreateShortcut('$Desktop\DGB Assistent.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\DGB-Assistent.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'DGB Assistent - Billedbehandling og Museum Organisering'; $Shortcut.Save()}"
)

REM Add to Windows Registry (for uninstall info)
echo Tilføjer til Windows Programs...
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /v "DisplayName" /t REG_SZ /d "DGB Assistent" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /v "DisplayVersion" /t REG_SZ /d "1.0.0" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /v "Publisher" /t REG_SZ /d "DivEden" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall.bat" /f >nul

REM Create uninstall script
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo echo Afinstallerer DGB Assistent... >> "%INSTALL_DIR%\uninstall.bat"
echo del "%STARTMENU_DIR%\DGB Assistent.lnk" /f /q >> "%INSTALL_DIR%\uninstall.bat"
echo del "%PUBLIC%\Desktop\DGB Assistent.lnk" /f /q 2^>nul >> "%INSTALL_DIR%\uninstall.bat"
echo reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\DGB Assistent" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo rd "%INSTALL_DIR%" /s /q >> "%INSTALL_DIR%\uninstall.bat"
echo echo DGB Assistent er afinstalleret. >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

echo.
echo ========================================
echo Installation fuldført!
echo ========================================
echo.
echo DGB Assistent er nu installeret og kan findes ved at:
echo 1. Trykke Windows-tasten og søge efter "DGB"
echo 2. Gå til Start Menu ^> Alle Apps ^> DGB Assistent
echo 3. Køre direkte fra: %INSTALL_DIR%\DGB-Assistent.exe
echo.
echo For at afinstallere: Kør %INSTALL_DIR%\uninstall.bat som administrator
echo.
pause