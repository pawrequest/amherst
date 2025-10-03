@echo off

echo Configuring Environment
set ENV_DIR_REMOTE=C:\prdev\envs\amdev
set SCRIPTS_DIR=C:\prdev\amdev\amherst\scripts

echo Copying all files from remote scripts directory to local scripts directory (%SCRIPTS_DIR% to %SCRIPTS_DIR_LOCAL%)
set SCRIPTS_DIR_LOCAL=%AMHERSTSHIPPER%\scripts
xcopy /Y /E %SCRIPTS_DIR%\* %SCRIPTS_DIR_LOCAL%\

echo Copying all files from remote directory to local directory (%ENV_DIR_REMOTE% to %ENV_DIR_LOCAL%)
set ENV_DIR_LOCAL=%AMHERSTSHIPPER%\envs
xcopy /Y /E %ENV_DIR_REMOTE%\* %ENV_DIR_LOCAL%\