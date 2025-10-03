@echo off
if "%AMHERSTSHIPPER%"=="" (
    echo Error: AMHERSTSHIPPER environment variable is not set.
    exit /b 1
)
echo %AMHERSTSHIPPER% is set to %AMHERSTSHIPPER%

set thisDir=%~dp0
echo this dir is %thisDir%
call %thisDir%/install/clone_or_pull_amherst_repo.bat

pushd %AMHERSTSHIPPER%
echo Running shipper from %~dp0 with arguments: %1 %2 %3
uv run shipper %1 %2 %3
if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
popd