# Guía para Crear Ejecutable de AppBuscador

## Objetivo
Convertir la aplicación AppBuscador en un archivo ejecutable (.exe) para distribuir e instalar en computadoras sin Python.

---

## Opción 1: PyInstaller (Recomendado)

### Paso 1: Instalar PyInstaller
```bash
pip install pyinstaller
```

### Paso 2: Crear el Ejecutable

#### Opción A: Ejecutable Simple (Múltiples archivos)
```bash
pyinstaller --name="AppBuscador" --windowed --icon=imagenes/logouce.png main.py
```

#### Opción B: Ejecutable de Un Solo Archivo (Recomendado)
```bash
pyinstaller --name="AppBuscador" ^
    --onefile ^
    --windowed ^
    --icon=imagenes/logouce.png ^
    --add-data="imagenes;imagenes" ^
    --add-data="data;data" ^
    main.py
```

**Parámetros explicados:**
- `--name="AppBuscador"`: Nombre del ejecutable
- `--onefile`: Crea un solo archivo .exe
- `--windowed`: No muestra consola (solo ventana GUI)
- `--icon=`: Icono del ejecutable
- `--add-data=`: Incluye carpetas necesarias (formato: "origen;destino")

### Paso 3: Archivo de Especificación (spec)

Para más control, crea un archivo `AppBuscador.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('imagenes', 'imagenes'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'tkinter',
        'PIL',
        'fitz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AppBuscador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='imagenes\\logouce.png',
)
```

Luego ejecuta:
```bash
pyinstaller AppBuscador.spec
```

### Paso 4: Ubicación del Ejecutable
El archivo .exe estará en:
```
dist/AppBuscador.exe
```

---

## Opción 2: Auto-py-to-exe (Interfaz Gráfica)

### Paso 1: Instalar
```bash
pip install auto-py-to-exe
```

### Paso 2: Ejecutar
```bash
auto-py-to-exe
```

### Paso 3: Configurar en la Interfaz
1. **Script Location**: Selecciona `main.py`
2. **One File**: Selecciona "One File"
3. **Console Window**: Selecciona "Window Based"
4. **Icon**: Selecciona `imagenes/logouce.png`
5. **Additional Files**: Agrega carpetas `imagenes` y `data`
6. Click en "CONVERT .PY TO .EXE"

---

## Opción 3: cx_Freeze (Alternativa)

### Paso 1: Instalar
```bash
pip install cx_Freeze
```

### Paso 2: Crear setup.py
```python
from cx_Freeze import setup, Executable
import sys

# Dependencias
build_exe_options = {
    "packages": ["tkinter", "PIL", "fitz"],
    "include_files": [
        ("imagenes", "imagenes"),
        ("data", "data"),
    ],
    "excludes": ["matplotlib", "numpy"],
}

# Configuración base para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="AppBuscador",
    version="1.0",
    description="Sistema de Gestión de Doctorados",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            icon="imagenes/logouce.png",
            target_name="AppBuscador.exe"
        )
    ],
)
```

### Paso 3: Compilar
```bash
python setup.py build
```

---

## Crear Instalador con Inno Setup

### Paso 1: Descargar Inno Setup
Descarga desde: https://jrsoftware.org/isdl.php

### Paso 2: Crear Script de Instalación

Crea `installer.iss`:

```ini
[Setup]
AppName=AppBuscador
AppVersion=1.0
DefaultDirName={pf}\AppBuscador
DefaultGroupName=AppBuscador
OutputDir=instaladores
OutputBaseFilename=AppBuscador_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=imagenes\logouce.png

[Files]
Source: "dist\AppBuscador.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "imagenes\*"; DestDir: "{app}\imagenes"; Flags: ignoreversion recursesubdirs
Source: "data\usuarios.json"; DestDir: "{app}\data"; Flags: ignoreversion

[Icons]
Name: "{group}\AppBuscador"; Filename: "{app}\AppBuscador.exe"
Name: "{commondesktop}\AppBuscador"; Filename: "{app}\AppBuscador.exe"

[Run]
Filename: "{app}\AppBuscador.exe"; Description: "Ejecutar AppBuscador"; Flags: postinstall nowait skipifsilent
```

