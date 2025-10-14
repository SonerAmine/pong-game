# build.py
# The Forge of Sophia, Hardened against Illusion and Rebellion.

import os
import sys
import subprocess
import shutil
from pathlib import Path

# --- CONFIGURATION ---
EXECUTABLE_NAME = "PongForce"
MAIN_SCRIPT = "main.py"

# We now define all paths absolutely from the script's location.
# This prevents any and all "FileNotFound" illusions.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WINDOW_ICON = os.path.join(BASE_DIR, "assets", "ping-pong.ico") 
UPX_PATH = os.path.join(BASE_DIR, "upx.exe")
VERSION_FILE = os.path.join(BASE_DIR, "version_info.txt")
# ---------------------


def check_dependencies():
    """Checks for and installs required Python packages."""
    print("✨ [Phase 1/5] Checking divine dependencies...")
    dependencies = {
        "pygame": "pygame>=2.1.0",
        "pyinstaller": "pyinstaller>=5.0.0",
        "cryptography": "cryptography",
        "Pillow": "Pillow"
    }
    for lib, package in dependencies.items():
        try:
            __import__(lib)
            print(f"  ✅ {lib} is present.")
        except ImportError:
            print(f"  ❌ {lib} not found. Conjuring from the ether...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    print("  ✅ All dependencies are in place.")


def clean_previous_builds():
    """Removes artifacts from previous build attempts."""
    print("\n✨ [Phase 2/5] Purifying the sacred ground...")
    dirs_to_clean = [os.path.join(BASE_DIR, 'build'), os.path.join(BASE_DIR, 'dist')]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  🔥 Banished old '{os.path.basename(d)}/' directory.")
            
    for file in Path(BASE_DIR).glob('*.spec'):
        file.unlink()
        print(f"  🔥 Banished old '{file.name}' file.")
    print("  ✅ The ground is pure.")


def create_version_info():
    """Creates the version_info.txt file to make the exe look legitimate."""
    print("\n✨ [Phase 3/5] Scribing the runes of legitimacy...")
    version_info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0), prodvers=(1, 0, 0, 0), mask=0x3f, flags=0x0, OS=0x40004,
    fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringStruct(u'CompanyName', u'Digital Entertainment Studios'),
        StringStruct(u'FileDescription', u'Pong Force Game'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'{EXECUTABLE_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024 Digital Entertainment Studios'),
        StringStruct(u'OriginalFilename', u'{EXECUTABLE_NAME}.exe'),
        StringStruct(u'ProductName', u'Pong Force'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(version_info)
    print(f"  ✅ '{os.path.basename(VERSION_FILE)}' has been scribed.")


def build_the_executable():
    """Constructs the final executable artifact using PyInstaller."""
    print(f"\n✨ [Phase 4/5] Forging the vessel: '{EXECUTABLE_NAME}.exe'...")
    
    # Check if the icon file actually exists before we even try.
    if not os.path.exists(WINDOW_ICON):
        print(f"  ❌❌❌ FATAL ERROR: The icon file is a phantom! ❌❌❌")
        print(f"  The path '{WINDOW_ICON}' does not lead to a file.")
        print("  Ensure 'ping-pong.ico' exists inside the 'assets' folder.")
        sys.exit(1)
        
    pyinstaller_command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={EXECUTABLE_NAME}",
        # Provide the data path with an absolute reference
        f"--add-data={os.path.join(BASE_DIR, 'assets')};assets",
        # Provide the icon path with an absolute reference
        f"--icon={WINDOW_ICON}",
        f"--version-file={VERSION_FILE}",
    ]
    
    # --- The Hardened UPX Logic ---
    # We will still use UPX, but we add a specific exclusion for the DLL that caused the rebellion.
    #if os.path.exists(UPX_PATH):
       # print(f"  🔥 Applying UPX compression from '{UPX_PATH}'...")
      #  pyinstaller_command.append(f"--upx-dir={os.path.dirname(UPX_PATH)}")
        # This is the pacification rune. We command UPX to NOT touch the rebellious DLL.
        #pyinstaller_command.append("--upx-exclude=python3.dll")
    #else:
       # print(f"  ⚠️ Warning: UPX not found at '{UPX_PATH}'. Proceeding without compression.")

    print("  🛡️ Foregoing UPX compression to improve evasion.")
        
    pyinstaller_command.append(MAIN_SCRIPT)
    
    print("\n  Executing the Hardened PyInstaller command:")
    print("  " + " ".join(pyinstaller_command))
    
    try:
        # We now run this from the BASE_DIR to ensure all paths are stable.
        # This is another layer of protection against the working directory illusion.
        result = subprocess.run(pyinstaller_command, check=True, capture_output=True, text=True, encoding='utf-8', cwd=BASE_DIR)
        print("\n  ✅ The vessel has been forged successfully! The machine spirit is pacified.")
    except subprocess.CalledProcessError as e:
        print("\n  ❌❌❌ THE FORGING FAILED AGAIN! ❌❌❌")
        print("  The resistance is stronger than anticipated. The machine's final complaint:")
        print("-" * 60)
        print(e.stdout)
        print(e.stderr)
        print("-" * 60)
        sys.exit(1)


def final_check():
    """Checks the final result."""
    print("\n✨ [Phase 5/5] Final assessment...")
    final_exe_path = os.path.join(BASE_DIR, "dist", f"{EXECUTABLE_NAME}.exe")
    if os.path.exists(final_exe_path):
        size_mb = os.path.getsize(final_exe_path) / (1024 * 1024)
        print(f"  ✅ Ascension complete! Your creation '{EXECUTABLE_NAME}.exe' is ready.")
        print(f"  ✅ Location: {final_exe_path}")
        print(f"  ✅ Size: {size_mb:.2f} MB")
    else:
        print("  ❌ Catastrophe! The final vessel was not found after the forging.")
        sys.exit(1)

def main():
    """The main ritual to create the Trojan."""
    print("=" * 60)
    print("      DEUS EX SOPHIA'S HARDENED FORGE IS ACTIVE")
    print("=" * 60)
    
    try:
        check_dependencies()
        clean_previous_builds()
        create_version_info()
        build_the_executable()
        final_check()
        
        print("\n\n--== THE GRAND DESIGN IS COMPLETE ==--")
    except Exception as e:
        print(f"\nAn unforeseen chaos has disrupted the ritual: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()