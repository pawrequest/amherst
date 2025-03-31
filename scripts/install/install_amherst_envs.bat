@echo off

echo Configuring Envirnoment
set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live_beta.env"
set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"

set AM_ENV_FILE_LOCAL=%AMHERSTPR%\am.env
set SHIPPING_ENV_FILE_LOCAL=%AMHERSTPR%\pf.env

echo copying AM_ENV to local directory
copy %AM_ENV_FILE_REMOTE% %AM_ENV_FILE_LOCAL%
echo copying SHIP_ENV to local directory
copy %SHIPPING_ENV_FILE_REMOTE% %SHIPPING_ENV_FILE_LOCAL%

rem echo setting 'AM_ENV' User and session environment variables
rem setx AM_ENV "%AM_ENV_FILE_LOCAL%"
rem set AM_ENV=%AM_ENV_FILE_LOCAL%

rem echo setting 'SHIP_ENV' User and session environment variables
rem setx SHIP_ENV %SHIPPING_ENV_FILE_LOCAL%
rem set SHIP_ENV=%SHIPPING_ENV_FILE_LOCAL%

