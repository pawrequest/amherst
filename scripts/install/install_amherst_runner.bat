@echo off
rem Get admin rights
NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)
rem Set the directory where the script is located (absolute path)
set SCRIPT_DIR=%~dp0
rem Set the destination directory
set PROG_DIR=%ProgramFiles%\amherst_pr
echo ready to create directory %PROG_DIR%
if not exist "%PROG_DIR%" (
    echo Creating directory %PROG_DIR%
    mkdir "%PROG_DIR%"
)
echo Directory created

rem Define input and output file paths
set RUNNER_IN=%SCRIPT_DIR%run_amherst_uv.bat
echo set runner in
set RUNNER_OUT=%PROG_DIR%\run_amherst_uv.bat
echo set runner out

rem Copy the file from the current directory (SCRIPT_DIR) to the destination directory
echo Copying Runner %RUNNER_IN% --> %RUNNER_OUT%
pause
copy /Y "%RUNNER_IN%" "%RUNNER_OUT%"
echo Finished - reverting to user privileges...
pause
