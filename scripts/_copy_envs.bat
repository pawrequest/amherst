@echo off
REM Copy environment files and scripts from network location to local directory
set DIR_LOCAL=%1
set DIR_REMOTE=R:\paul_r\v3\
echo Copying envs and scripts from %DIR_REMOTE% to %DIR_LOCAL%
xcopy /Y /E %DIR_REMOTE%\* %DIR_LOCAL%\

