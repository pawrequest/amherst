set REPO_URL=https://github.com/pawrequest/amherst/
set DATA_DIR=%LocalAppData%\amherst_pr

REM Clone or pull repo
if exist "%DATA_DIR%" (
    echo Repository exists, updating repo...
    pushd "%DATA_DIR%"
    git pull
    popd
) else (
    echo Repository not found, cloning repo...
    git clone "%REPO_URL%" "%DATA_DIR%"
)

pause