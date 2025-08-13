@echo off
pushd %AMHERSTPR%
uv run email-file %1 %2
if %errorlevel% neq 0 (
    pause
) else (
)
popd