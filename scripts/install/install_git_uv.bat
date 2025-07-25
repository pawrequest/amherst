@echo off
echo Installing Git and UV

REM Set paths

set UV_DIR=%USERPROFILE%\.local\bin

REM maybe install uv
if exist "%UV_DIR%\uv.exe" (
    echo UV already installed
) else (
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo UV installed, adding to path...
)

REM maybe install git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Git is installed.
) else (
    echo Installing Git.
    call "R:\paul_r\dist\Git-2.49.0-64-bit.exe"
)
