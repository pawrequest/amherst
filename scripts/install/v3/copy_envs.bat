@echo off

echo Configuring Environment
set ENV_DIR_REMOTE=R:\paul_r\.internal\envs\v2
set SCRIPTS_DIR_REMOTE=R:\paul_r\install2

set SCRIPTS_DIR_LOCAL=%AMHERSTSHIPPER%\scripts
set ENV_DIR_LOCAL=%AMHERSTSHIPPER%\envs

echo Copying remote scripts from %SCRIPTS_DIR_REMOTE% to %SCRIPTS_DIR_LOCAL%
xcopy /Y /E %SCRIPTS_DIR_REMOTE%\* %SCRIPTS_DIR_LOCAL%\

echo Copying env files from %ENV_DIR_REMOTE% to %ENV_DIR_LOCAL%
xcopy /Y /E %ENV_DIR_REMOTE%\* %ENV_DIR_LOCAL%\