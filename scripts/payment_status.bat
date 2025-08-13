@echo off
pushd %AMHERSTPR%
uv run payment-status %1
if %errorlevel% neq 0 (
    pause
) else (
)
popd