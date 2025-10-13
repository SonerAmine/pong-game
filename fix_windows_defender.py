#!/usr/bin/env python3
"""
Script pour résoudre les problèmes de Windows Defender avec Pong Force
"""

import os
import sys
import subprocess
from pathlib import Path

def create_code_signing_certificate():
    """Créer un certificat auto-signé pour signer l'exécutable"""
    print("Creating self-signed certificate for code signing...")
    
    cert_script = """
# Créer un certificat auto-signé
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Pong Force Studios" -KeyUsage DigitalSignature -FriendlyName "Pong Force Code Signing" -CertStoreLocation "Cert:\CurrentUser\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Exporter le certificat
$certPath = "pong_force_cert.pfx"
$password = ConvertTo-SecureString -String "PongForce2024!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $password

Write-Host "Certificate created: $certPath"
Write-Host "Password: PongForce2024!"
"""
    
    with open("create_cert.ps1", "w") as f:
        f.write(cert_script)
    
    print("Certificate creation script created: create_cert.ps1")
    print("Run this script in PowerShell as Administrator to create the certificate.")

def sign_executable():
    """Signer l'exécutable avec le certificat"""
    exe_path = "assets/PongForceSetup.exe"
    cert_path = "pong_force_cert.pfx"
    
    if not os.path.exists(exe_path):
        print(f"ERROR: {exe_path} not found!")
        return False
    
    if not os.path.exists(cert_path):
        print(f"ERROR: {cert_path} not found!")
        print("Please run create_cert.ps1 first to create the certificate.")
        return False
    
    print("Signing executable...")
    
    sign_script = f"""
# Signer l'exécutable
$certPath = "{cert_path}"
$exePath = "{exe_path}"
$password = ConvertTo-SecureString -String "PongForce2024!" -Force -AsPlainText

# Importer le certificat
$cert = Import-PfxCertificate -FilePath $certPath -CertStoreLocation "Cert:\CurrentUser\My" -Password $password

# Signer l'exécutable
Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert

Write-Host "Executable signed successfully!"
"""
    
    with open("sign_exe.ps1", "w") as f:
        f.write(sign_script)
    
    print("Signing script created: sign_exe.ps1")
    print("Run this script in PowerShell as Administrator to sign the executable.")

def create_installer_script():
    """Créer un script d'installation qui évite les problèmes de Windows Defender"""
    installer_script = """@echo off
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
set "INSTALL_DIR=C:\\Program Files\\Pong Force"
if not exist "%INSTALL_DIR%" (
    echo Creating installation directory...
    mkdir "%INSTALL_DIR%"
)

REM Copier l'exécutable
echo Copying game files...
copy "PongForceSetup.exe" "%INSTALL_DIR%\\PongForce.exe"

REM Créer un raccourci sur le bureau
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Pong Force.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\PongForce.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Pong Force - Revolutionary Pong Game'; $Shortcut.Save()"

REM Créer un raccourci dans le menu Démarrer
echo Creating Start Menu shortcut...
set "START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
if not exist "%START_MENU%\\Pong Force" mkdir "%START_MENU%\\Pong Force"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\\Pong Force\\Pong Force.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\PongForce.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Pong Force - Revolutionary Pong Game'; $Shortcut.Save()"

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
echo - %INSTALL_DIR%\\PongForce.exe
echo.
echo If Windows Defender still blocks the game:
echo 1. Open Windows Security
echo 2. Go to Virus & threat protection
echo 3. Click "Manage settings" under Virus & threat protection settings
echo 4. Click "Add or remove exclusions"
echo 5. Add folder: %INSTALL_DIR%
echo.
pause
"""
    
    with open("install_pong_force.bat", "w") as f:
        f.write(installer_script)
    
    print("Installer script created: install_pong_force.bat")

def create_readme_for_users():
    """Créer un README pour les utilisateurs expliquant le problème Windows Defender"""
    readme_content = """# Pong Force - Installation Guide

## 🛡️ Windows Defender Warning

If Windows Defender shows a warning about Pong Force being a threat, this is a **false positive**. This is common with games created using PyInstaller.

### Why does this happen?
- PyInstaller packages Python applications into executables
- Windows Defender sometimes flags these as suspicious
- This is a known issue with many legitimate applications

### How to fix it:

#### Method 1: Use the installer script
1. Run `install_pong_force.bat` as Administrator
2. This will install the game properly and add Windows Defender exceptions

#### Method 2: Manual Windows Defender exception
1. Open Windows Security (Windows Defender)
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Click "Add or remove exclusions"
5. Click "Add an exclusion" → "Folder"
6. Add the folder where you extracted Pong Force

#### Method 3: Temporary disable real-time protection
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Turn off "Real-time protection" temporarily
5. Run Pong Force
6. Turn "Real-time protection" back on

### Is Pong Force safe?
✅ **YES!** Pong Force is completely safe:
- Open source code
- No malicious functionality
- Created with standard Python/Pygame tools
- No network connections (except for multiplayer)
- No data collection

### Game Features:
- 2-Player Multiplayer (Local & LAN)
- Force Push Mechanics
- Neon Arcade Visuals
- Particle Effects
- Sound System
- Network Play

### Controls:
- **Player 1**: Arrow Keys (move), SPACE (force push)
- **Player 2**: W/S (move), SHIFT (force push)
- **General**: ESC (pause), R (restart)

Enjoy the game! 🎮
"""
    
    with open("WINDOWS_DEFENDER_FIX.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("User guide created: WINDOWS_DEFENDER_FIX.txt")

def main():
    """Main function to set up Windows Defender fixes"""
    print("Pong Force - Windows Defender Fix Setup")
    print("=" * 50)
    
    # Créer le certificat de signature
    create_code_signing_certificate()
    
    # Créer le script de signature
    sign_executable()
    
    # Créer le script d'installation
    create_installer_script()
    
    # Créer le guide utilisateur
    create_readme_for_users()
    
    print("\n" + "=" * 50)
    print("Windows Defender Fix Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run 'create_cert.ps1' in PowerShell as Administrator")
    print("2. Run 'sign_exe.ps1' in PowerShell as Administrator")
    print("3. Include 'install_pong_force.bat' with your download")
    print("4. Include 'WINDOWS_DEFENDER_FIX.txt' with your download")
    print("\nThis will help users avoid Windows Defender false positives.")

if __name__ == "__main__":
    main()
