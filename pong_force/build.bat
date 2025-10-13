@echo off
echo 🎮 Pong Force - Build Script
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7+ and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
pip install pygame>=2.1.0
pip install pyinstaller>=5.0.0

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Build executable
echo 🔨 Building executable...
pyinstaller --onefile --windowed --name=PongForce --add-data="assets;assets" main.py

REM Check if build was successful
if exist dist\PongForce.exe (
    echo ✅ Build successful!
    echo 📁 Executable created: dist\PongForce.exe
    echo.
    echo 🚀 To test the game:
    echo    cd dist
    echo    PongForce.exe --server
    echo    PongForce.exe --client --host localhost
) else (
    echo ❌ Build failed!
    echo Please check the error messages above.
)

pause
