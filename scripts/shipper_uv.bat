@echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)
set thisDir=%~dp0
echo Running shipper from %~dp0 with arguments: %1 %2 %3
call %thisDir%\install\uv_install_amherst_app.bat

pushd %AMHERSTSHIPPER%
set AMHERST_ENV=%AMHERSTSHIPPER%\amherst.env
set AMHERST_ENV=%AMHERSTSHIPPER%\shipaw.env
uv run shipper %1 %2 %3
popd

if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
