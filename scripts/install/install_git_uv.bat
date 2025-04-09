@echo off
echo Installing Git and UV

REM Set paths

set UV_DIR=%USERPROFILE%\.local\bin
set GIT_DIR=%USERPROFILE%\.local\opt\git
set GIT_EXE=%GIT_DIR%\cmd\git.exe


REM install uv if not already installed
if exist "%UV_DIR%\uv.exe" (
    echo UV already installed
) else (
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo UV installed, adding to path...
)

git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Git is installed.
) else (
    echo Installing Git.
    call "R:\paul_r\dist\Git-2.49.0-64-bit.exe"
)

REM TO-DO: install git (if not already installed)
rem if exist %GIT_EXE% (
rem     echo Git already installed
rem ) else (
rem     echo Installing Git...
rem )
