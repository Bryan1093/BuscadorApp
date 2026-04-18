@echo off
echo ========================================
echo  Compilando AppBuscador
echo ========================================

REM Limpiar compilaciones anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Crear ejecutable con PyInstaller
echo.
echo [1/2] Creando ejecutable...
pyinstaller --name="AppBuscador" ^
    --onefile ^
    --windowed ^
    --icon=imagenes/iconoexe.ico ^
    --add-data="imagenes;imagenes" ^
    --add-data="data;data" ^
    main.py

if %errorlevel% neq 0 (
    echo Error al crear ejecutable
    pause
    exit /b 1
)

echo.
echo [2/2] Ejecutable creado en: dist\AppBuscador.exe

echo.
echo ========================================
echo  Compilacion completada!
echo ========================================
echo.
echo Archivos generados:
echo - Ejecutable: dist\AppBuscador.exe
echo.
echo Para crear un instalador, consulta GUIA_EJECUTABLE.md
echo.
pause
