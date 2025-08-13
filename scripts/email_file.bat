@echo off
pushd %AMHERSTPR%
uv run email-file %1 %2
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd