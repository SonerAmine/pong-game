@echo off
echo 🎮 Pong Force - Complete Download Setup
echo ======================================

echo 📋 This script will:
echo    1. Install Python and dependencies
echo    2. Build the game executable
echo    3. Set up download functionality
echo    4. Test the download process
echo.

echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo 📥 Please install Python first:
    echo    1. Go to: https://www.python.org/downloads/
    echo    2. Download Python 3.11 (latest)
    echo    3. Run installer and CHECK "Add Python to PATH"
    echo    4. Restart your computer
    echo    5. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

echo.
echo 📦 Installing game dependencies...
pip install pygame>=2.1.0
pip install pyinstaller>=5.0.0

echo.
echo 🔨 Building the game executable...
cd pong_force

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Build the executable
pyinstaller --onefile --windowed --name=PongForce --add-data="assets;assets" main.py

echo.
echo 📁 Copying executable to website assets...
cd ..
if exist "pong_force\dist\PongForce.exe" (
    copy "pong_force\dist\PongForce.exe" "assets\PongForceSetup.exe"
    echo ✅ Executable copied to website!
    echo.
    echo 🎮 Your game is now ready for download!
    echo.
    echo 📊 File information:
    for %%I in ("assets\PongForceSetup.exe") do echo    Size: %%~zI bytes
    echo    Location: %CD%\assets\PongForceSetup.exe
    echo.
    echo 🌐 To test:
    echo    1. Open index.html in your browser
    echo    2. Click "Download Now" button
    echo    3. The game will download to your PC
    echo    4. Run the downloaded .exe file to play!
) else (
    echo ❌ Build failed! Check the error messages above.
)

echo.
pause
