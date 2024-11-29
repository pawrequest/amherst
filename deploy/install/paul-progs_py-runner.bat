@echo off

NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)

if exist "C:\Program Files\Python313\python.exe" (
    echo Python 3.13.0 already installed
) else (
    echo Installing Python 3.13.0, please wait...
    %~dp0python-3.13.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
)
echo Running paul py script...
python  %~dp0paul-progs.py
echo All done
pause