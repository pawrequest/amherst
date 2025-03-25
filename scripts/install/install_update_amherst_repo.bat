@echo off

set REPO_URL=https://github.com/pawrequest/amherst/
set AMHERST_DIR=C:\ProgramData\AmherstPR
set GIT_DIR=%USERPROFILE%\.local\opt\git
set GIT_EXE=%GIT_DIR%\cmd\git.exe

REM Clone or pull repo
if exist "%AMHERST_DIR%" (
    echo Repository exists, updating repo...
    pushd "%AMHERST_DIR%"
    %GIT_EXE% pull
    popd
) else (
    echo Repository not found, cloning repo...
    %GIT_EXE% clone "%REPO_URL%" "%AMHERST_DIR%"
)
