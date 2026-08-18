@echo off
set UV_DIR=%USERPROFILE%\.local\bin

REM maybe install uv
if not exist "%UV_DIR%\uv.exe" (
    echo Astral uv not installed - fetching from https://astral.sh/uv/install.ps1
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo UV installed
)

REM maybe install git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo git is not installed - installing from R:\paul_r\dist\Git-2.49.0-64-bit.exe
    call "R:\paul_r\dist\Git-2.49.0-64-bit.exe"
)
