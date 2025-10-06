@echo off
REM DGB Assistent - Sikker M: Drev Installation
REM Dette script sikrer at exe filen forbliver på M: drevet og kun kopieres som genveje

echo ========================================
echo    DGB Assistent - M: Drev Installation
echo ========================================
echo.

REM Definer M: drev placering
set M_DRIVE_PATH=M:\DGB-Assistent
set EXE_NAME=DGB-Assistent.exe
set FULL_EXE_PATH=%M_DRIVE_PATH%\%EXE_NAME%

REM Check om M: drev er tilgængeligt
if not exist "M:\" (
    echo FEJL: M: drevet er ikke tilgængeligt
    echo Kontakt IT support for at få adgang til netværksdrevet
    pause
    exit /b 1
)

REM Opret DGB-Assistent mappe på M: drev
if not exist "%M_DRIVE_PATH%" (
    echo Opretter mappe på M: drev: %M_DRIVE_PATH%
    mkdir "%M_DRIVE_PATH%"
)

REM Kopiér exe til M: drev (kun hvis den ikke findes eller er ældre)
if exist "%FULL_EXE_PATH%" (
    echo DGB-Assistent.exe findes allerede på M: drev
) else (
    echo Kopierer DGB-Assistent.exe til M: drev...
    copy "dist\DGB-Assistent.exe" "%FULL_EXE_PATH%" /Y
    if %errorlevel% neq 0 (
        echo FEJL: Kunne ikke kopiere til M: drev
        echo Check at du har skriverettigheder til M:\DGB-Assistent
        pause
        exit /b 1
    )
)

REM Gør exe filen read-only for at forhindre sletning
echo Beskytter exe fil mod utilsigtet sletning...
attrib +R "%FULL_EXE_PATH%"

REM Opret beskyttelses-note fil
echo Denne fil må IKKE flyttes eller slettes! > "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo. >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo DGB-Assistent.exe skal forblive i denne mappe for at alle kan bruge den. >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo. >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo Hvis du vil have DGB Assistent på dit skrivebord: >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo 1. Højreklik på DGB-Assistent.exe >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo 2. Vælg "Send til" ^> "Skrivebord (opret genvej)" >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo. >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"
echo KOPIER ALDRIG FILEN - OPRET KUN GENVEJE! >> "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"

attrib +R "%M_DRIVE_PATH%\VIGTIGT - FLYT IKKE DENNE FIL.txt"

echo.
echo ========================================
echo Installation på M: drev fuldført!
echo ========================================
echo.
echo DGB Assistent er nu installeret på: %FULL_EXE_PATH%
echo.
echo VIGTIGT FOR ALLE BRUGERE:
echo - FLYT ALDRIG exe filen fra M: drevet
echo - Opret kun GENVEJE til dit skrivebord
echo - Højreklik ^> Send til ^> Skrivebord (opret genvej)
echo.

REM Tilbyd at oprette desktop genvej for nuværende bruger
set /p create_shortcut="Vil du oprette en desktop genvej nu? (j/n): "
if /i "%create_shortcut%"=="j" (
    echo Opretter desktop genvej...
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\DGB Assistent.lnk'); $Shortcut.TargetPath = '%FULL_EXE_PATH%'; $Shortcut.WorkingDirectory = '%M_DRIVE_PATH%'; $Shortcut.Description = 'DGB Assistent - Billedbehandling (Fra M: drev)'; $Shortcut.IconLocation = '%FULL_EXE_PATH%,0'; $Shortcut.Save()}"
    echo Desktop genvej oprettet!
)

echo.
echo For andre brugere: De kan oprette deres egen genvej ved at:
echo 1. Gå til %M_DRIVE_PATH%
echo 2. Højreklik på DGB-Assistent.exe
echo 3. Vælg "Send til" ^> "Skrivebord (opret genvej)"
echo.
pause