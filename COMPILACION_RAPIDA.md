# Compilación Rápida - AppBuscador

## Método Más Rápido (Recomendado)

### 1. Instalar PyInstaller
```bash
pip install pyinstaller
```

### 2. Ejecutar el Script de Compilación
```bash
.\build.bat
```

¡Listo! El ejecutable estará en `dist/AppBuscador.exe`

---

## Método Alternativo: Comando Manual

```bash
pyinstaller --name="AppBuscador" --onefile --windowed --icon=imagenes/logouce.png --add-data="imagenes;imagenes" --add-data="data;data" main.py
```

py -m PyInstaller --name="AppBuscador" --onefile --windowed --icon=imagenes/logouce.png --add-data="imagenes;imagenes" --add-data="data;data" main.py

---

## Método Avanzado: Usar Archivo .spec

```bash
pyinstaller AppBuscador.spec
```

---

## Probar el Ejecutable

1. Ve a la carpeta `dist/`
2. Ejecuta `AppBuscador.exe`
3. Verifica que todo funcione correctamente

---

## Distribuir

### Opción 1: Solo el Ejecutable
- Comparte `dist/AppBuscador.exe`
- El usuario lo ejecuta directamente

### Opción 2: Con Instalador
- Consulta `GUIA_EJECUTABLE.md` para crear un instalador profesional

---

## Solución de Problemas

**Error al compilar:**
```bash
pip install --upgrade pyinstaller pillow pymupdf
```

**El ejecutable no abre:**
- Verifica que las carpetas `imagenes` y `data` estén incluidas
- Revisa que el antivirus no lo esté bloqueando

---

Para más detalles, consulta: **GUIA_EJECUTABLE.md**
