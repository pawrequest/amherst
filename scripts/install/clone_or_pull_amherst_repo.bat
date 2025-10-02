@echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)

echo Installing / Updating Amherst Repository to %AMHERSTSHIPPER%
set REPO_URL=https://github.com/pawrequest/amherst/
set BRANCH_NAME=v3

REM Clone or pull repo
if exist "%AMHERSTSHIPPER%" (
    echo Repository exists, updating repo...
    pushd %AMHERSTSHIPPER%
    git pull
) else (
    echo Repository not found, cloning repo...
    git clone --branch %BRANCH_NAME% "%REPO_URL%" "%AMHERSTSHIPPER%"
    pushd %AMHERSTSHIPPER%
)
