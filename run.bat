@echo off
setlocal
chcp 65001 >nul
title Lanzador Void Exchange

echo 🚀 Iniciando Void Exchange...
echo Directorio actual: %CD%

:: Comprobación de .venv
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ ERROR CRÍTICO: No se encuentra .venv\Scripts\activate.bat
    echo Asegúrate de estar en la carpeta correcta y que el entorno virtual existe.
    pause
    exit /b 1
)

:: Comprobación de frontend
if not exist "frontend\package.json" (
    echo ❌ ERROR CRÍTICO: No se encuentra frontend\package.json
    echo Asegúrate de que la carpeta frontend existe.
    pause
    exit /b 1
)

echo.
echo 🔌 Lanzando Backend...
start "Void Exchange Backend" cmd /k "call .venv\Scripts\activate.bat && python main.py"

echo.
echo 💻 Lanzando Frontend...
cd frontend
start "Void Exchange Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Comandos de lanzamiento enviados.
echo Si las ventanas se cierran inmediatamente, revisa los mensajes de error en ellas.
echo.
pause