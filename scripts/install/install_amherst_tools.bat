rem @echo off
REM Set paths
set UV_DIR=%USERPROFILE%\.local\bin

REM install uv if not already installed
if exist "%UV_DIR%\uv.exe" (
    echo UV already installed
) else (
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo UV installed, adding to path...
)

REM TO-DO: install git (if not already installed)
REM curl.exe https://webi.ms/git | powershell
