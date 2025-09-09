@echo off
pushd %AMHERSTPR%
uv run payment-status %1
pause
popd