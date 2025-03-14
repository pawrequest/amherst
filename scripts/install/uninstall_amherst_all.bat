@echo off
set PROG_DIR=%ProgramFiles%\amherst_pr
set DATA_DIR=%LocalAppData%\amherst_pr
set UV_DIR=%USERPROFILE%\.local\bin
rem get admin rights

echo Amherst Uninstall Script
echo.
echo WARNING, DESTRUCTIVE ACTIONS AHEAD: CHECK PATHS BEFORE CONTINUING!!
echo !! CHECK THE WHOLE PROGRAM FILES DIRECTORY IS NOT SCHEDULED FOR DELETION !!
echo.
echo We will delete:
echo.
echo    This entire directory:
echo    !! CHECK THIS IS NOT THE WHOLE PROGRAM FILES DIRECTORY !!
echo        - %PROG_DIR%
echo    !! CHECK THIS IS NOT THE WHOLE PROGRAM FILES DIRECTORY !!
echo.
echo    This entire directory:
echo    !! CHECK THIS IS NOT THE WHOLE USER DATA DIRECTORY !!
echo        - %DATA_DIR%
echo    !! CHECK THIS IS NOT THE WHOLE USER DATA DIRECTORY !!
echo.
echo     - the files: %UV_DIR%\uv.exe and %UV_DIR%\uvx.exe
echo     - the user environment variables: AM_ENV and SHIP_ENV
echo.
echo Press any key to continue, or CTRL+C to cancel...
pause

NET SESSION >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Restarting with Administrator rights...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c, %~s0' -Verb RunAs"
    exit
)

rmdir /S "%PROG_DIR%"
rmdir /S "%DATA_DIR%"
del /F "%UV_DIR%\uv.exe"
del /F "%UV_DIR%\uvx.exe"

reg delete "HKCU\Environment" /F /V AM_ENV
reg delete "HKCU\Environment" /F /V SHIP_ENV

pause