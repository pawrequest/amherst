set HIRENAME=%1
set PYTHON_EXE=C:\Users\RYZEN\prdev\amdev\.venv\Scripts\python.exe
set VENV_ACTIVATE=C:\Users\RYZEN\prdev\amdev\.venv\Scripts\activate.bat
set SCRIPT_PATH=C:\Users\RYZEN\prdev\amdev\amherst\src\amherst\script.py
set SCRIPT_PATH_IMPORT=

call "%VENV_ACTIVATE%"
python -m %SCRIPT_PATH_IMPORT% %HIRENAME%

pause
