echo off
REM Set paths
set DATA_DIR=%LocalAppData%\amherst_pr
set PROG_DIR=%ProgramFiles%\amherst_pr

set REPO_URL=https://github.com/pawrequest/amherst/
set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live_beta.env"
set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"

set UV_EXE=%USERPROFILE%\.local\bin\uv.exe
set AM_ENV_FILE_LOCAL=%DATA_DIR%\am.env
set SHIPPING_ENV_FILE_LOCAL=%DATA_DIR%\pf.env

call ./install_amherst_tools.bat

REM Clone or pull repo
if exist "%DATA_DIR%" (
    echo Repository exists, updating repo...
    pushd "%DATA_DIR%"
    git pull
    popd
) else (
    echo Repository not found, cloning repo...
    git clone "%REPO_URL%" "%DATA_DIR%"
)

echo copying env files to local directory
copy %AM_ENV_FILE_REMOTE% %AM_ENV_FILE_LOCAL%
copy %SHIPPING_ENV_FILE_REMOTE% %SHIPPING_ENV_FILE_LOCAL%

echo setting user environment variables 'AM_ENV' and 'SHIP_ENV'
setx AM_ENV %AM_ENV_FILE_LOCAL%
setx SHIP_ENV %SHIPPING_ENV_FILE_LOCAL%

echo setting session environment variables 'AM_ENV' and 'SHIP_ENV'
set AM_ENV=%AM_ENV_FILE_LOCAL%
set SHIP_ENV=%SHIPPING_ENV_FILE_LOCAL%

pause
call ./install_amherst_runner.bat

pause