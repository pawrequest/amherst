REM Description: Run the powershell script paul_progs.ps1
REM add flag for uninstall arg


@echo off
powershell.exe -ExecutionPolicy Bypass -File ".\paul_progs.ps1"
echo (any key to exit)
pause > nul
