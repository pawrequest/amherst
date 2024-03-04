set HIRENAME=%1
set PYTHON_EXE=R:\paul_r\.internal\amdev\.venv\Scripts\python.exe
set VENV_ACTIVATE=R:\paul_r\.internal\amdev\.venv\Scripts\activate.bat
set SCRIPT_PATH=R:\paul_r\.internal\amdev\amherst\src\amherst\script.py

call "%VENV_ACTIVATE%"
python %SCRIPT_PATH% %HIRENAME%

pause
