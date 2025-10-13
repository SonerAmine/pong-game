@echo off
echo ========================================
echo   Pong Force - Installation Script
echo ========================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo WARNING: Not running as administrator
    echo Some features may not work properly.
    echo.
)

echo Installing Pong Force...
echo.

REM Créer le dossier d'installation
set "INSTALL_DIR=C:\Program Files\Pong Force"
if not exist "%INSTALL_DIR%" (
    echo Creating installation directory...
    mkdir "%INSTALL_DIR%"
)

REM Copier l'exécutable
echo Copying game files...
copy "PongForceSetup.exe" "%INSTALL_DIR%\PongForce.exe"

REM Créer un raccourci sur le bureau
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Pong Force.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\PongForce.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Pong Force - Revolutionary Pong Game'; $Shortcut.Save()"

REM Créer un raccourci dans le menu Démarrer
echo Creating Start Menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU%\Pong Force" mkdir "%START_MENU%\Pong Force"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Pong Force\Pong Force.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\PongForce.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Pong Force - Revolutionary Pong Game'; $Shortcut.Save()"

REM Ajouter une exception Windows Defender (si possible)
echo Adding Windows Defender exception...
powershell "Add-MpPreference -ExclusionPath '%INSTALL_DIR%'" 2>nul
if %errorLevel% == 0 (
    echo Windows Defender exception added successfully.
) else (
    echo Could not add Windows Defender exception automatically.
    echo Please add %INSTALL_DIR% to Windows Defender exclusions manually.
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Pong Force has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo Start Menu shortcut created.
echo.
echo You can now run Pong Force from:
echo - Desktop shortcut
echo - Start Menu
echo - %INSTALL_DIR%\PongForce.exe
echo.
echo If Windows Defender still blocks the game:
echo 1. Open Windows Security
echo 2. Go to Virus & threat protection
echo 3. Click "Manage settings" under Virus & threat protection settings
echo 4. Click "Add or remove exclusions"
echo 5. Add folder: %INSTALL_DIR%
echo.
pause
