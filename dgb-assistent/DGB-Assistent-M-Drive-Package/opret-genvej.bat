@echo off
REM DGB Assistent - Sikker Genvej Generator
REM Dette script hjælper brugere med at oprette genveje uden at flytte den originale fil

title DGB Assistent - Opret Desktop Genvej

echo ========================================
echo    DGB Assistent - Opret Desktop Genvej
echo ========================================
echo.
echo Dette script opretter en GENVEJ til DGB Assistent på dit skrivebord
echo UDEN at flytte den originale fil fra M: drevet.
echo.

REM Check om DGB Assistent findes på M: drev
set M_DRIVE_PATH=M:\DGB-Assistent\DGB-Assistent.exe

if not exist "%M_DRIVE_PATH%" (
    echo FEJL: DGB-Assistent blev ikke fundet på M: drevet
    echo Forventet placering: %M_DRIVE_PATH%
    echo.
    echo Kontakt IT support for at få DGB Assistent installeret på M: drevet
    pause
    exit /b 1
)

echo DGB Assistent fundet på: %M_DRIVE_PATH%
echo.

REM Check om der allerede er en desktop genvej
set DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\DGB Assistent.lnk

if exist "%DESKTOP_SHORTCUT%" (
    echo Der findes allerede en desktop genvej til DGB Assistent
    set /p overwrite="Vil du overskrive den eksisterende genvej? (j/n): "
    if /i not "%overwrite%"=="j" (
        echo Ingen ændringer foretaget.
        pause
        exit /b 0
    )
)

REM Opret desktop genvej
echo Opretter desktop genvej...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = '%M_DRIVE_PATH%'; $Shortcut.WorkingDirectory = 'M:\DGB-Assistent'; $Shortcut.Description = 'DGB Assistent - Billedbehandling og Museum Organisering (Fra M: drev)'; $Shortcut.IconLocation = '%M_DRIVE_PATH%,0'; $Shortcut.Save()}"

if exist "%DESKTOP_SHORTCUT%" (
    echo.
    echo ========================================
    echo Desktop genvej oprettet succesfuldt!
    echo ========================================
    echo.
    echo Du kan nu finde "DGB Assistent" på dit skrivebord
    echo Genvejen peger på: %M_DRIVE_PATH%
    echo.
    echo VIGTIGT: Dette er kun en GENVEJ - den originale fil
    echo forbliver sikkert på M: drevet hvor alle kan bruge den.
) else (
    echo FEJL: Kunne ikke oprette desktop genvej
    echo Prøv at køre dette script som administrator
)

echo.
pause