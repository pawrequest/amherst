@echo off
echo Running shipper from %~dp0 with arguments: %1 %2
uvx --from "git+https://github.com/pawrequest/amherst.git" shipper %1 %2 2>&1 | findstr /v /c:"[FLASKWEBGUI]"

if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
