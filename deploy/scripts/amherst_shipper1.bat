set CATEGORY=%1
set HIRENAME=%2


set VENV_ACTIVATE=C:\Users\RYZEN\prdev\amdev\.venv\Scripts\activate.bat
set SCRIPT_PATH=C:\Users\RYZEN\prdev\amdev\amherst\src\amherst\script.py

call "%VENV_ACTIVATE%"
python %SCRIPT_PATH% %CATEGORY% %HIRENAME%

pause