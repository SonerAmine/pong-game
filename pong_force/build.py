#!/usr/bin/env python3
# ===== PONG FORCE - BUILD SCRIPT =====

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import pygame
        print(f"Pygame {pygame.version.ver} installed")
    except ImportError:
        print("Pygame not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygame>=2.1.0"])
    
    try:
        import PyInstaller
        print("PyInstaller installed")
    except ImportError:
        print("PyInstaller not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_icon():
    """Create a simple icon if none exists"""
    icon_path = "../assets/images/icon.ico"
    
    if not os.path.exists(icon_path):
        print("Creating default icon...")
        
        # Create a simple 32x32 icon using pygame
        try:
            import pygame
            pygame.init()
            
            # Create a simple icon surface
            icon_surface = pygame.Surface((32, 32))
            icon_surface.fill((11, 12, 16))  # Dark background
            
            # Draw a simple paddle and ball
            pygame.draw.rect(icon_surface, (0, 255, 255), (2, 10, 4, 12))  # Left paddle
            pygame.draw.rect(icon_surface, (255, 0, 204), (26, 10, 4, 12))  # Right paddle
            pygame.draw.circle(icon_surface, (255, 215, 0), (16, 16), 3)  # Ball
            
            # Save as PNG first
            png_path = "assets/images/icon.png"
            pygame.image.save(icon_surface, png_path)
            
            # Convert to ICO (this is a simplified approach)
            # In a real scenario, you'd use PIL or another library
            print(f"   Created {png_path}")
            
        except Exception as e:
            print(f"   Warning: Could not create icon: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=PongForce",             # Executable name
        "--add-data=assets;assets",     # Include assets folder
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=.",                 # Spec file location
        "main.py"                       # Main script
    ]
    
    # Add icon if it exists
    icon_paths = [
        os.path.join("..", "assets", "images", "icon.ico"),
        os.path.join("assets", "images", "icon.ico"),
        "icon.ico"
    ]
    icon_found = False
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
            print(f"   Using icon: {icon_path}")
            icon_found = True
            break
    
    if not icon_found:
        print("   Warning: No icon found, building without icon")
    
    # Add version info
    cmd.extend([
        "--version-file=version_info.txt"
    ])
    
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False

def create_version_info():
    """Create version info file for Windows"""
    version_info = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Pong Force Studios'),
        StringStruct(u'FileDescription', u'Pong Force - Revolutionary Pong with Force Push'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'PongForce'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'PongForce.exe'),
        StringStruct(u'ProductName', u'Pong Force'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open("version_info.txt", "w") as f:
        f.write(version_info)
    
    print("Created version_info.txt")

def test_executable():
    """Test the built executable"""
    exe_path = "dist/PongForce.exe"
    
    if os.path.exists(exe_path):
        print("Testing executable...")
        print(f"   Executable size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        print("Executable created successfully!")
        print(f"   Location: {os.path.abspath(exe_path)}")
        return True
    else:
        print("Executable not found!")
        return False

def create_installer():
    """Create a simple installer script"""
    installer_script = """@echo off
echo Installing Pong Force...
echo.

REM Create installation directory
if not exist "C:\\Program Files\\Pong Force" mkdir "C:\\Program Files\\Pong Force"

REM Copy executable
copy "PongForce.exe" "C:\\Program Files\\Pong Force\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Pong Force.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\Pong Force\\PongForce.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run Pong Force from your desktop or Start menu.
pause
"""
    
    with open("dist/install.bat", "w") as f:
        f.write(installer_script)
    
    print("Created installer script")

def main():
    """Main build process"""
    print("Pong Force - Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Error: main.py not found. Please run this script from the pong_force directory.")
        sys.exit(1)
    
    try:
        # Step 1: Check dependencies
        check_dependencies()
        
        # Step 2: Clean previous builds
        clean_build()
        
        # Step 3: Create icon
        create_icon()
        
        # Step 4: Create version info
        create_version_info()
        
        # Step 5: Build executable
        if build_executable():
            # Step 6: Test executable
            if test_executable():
                # Step 7: Create installer
                create_installer()
                
                print("\nBuild completed successfully!")
                print("\nFiles created:")
                print("   - dist/PongForce.exe (Main executable)")
                print("   - dist/install.bat (Installer script)")
                print("\nTo test the game:")
                print("   cd dist")
                print("   PongForce.exe --server")
                print("   PongForce.exe --client --host localhost")
                
            else:
                print("Build test failed!")
                sys.exit(1)
        else:
            print("Build failed!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Build error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
