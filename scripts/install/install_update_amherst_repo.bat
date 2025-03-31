@echo off

set REPO_URL=https://github.com/pawrequest/amherst/

REM Clone or pull repo
if exist "%AMHERSTPR%" (
    echo Repository exists, updating repo...
    echo am env == %AMHERSTPR%
    pushd %AMHERSTPR%
    git pull
) else (
    echo Repository not found, cloning repo...
    git clone "%REPO_URL%" "%AMHERSTPR%"
)
