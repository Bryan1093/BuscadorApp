@echo off
REM ========================================
REM Script de limpieza de AppBuscador
REM Elimina archivos temporales y de cache
REM ========================================

echo ========================================
echo  Limpiando proyecto AppBuscador
echo ========================================
echo.

REM Eliminar carpeta build de PyInstaller
if exist "build" (
    echo [1/5] Eliminando carpeta build...
    rmdir /s /q "build"
    echo      Carpeta build eliminada
) else (
    echo [1/5] Carpeta build no existe
)

REM Eliminar archivos .spec (opcional, descomenta si quieres eliminarlos)
REM if exist "*.spec" (
REM     echo [2/5] Eliminando archivos .spec...
REM     del /q "*.spec"
REM     echo      Archivos .spec eliminados
REM ) else (
REM     echo [2/5] No hay archivos .spec
REM )
echo [2/5] Manteniendo archivos .spec (configuracion)

REM Eliminar cache de Python (__pycache__)
echo [3/5] Eliminando cache de Python...
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo      Cache de Python eliminado

REM Eliminar archivos .pyc
echo [4/5] Eliminando archivos .pyc...
del /s /q "*.pyc" 2>nul
echo      Archivos .pyc eliminados

REM Eliminar archivos .pyo
echo [5/5] Eliminando archivos .pyo...
del /s /q "*.pyo" 2>nul
echo      Archivos .pyo eliminados

echo.
echo ========================================
echo  Limpieza completada!
echo ========================================
echo.
echo El proyecto esta limpio y listo.
echo El ejecutable en dist\ se mantiene intacto.
echo.
pause
