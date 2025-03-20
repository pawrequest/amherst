@echo off
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

REM TO-DO: install git (if not already installed)
REM if exist %GIT_EXE% (
REM     echo Git already installed
REM ) else (
REM     echo Installing Git...
REM     curl.exe https://webi.ms/git | powershell
REM )
pause