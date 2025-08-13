@echo off
pushd %AMHERSTPR%
uv run convert_tracking %1
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd