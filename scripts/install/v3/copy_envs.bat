@echo off

echo Configuring Environment
set ENV_DIR_REMOTE=R:\paul_r\.internal\envs\v2
set ENV_DIR_LOCAL=%AMHERSTSHIPPER%\envs

echo Copying all files from remote directory to local directory (%ENV_DIR_REMOTE% to %ENV_DIR_LOCAL%)
xcopy /Y /E %ENV_DIR_REMOTE%\* %ENV_DIR_LOCAL%\