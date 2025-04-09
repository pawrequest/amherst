@echo off

echo Installing / Updating Amherst Repository to %AMHERSTPR%
set REPO_URL=https://github.com/pawrequest/amherst/

REM Clone or pull repo
if exist "%AMHERSTPR%" (
    echo Repository exists, updating repo...
    dir
    pushd %AMHERSTPR%
    dir
    git pull
) else (
    echo Repository not found, cloning repo...
    git clone "%REPO_URL%" "%AMHERSTPR%"
)