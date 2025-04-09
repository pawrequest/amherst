@echo off
echo Installing AmherstPR
set thisDir=%~dp0
set AMHERSTPR=C:\ProgramData\AmherstPR
setx AMHERSTPR %AMHERSTPR%

rem call %thisDir%/install_amherst_envs.bat

call %thisDir%/install_git_uv.bat
call %thisDir%/clone_or_pull_amherstpr_repo.bat
call %thisDir%/install_amherst_envs.bat

