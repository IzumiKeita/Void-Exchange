@echo off
setlocal enabledelayedexpansion
title Construyendo Void Exchange...

echo 🚀 Iniciando proceso de construcción de Void Exchange (Standalone)...
echo.

:: 1. Verificar entorno virtual
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ ERROR: No se encuentra el entorno virtual (.venv).
    echo Asegúrate de haber ejecutado 'run.bat' al menos una vez o crea el venv manualmente.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

:: 2. Instalar PyInstaller
echo 📦 Verificando/Instalando PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al instalar PyInstaller.
    pause
    exit /b 1
)

:: 3. Construir Frontend
echo.
echo 💻 Construyendo Frontend (Vue.js)...
cd frontend
if not exist "node_modules" (
    echo 📦 Instalando dependencias de Node...
    call npm install
)
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al construir el frontend. Revisa los logs de npm.
    cd ..
    pause
    exit /b 1
)
cd ..

:: 4. Construir Ejecutable
echo.
echo 🔨 Generando ejecutable (esto puede tardar unos minutos)...
echo Incluyendo:
echo  - Frontend (dist)
echo  - Traducciones (backend/data/translations.json)
echo  - Icono (frontend/public/favicon.ico)

:: Limpiar builds anteriores
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"

:: Ejecutar PyInstaller
pyinstaller --noconfirm --onefile --console --clean ^
    --name "VoidExchange" ^
    --add-data "frontend/dist;dist" ^
    --add-data "backend/data/translations.json;data" ^
    --icon "frontend/public/favicon.ico" ^
    --collect-all "flask" ^
    --collect-all "sqlalchemy" ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al generar el ejecutable.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo ✅ ¡Construcción completada con éxito!
echo ========================================================
echo.
echo 📂 El ejecutable se encuentra en: %CD%\dist\VoidExchange.exe
echo.
echo Puedes copiar este archivo a cualquier computadora con Windows.
echo No necesita Python ni Node.js instalados.
echo.
echo NOTA: Al ejecutarlo por primera vez, creará la base de datos
echo y archivos de caché en la misma carpeta donde esté el .exe.
echo Si usas Gemini AI, recuerda poner tu archivo .env junto al .exe.
echo.
pause