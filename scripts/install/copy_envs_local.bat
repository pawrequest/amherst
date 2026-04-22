@echo off

echo Configuring Environment
set SCRIPTS_DIR_REMOTE=C:\prdev\amdev\amherst\scripts
set ENV_DIR_REMOTE=C:\prdev\envs\amdev

set SCRIPTS_DIR_LOCAL=%AMHERSTSHIPPER%\scripts
set ENV_DIR_LOCAL=%AMHERSTSHIPPER%\envs

echo Copying remote scripts from %SCRIPTS_DIR_REMOTE% to %SCRIPTS_DIR_LOCAL%
xcopy /Y /E %SCRIPTS_DIR_REMOTE%\* %SCRIPTS_DIR_LOCAL%\

echo Copying env files from %ENV_DIR_REMOTE% to %ENV_DIR_LOCAL%
xcopy /Y /E %ENV_DIR_REMOTE%\* %ENV_DIR_LOCAL%\