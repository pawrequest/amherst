set CATEGORY=%1
set RECORD=%2
set VENV=C:\prdev\venvs\amherst\.venv
set PYTHONPATH=C:\prdev\repos\amherst\src

set SHIP_ENV=C:\prdev\envs\pf_sandbox.env
set AM_ENV=C:\prdev\envs\am_sandbox.env


set PROG_DIR=c:\ProgramData\pawrequest\amherst
if not exist "%PROG_DIR%" mkdir "%PROG_DIR%"
cd /d "%PROG_DIR%"


call %VENV%\Scripts\activate
python -m amherst.cli %CATEGORY% %RECORD%

