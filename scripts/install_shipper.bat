@echo off
set thisDir=%~dp0
set LOCAL_DIR=C:\ProgramData\AmherstShipper
set REMOTE_DIR=R:\paul_r\v3\

echo Installing Amherst Shipper Configuration to %LOCAL_DIR%...

rem install git and uv
call %thisDir%\_install_git_uv.bat

rem copy envs and scripts from network location to local directory
echo Copying envs and scripts from %REMOTE_DIR%
xcopy /Y /E %REMOTE_DIR%\* %LOCAL_DIR%\

REM Set and export environment variables
set AMHERST_ENV=%LOCAL_DIR%\envs\amherst.env
set SHIPAW_ENV=%LOCAL_DIR%\envs\shipaw.env
setx AMHERST_ENV %AMHERST_ENV%
setx SHIPAW_ENV %SHIPAW_ENV%

echo Environment variables set:
echo AMHERST_ENV=%AMHERST_ENV%
echo SHIPAW_ENV=%SHIPAW_ENV%
