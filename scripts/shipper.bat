@echo off
echo Running shipper from %~dp0 with arguments: %1 %2
uvx --from "git+https://github.com/pawrequest/amherst.git@latest" shipper %1 %2
if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
