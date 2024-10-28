set CATEGORY=%1
set RECORD=%2

set VENV=C:\prdev\venvs\amherst\.venv
set PYTHONPATH=C:\prdev\repos\amherst\src

set SHIP_ENV=R:\paul_r\.internal\envs\pf_live.env
set AM_ENV=R:\paul_r\.internal\envs\am_live_beta.env


set PROG_DIR=c:\ProgramData\pawrequest\amherst
if not exist "%PROG_DIR%" mkdir "%PROG_DIR%"
cd /d "%PROG_DIR%"

call %VENV%\Scripts\activate
python -m amherst.cli %CATEGORY% %RECORD%

