@echo off

set REPO_URL=https://github.com/pawrequest/amherst/
set DATA_DIR=%LocalAppData%\amherst_pr
set GIT_DIR=%USERPROFILE%\.local\opt\git
set GIT_EXE=%GIT_DIR%\cmd\git.exe
echo data dir: %DATA_DIR%

REM Clone or pull repo
if exist "%DATA_DIR%" (
    echo Repository exists, updating repo...
    pushd "%DATA_DIR%"
    %GIT_EXE% pull
    popd
) else (
    echo Repository not found, cloning repo...
    %GIT_EXE% clone "%REPO_URL%" "%DATA_DIR%"
)
