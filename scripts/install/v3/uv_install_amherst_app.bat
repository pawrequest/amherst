@echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)

echo Installing / Updating Amherst App in %AMHERSTSHIPPER%
set REPO_URL=https://github.com/pawrequest/amherst/
set BRANCH_NAME=v3

REM Clone or pull repo
if not exist "%AMHERSTSHIPPER%" (
    echo %AMHERSTSHIPER% virtual environment not found, making now...
    mkdir "%AMHERSTSHIPPER%"
    pushd %AMHERSTSHIPPER%
    call uv venv
) else (
    echo Environment exists, entering...
    pushd %AMHERSTSHIPPER%
)

echo Installing / Updating Amherst from branch %BRANCH_NAME%...
call .venv\Scripts\activate
call uv pip install "git+https://github.com/pawrequest/amherst.git@%BRANCH_NAME%#egg=amherst"
call deactivate
popd

if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
