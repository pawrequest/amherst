@echo off
pushd %AMHERSTPR%
uv run print-file %1
if %errorlevel% neq 0 (
    pause
)
popd