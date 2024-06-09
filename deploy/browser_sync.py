import os
from subprocess import call


os.chdir(r'C:\Users\RYZEN\prdev\amdev\amherst\src\amherst\front')
print(os.getcwd())

command = 'browser-sync start --proxy "localhost:8000" --files "templates/*/*.html, static/*/*.css"'
call(command, shell=True)