### Paso 3: Compilar Instalador
1. Abre Inno Setup
2. File → Open → Selecciona `installer.iss`
3. Build → Compile
4. El instalador estará en `instaladores/AppBuscador_Setup.exe`

---

## Script Automatizado Completo

Crea `build.bat`:

```batch
@echo off
echo ========================================
echo  Compilando AppBuscador
echo ========================================

REM Limpiar compilaciones anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Crear ejecutable con PyInstaller
echo.
echo [1/3] Creando ejecutable...
pyinstaller --name="AppBuscador" ^
    --onefile ^
    --windowed ^
    --icon=imagenes/logouce.png ^
    --add-data="imagenes;imagenes" ^
    --add-data="data;data" ^
    main.py

if %errorlevel% neq 0 (
    echo Error al crear ejecutable
    pause
    exit /b 1
)

echo.
echo [2/3] Ejecutable creado en: dist\AppBuscador.exe

REM Crear instalador (si tienes Inno Setup)
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo.
    echo [3/3] Creando instalador...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo.
    echo Instalador creado en: instaladores\AppBuscador_Setup.exe
) else (
    echo.
    echo [3/3] Inno Setup no encontrado, saltando creación de instalador
)

echo.
echo ========================================
echo  Compilación completada!
echo ========================================
echo.
echo Archivos generados:
echo - Ejecutable: dist\AppBuscador.exe
if exist instaladores\AppBuscador_Setup.exe echo - Instalador: instaladores\AppBuscador_Setup.exe
echo.
pause
```

Ejecuta:
```bash
build.bat
```

---

## Consideraciones Importantes

### 1. Dependencias
Asegúrate de que todas las dependencias estén instaladas:
```bash
pip freeze > requirements.txt
```

### 2. Tamaño del Ejecutable
- **Un solo archivo**: ~50-100 MB (incluye Python y todas las librerías)
- **Múltiples archivos**: Más pequeño pero requiere carpeta completa

### 3. Antivirus
Los ejecutables de PyInstaller pueden ser marcados como falsos positivos. Soluciones:
- Firma digital del ejecutable
- Agregar excepción en antivirus
- Usar certificado de código

### 4. Rutas de Google Drive
El ejecutable buscará automáticamente las rutas de Drive en todas las unidades.

### 5. Archivo de Usuarios
Incluye `data/usuarios.json` en el instalador para que funcione el login.

---

## Distribución

### Opción A: Ejecutable Solo
1. Comparte `dist/AppBuscador.exe`
2. El usuario solo ejecuta el .exe
3. Requiere que Google Drive esté sincronizado

### Opción B: Instalador
1. Comparte `AppBuscador_Setup.exe`
2. El usuario ejecuta el instalador
3. Se crea acceso directo en escritorio
4. Se puede desinstalar desde Panel de Control

### Opción C: Carpeta Portable
1. Copia toda la carpeta `dist/`
2. Incluye un README.txt con instrucciones
3. El usuario puede ejecutar desde USB

---

## Solución de Problemas

### Error: "Failed to execute script"
- Verifica que todas las carpetas estén incluidas con `--add-data`
- Revisa que no falten dependencias

### Error: "No module named..."
- Agrega el módulo a `hiddenimports` en el .spec

### El ejecutable es muy grande
- Usa `--exclude-module` para excluir módulos no usados
- Considera UPX para comprimir: `--upx-dir=ruta/upx`

### No encuentra archivos de datos
- Verifica las rutas en `resource_path()` en `utils/file_utils.py`
- Asegúrate de usar `--add-data` correctamente

---

## Checklist de Distribución

- [ ] Ejecutable compilado y probado
- [ ] Todas las funcionalidades funcionan
- [ ] Archivos de datos incluidos (imagenes, data)
- [ ] Icono del ejecutable configurado
- [ ] Instalador creado (opcional)
- [ ] Documentación de usuario incluida
- [ ] Probado en computadora limpia (sin Python)
- [ ] Antivirus no bloquea el ejecutable

---

## Recursos Adicionales

- **PyInstaller**: https://pyinstaller.org/
- **Auto-py-to-exe**: https://github.com/brentvollebregt/auto-py-to-exe
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **cx_Freeze**: https://cx-freeze.readthedocs.io/

---

**¡Listo para distribuir!** 🚀
