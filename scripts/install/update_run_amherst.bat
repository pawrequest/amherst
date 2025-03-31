@echo off
rem set SCRIPT_DIR=%~dp0
rem pushd %SCRIPT_DIR%
pushd %AMHERSTPR%
dir
call scripts\install\install_update_amherst_repo.bat
call scripts\install\run_amherst.bat %1 %2
