@echo off
pushd %AMHERSTPR%
uv run invoice-number
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd