@echo off
echo Installing AmherstPR

set AMHERSTPR=C:\ProgramData\AmherstPR
setx AMHERSTPR %AMHERSTPR%

call ./install_update_amherst_repo.bat
call ./install_amherst_envs.bat

pause