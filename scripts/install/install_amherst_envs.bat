@echo off

echo Configuring Environment
set AM_ENV_DIR_REMOTE="R:\paul_r\.internal\envs\v2"
set AM_ENV_DIR_LOCAL=%AMHERSTPR%

echo Copying all files from remote directory to local directory
xcopy /Y /E %AM_ENV_DIR_REMOTE%\* %AM_ENV_DIR_LOCAL%\