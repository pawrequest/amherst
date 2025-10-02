@echo off
set thisDir=%~dp0
set AMHERSTSHIPPER=C:\ProgramData\AmherstShipper
setx AMHERSTSHIPPER %AMHERSTSHIPPER%

echo Installing Amherst Shipper into %AMHERSTSHIPPER%

call %thisDir%/install_git_uv.bat
call %thisDir%/clone_or_pull_amherst_repo.bat
call %thisDir%/install_amherst_envs.bat

pushd %AMHERSTSHIPPER%

pause