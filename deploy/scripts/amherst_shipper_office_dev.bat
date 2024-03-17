set HIRENAME=%1
set VENV_LOC=R:\paul_r\.internal\amdev\.shipvenv

call "%VENV_LOC%\Scripts\activate.bat"
python am_address %HIRENAME%

pause
