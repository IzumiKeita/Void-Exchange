@echo off
setlocal enabledelayedexpansion
title Void Exchange - Instalador Portátil

echo ========================================================
echo 🚀 Void Exchange - Configuración Portátil (Embeddable)
echo ========================================================
echo.
echo Este script preparará un entorno Python aislado para ejecutar la aplicación
echo sin necesidad de tener Python instalado en el sistema.
echo.

:: 1. Definir versión de Python (3.11.9 es muy estable)
set PYTHON_VERSION=3.11.9
set PYTHON_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_ZIP%
set PORTABLE_DIR=python_portable

:: 2. Verificar si ya existe
if exist "%PORTABLE_DIR%" goto :check_pip

:download_python
echo 📥 Descargando Python %PYTHON_VERSION% (Embeddable)...
mkdir "%PORTABLE_DIR%"

:: Descargar ZIP (usando curl que viene en Windows 10/11 por defecto, es más seguro que powershell en batch)
curl -L -o "%PYTHON_ZIP%" "%PYTHON_URL%"

if not exist "%PYTHON_ZIP%" (
    echo ❌ Error al descargar Python. Verifica tu conexión.
    pause
    exit /b 1
)

echo 📦 Extrayendo Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PORTABLE_DIR%'"
del "%PYTHON_ZIP%"

:: Configurar pth para que soporte site-packages
echo Importante: Habilitando site-packages en python._pth...
:: Buscar archivo ._pth
dir /b "%PORTABLE_DIR%\python*._pth" > pth_file.tmp
set /p PTH_FILE=<pth_file.tmp
del pth_file.tmp

if not exist "%PORTABLE_DIR%\!PTH_FILE!" (
    echo ❌ No se encontró el archivo .pth. Algo salió mal.
    pause
    exit /b 1
)

type "%PORTABLE_DIR%\!PTH_FILE!" | findstr /v "#import site" > "%PORTABLE_DIR%\!PTH_FILE!.tmp"
echo import site>> "%PORTABLE_DIR%\!PTH_FILE!.tmp"
move /y "%PORTABLE_DIR%\!PTH_FILE!.tmp" "%PORTABLE_DIR%\!PTH_FILE!"

echo ✅ Python portátil configurado.

:check_pip
:: 3. Instalar PIP en el Python portátil
if exist "%PORTABLE_DIR%\Scripts\pip.exe" goto :install_deps

echo 📥 Descargando e instalando PIP...
curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
"%PORTABLE_DIR%\python.exe" get-pip.py --no-warn-script-location
del get-pip.py

:install_deps
:: 4. Instalar Dependencias del Proyecto
echo.
echo 📦 Instalando dependencias en el entorno portátil...
"%PORTABLE_DIR%\python.exe" -m pip install -r requirements.txt --no-warn-script-location

:: 5. Crear lanzador portátil
echo.
echo 🔨 Creando lanzador 'start_portable.bat'...

echo @echo off > start_portable.bat
echo title Void Exchange Portable >> start_portable.bat
echo set "PATH=%%~dp0%PORTABLE_DIR%;%%~dp0%PORTABLE_DIR%\Scripts;%%PATH%%" >> start_portable.bat
echo echo 🚀 Iniciando Void Exchange con Python Portátil... >> start_portable.bat
echo. >> start_portable.bat
echo :: Iniciar Backend y Frontend >> start_portable.bat
echo start "Void Exchange Backend" cmd /k "python.exe main.py" >> start_portable.bat
echo. >> start_portable.bat
echo :: Nota: El frontend necesita Node.js o servirse estáticamente. >> start_portable.bat
echo :: Si usas la versión compilada del frontend (dist), el backend lo servirá. >> start_portable.bat
echo. >> start_portable.bat
echo pause >> start_portable.bat

echo.
echo ========================================================
echo ✅ ¡Instalación portátil completada!
echo ========================================================
echo.
echo Ahora puedes copiar toda la carpeta del proyecto (incluyendo 'python_portable')
echo a cualquier computadora y ejecutar 'start_portable.bat'.
echo.
echo NOTA: Para que funcione sin Node.js en la otra PC, debes haber ejecutado
echo 'npm run build' en la carpeta frontend previamente.
