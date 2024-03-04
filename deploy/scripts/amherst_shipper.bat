set HIRENAME=%1
set PYTHON_EXE=C:\Users\RYZEN\prdev\amdev\.venv\Scripts\python.exe
set VENV_ACTIVATE=C:\Users\RYZEN\prdev\amdev\.venv\Scripts\activate.bat
set SCRIPT_PATH=C:\Users\RYZEN\prdev\amdev\amherst\src\amherst\script.py

call "%VENV_ACTIVATE%"
python %SCRIPT_PATH% %HIRENAME%

pause
