@echo off
rem Get admin rights
NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)
set PROG_DIR=C:\ProgramData\AmherstPR
if not exist "%PROG_DIR%" (
    echo Creating directory %PROG_DIR%
    mkdir "%PROG_DIR%"
)

echo Copying Batch scripts to %PROG_DIR%
set SCRIPT_DIR=%~dp0
copy /Y "%SCRIPT_DIR%" "%PROG_DIR%"

rem fin
echo Finished - reverting to user privileges...
