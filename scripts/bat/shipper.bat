@echo off
uvx shipper %1 %2

if %errorlevel% neq 0 if %errorlevel% neq 15 (
    echo Error: shipper exited with code %errorlevel%
    pause
)
