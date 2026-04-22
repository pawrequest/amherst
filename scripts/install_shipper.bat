@echo off
set thisDir=%~dp0
set INSTALL_DIR=C:\ProgramData\AmherstShipper

echo Installing Amherst Shipper to %INSTALL_DIR%...

call %thisDir%\_install_git_uv.bat
call %thisDir%\_copy_envs.bat %INSTALL_DIR%

REM Set and export environment variables
set AMHERST_ENV=%INSTALL_DIR%\envs\amherst.env
set SHIPAW_ENV=%INSTALL_DIR%\envs\shipaw.env
setx AMHERST_ENV %AMHERST_ENV%
setx SHIPAW_ENV %SHIPAW_ENV%

if %errorlevel% neq 0 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
echo Environment variables set:
echo AMHERST_ENV=%AMHERST_ENV%
echo SHIPAW_ENV=%SHIPAW_ENV%
