echo off
REM Set paths
set DATA_DIR=%LocalAppData%\amherst_pr
set UV_DIR=%USERPROFILE%\.local\bin

echo Run cli
pushd %DATA_DIR%
%UV_DIR%\uv.exe run src\amherst\cli.py %1 %2
