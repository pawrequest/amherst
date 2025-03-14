@echo off

rem Set the directory where the script is located (absolute path)
set SCRIPT_DIR=%~dp0

rem Set the destination directory
set PROG_DIR=%ProgramFiles%\amherst_pr
mkdir "%PROG_DIR%"

rem Define input and output file paths
set RUNNER_IN=%SCRIPT_DIR%run_amherst_uv.bat
set RUNNER_OUT=%PROG_DIR%\run_amherst_uv.bat

rem Get admin rights
NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)

rem Copy the file from the current directory (SCRIPT_DIR) to the destination directory
echo COPYING FILE FROM %RUNNER_IN% TO %RUNNER_OUT%
copy "%RUNNER_IN%" "%RUNNER_OUT%"
