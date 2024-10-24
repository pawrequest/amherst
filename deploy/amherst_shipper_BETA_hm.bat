set CATEGORY=%1
set RECORD=%2
set AM_LOC=C:\Users\RYZEN\prdev\amdev
set VENV=%AM_LOC%\.venv
set PYTHONPATH=%AM_LOC%\amherst\src

set PROG_DIR=c:\ProgramData\pawrequest\amherst
if not exist "%PROG_DIR%" mkdir "%PROG_DIR%"
cd /d "%PROG_DIR%"

call %VENV%\Scripts\activate
python -m amherst.shipper %CATEGORY% %RECORD%

