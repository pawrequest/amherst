@echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)
REM Check for --no-cache argument
set NO_CACHE=
set FORECE_REINSTALL=
for %%A in (%*) do (
    if "%%A"=="--no-cache" set NO_CACHE=--no-cache
    if "%%A"=="--force-reinstall" set FORCE_REINSTALL=--force-reinstall
)

echo Installing / Updating Amherst App in %AMHERSTSHIPPER% with arguments: %NO_CACHE% %FORCE_REINSTALL%
set REPO_URL=https://github.com/pawrequest/amherst/
set BRANCH_NAME=v3

REM Make / enter the shipper directory
if not exist "%AMHERSTSHIPPER%" (
    echo %AMHERSTSHIPER% virtual environment not found, making now...
    mkdir "%AMHERSTSHIPPER%"
    pushd %AMHERSTSHIPPER%
    call uv venv
) else (
    echo Environment exists, entering...
    pushd %AMHERSTSHIPPER%
)

REM Install / Update Amherst App
echo Installing / Updating Amherst from branch %BRANCH_NAME%...
call .venv\Scripts\activate
call uv pip install %NO_CACHE% %FORCE_REINSTALL% "git+https://github.com/pawrequest/amherst.git@%BRANCH_NAME%#egg=amherst"
call deactivate
popd

if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
