@echo off
pushd %AMHERSTPR%
call scripts\install\install_update_amherst_repo.bat
uv run shipper %1 %2


rem call scripts\install\run_amherst.bat %1 %2
