echo off
REM Set paths
set REPO_URL=https://github.com/pawrequest/amherst/
rem set REPO_DIR=%LOCALAPPDATA%\amherst_pr
set REPO_DIR=%ProgramFiles%\amherst_pr
set UV_DIR=%USERPROFILE%\.local\bin

set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live_beta.env"
set AM_ENV_FILE_LOCAL=%REPO_DIR%\am.env

set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"
set SHIPPING_ENV_FILE_LOCAL=%REPO_DIR%\pf.env

rem get admin rights
NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)

REM install uv if not already installed
if exist "%UV_DIR%\uv.exe" (
    echo UV already installed
) else (
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo UV installed, adding to path...
)

REM TO-DO: install git (if not already installed)

REM Clone or pull repo
if exist "%REPO_DIR%" (
    echo Repository exists, updating repo...
    pushd "%REPO_DIR%"
    git pull
    popd
) else (
    echo Repository not found, cloning repo...
    git clone "%REPO_URL%" "%REPO_DIR%"
)

copy "%REPO_DIR%" "%PROGRAMFILES%\amherst_pr"
pause

echo copying env files to local directory
copy %AM_ENV_FILE_REMOTE% %AM_ENV_FILE_LOCAL%
copy %SHIPPING_ENV_FILE_REMOTE% %SHIPPING_ENV_FILE_LOCAL%

echo setting user environment variables 'AM_ENV' and 'SHIP_ENV'
setx AM_ENV %AM_ENV_FILE_LOCAL%
setx SHIP_ENV %SHIPPING_ENV_FILE_LOCAL%

echo setting session environment variables 'AM_ENV' and 'SHIP_ENV'
set AM_ENV=%AM_ENV_FILE_LOCAL%
set SHIP_ENV=%SHIPPING_ENV_FILE_LOCAL%

echo Run cli on test customer
pushd %REPO_DIR%
%UV_DIR%\uv.exe run src\amherst\cli.py Customer Test

pause
