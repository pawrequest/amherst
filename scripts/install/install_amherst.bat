@echo off
echo Installing AmherstPR
set thisDir=%~dp0
set AMHERSTPR=C:\ProgramData\AmherstPR
setx AMHERSTPR %AMHERSTPR%

rem call %thisDir%/install_amherst_envs.bat

call %thisDir%/install_git_uv.bat
pause
start /wait cmd /k %thisDir%/install_update_amherst_repo.bat
pause
start /wait cmd /k %thisDir%/install_amherst_envs.bat
pause