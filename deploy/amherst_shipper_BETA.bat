set CATEGORY=%1
set RECORD=%2
set VENV=C:\Users\giles\prdev\amdev\amherst\.venv
set PYTHONPATH=C:\Users\giles\prdev\amdev\amherst\src

set SHIP_ENV=R:\paul_r\.internal\envs\pf_sandbox.env
set AM_ENV=R:\paul_r\.internal\envs\am_sandbox.env


set PROG_DIR=c:\ProgramData\pawrequest\amherst
if not exist "%PROG_DIR%" mkdir "%PROG_DIR%"
cd /d "%PROG_DIR%"


call %VENV%\Scripts\activate
python -m amherst.amherst_fastui_desktop %CATEGORY% %RECORD%
