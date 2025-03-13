set REPO_URL=https://github.com/pawrequest/amherst/
set REPO_DIR=%LOCALAPPDATA%\amherst_pr
set UV_DIR=%USERPROFILE%\.local\bin

set AM_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\am_live_beta.env"
set AM_ENV_FILE_LOCAL=%REPO_DIR%\am.env

set SHIPPING_ENV_FILE_REMOTE="R:\paul_r\.internal\envs\pf_live.env"
set SHIPPING_ENV_FILE_LOCAL=%REPO_DIR%\pf.env

cd %REPO_DIR%
%UV_DIR%\uv.exe run src\amherst\cli.py %1 %2