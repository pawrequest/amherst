@echo off
pushd %AMHERSTPR%
uv run convert_tracking %1
pause