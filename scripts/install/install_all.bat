@echo off
set thisDir=%~dp0
set AMHERSTSHIPPER=C:\ProgramData\AmherstShipper
setx AMHERSTSHIPPER %AMHERSTSHIPPER%

echo Installing Amherst Shipper into %AMHERSTSHIPPER%

call %thisDir%\install_git_uv.bat
call %thisDir%\uv_install_amherst_app.bat
call %thisDir%\copy_envs.bat

pushd %AMHERSTSHIPPER%

if %errorlevel% neq 0 (
    echo Error: shipper exited with code %errorlevel%
    pause
)