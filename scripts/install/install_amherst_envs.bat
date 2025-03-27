@echo off

set DATA_DIR=C:\ProgramData\AmherstPR
set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live.env"
set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"

set AM_ENV_FILE_LOCAL=%DATA_DIR%\am.env
set SHIPPING_ENV_FILE_LOCAL=%DATA_DIR%\pf.env

echo copying AM_ENV to local directory
copy %AM_ENV_FILE_REMOTE% %AM_ENV_FILE_LOCAL%
echo copying SHIP_ENV to local directory
copy %SHIPPING_ENV_FILE_REMOTE% %SHIPPING_ENV_FILE_LOCAL%

echo setting 'AM_ENV' User and session environment variables
setx AM_ENV "%AM_ENV_FILE_LOCAL%"
set AM_ENV=%AM_ENV_FILE_LOCAL%

echo setting 'SHIP_ENV' User and session environment variables
setx SHIP_ENV %SHIPPING_ENV_FILE_LOCAL%
set SHIP_ENV=%SHIPPING_ENV_FILE_LOCAL%

echo setting 'AMHERSTPR' User and session environment variables
setx AMHERSTPR %DATA_DIR%
set AMHERSTPR=%DATA_DIR%