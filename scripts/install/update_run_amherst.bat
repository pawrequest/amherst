@echo off
set SCRIPT_DIR=%~dp0
pushd %SCRIPT_DIR%

call .\install_update_amherst_repo.bat
call .\run_amherst.bat %1 %2
