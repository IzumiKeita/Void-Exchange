@echo off 
title Void Exchange Portable 
set "PATH=%~dp0python_portable;%~dp0python_portable\Scripts;%PATH%" 
echo 🚀 Iniciando Void Exchange con Python Portátil... 
 
:: Iniciar Backend y Frontend 
start "Void Exchange Backend" cmd /k "python.exe main.py" 
 
:: Nota: El frontend necesita Node.js o servirse estáticamente. 
:: Si usas la versión compilada del frontend (dist), el backend lo servirá. 
 
pause 
