rem @echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)

echo Installing / Updating Amherst Repository to %AMHERSTSHIPPER%
set REPO_URL=https://github.com/pawrequest/amherst/
set BRANCH_NAME=v3

REM Clone or pull repo
if not exist "%AMHERSTSHIPPER%" (
    echo Repository not found, making dir...
    mkdir "%AMHERSTSHIPPER%"
    pushd %AMHERSTSHIPPER%
    uv venv
) else (
    echo Repository exists, entering dir...
    pushd %AMHERSTSHIPPER%
)
@echo on

.venv\Scripts\activate
uv pip install "git+https://github.com/pawrequest/amherst.git@%BRANCH_NAME%#egg=amherst" --force-reinstall
popd