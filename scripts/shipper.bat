@echo off
set thisDir=%~dp0
call %thisDir%/install/clone_or_pull_amherstpr_repo.bat
pushd %AMHERSTPR%
uv run shipper %1 %2 %3
if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
popd