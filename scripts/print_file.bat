@echo off
pushd %AMHERSTPR%
uv run print-file %1
pause