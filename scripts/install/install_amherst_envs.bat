@echo off

set DATA_DIR=%LocalAppData%\amherst_pr

if not exist "%DATA_DIR%" (
    echo no repo found
    call .\install_update_amherst_repo.bat
)

set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live_beta.env"
set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"
set AM_ENV_FILE_LOCAL=%DATA_DIR%\am.env
set SHIPPING_ENV_FILE_LOCAL=%DATA_DIR%\pf.env

echo copying env files to local directory
copy %AM_ENV_FILE_REMOTE% %AM_ENV_FILE_LOCAL%
copy %SHIPPING_ENV_FILE_REMOTE% %SHIPPING_ENV_FILE_LOCAL%

echo setting 'AM_ENV' User and session environment variables
setx AM_ENV "%AM_ENV_FILE_LOCAL%"
set AM_ENV=%AM_ENV_FILE_LOCAL%

echo setting 'SHIP_ENV' User and session environment variables
setx SHIP_ENV %SHIPPING_ENV_FILE_LOCAL%
set SHIP_ENV=%SHIPPING_ENV_FILE_LOCAL%
