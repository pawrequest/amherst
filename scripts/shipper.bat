@echo off
set thisDir=%~dp0
call %thisDir%/install/clone_or_pull_amherstpr_repo.bat
pushd %AMHERSTPR%
uv run shipper %1 %2 %3
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd