set CATEGORY=%1
set RECORD=%2

set VENV=C:\Users\RYZEN\prdev\venvs\amherst-venv
set PYTHONPATH=C:\Users\RYZEN\prdev\repos\amdev\amherst\src

set PROG_DIR=c:\ProgramData\pawrequest\amherst
if not exist "%PROG_DIR%" mkdir "%PROG_DIR%"
cd /d "%PROG_DIR%"

call %VENV%\Scripts\activate
python -m amherst.cli %CATEGORY% %RECORD%

