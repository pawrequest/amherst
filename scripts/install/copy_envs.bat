@echo off

echo Configuring Environment
set DIR_REMOTE=R:\paul_r\v3
set DIR_LOCAL=%AMHERSTSHIPPER%

echo Copying remote files from %DIR_REMOTE% to %DIR_LOCAL%
xcopy /Y /E %DIR_REMOTE%\* %DIR_LOCAL%\
