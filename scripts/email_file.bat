@echo off
pushd %AMHERSTPR%
uv run email-file %1 %2
pause