set REPO_DIR=%LOCALAPPDATA%\amherst_pr
set UV_DIR=%USERPROFILE%\.local\bin

rmdir /S /Q "%REPO_DIR%"
del /F /Q "%UV_DIR%\uv.exe"
del /F /Q "%UV_DIR%\uvx.exe"

reg delete "HKCU\Environment" /F /V AM_ENV
reg delete "HKCU\Environment" /F /V SHIP_ENV

pause