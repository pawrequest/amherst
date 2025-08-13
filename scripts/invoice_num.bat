@echo off
pushd %AMHERSTPR%
uv run invoice-number
if %errorlevel% neq 0 (
    pause
) else (
)
popd