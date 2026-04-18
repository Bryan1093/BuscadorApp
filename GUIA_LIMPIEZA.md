# 🧹 Guía de Limpieza del Proyecto

Esta guía explica cómo mantener el proyecto limpio eliminando archivos temporales y de caché.

## 📁 Archivos Temporales Generados

Durante el desarrollo y compilación, se generan varios archivos temporales:

### PyInstaller (al compilar)
- `build/` - Archivos intermedios de compilación
- `*.spec` - Archivo de configuración (se mantiene por defecto)

### Python (al ejecutar)
- `__pycache__/` - Cache de bytecode compilado
- `*.pyc` - Archivos de bytecode
- `*.pyo` - Archivos de bytecode optimizados

## 🚀 Limpieza Rápida

### Opción 1: Script Automático (Recomendado)

Ejecuta el script de limpieza:

```bash
.\clean.bat
```

Este script eliminará:
- ✅ Carpeta `build/`
- ✅ Todos los `__pycache__/`
- ✅ Archivos `.pyc` y `.pyo`
- ⚠️ Mantiene `dist/` con el ejecutable
- ⚠️ Mantiene `*.spec` (configuración)

### Opción 2: Limpieza Manual

#### Windows PowerShell:
```powershell
# Eliminar build
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# Eliminar cache de Python
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -File *.pyc | Remove-Item -Force
```

#### Windows CMD:
```cmd
rmdir /s /q build
for /d /r %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d"
del /s /q *.pyc
```

## 📋 Qué Mantener vs Qué Eliminar

### ✅ Mantener (Archivos Importantes)
- `dist/AppBuscador.exe` - Tu ejecutable compilado
- `AppBuscador.spec` - Configuración de compilación
- `data/` - Datos de la aplicación
- `imagenes/` - Recursos visuales
- Todo el código fuente (`.py`)

### ❌ Eliminar (Archivos Temporales)
- `build/` - Se regenera al compilar
- `__pycache__/` - Se regenera al ejecutar
- `*.pyc`, `*.pyo` - Se regeneran automáticamente

## 🔄 Cuándo Limpiar

### Limpia cuando:
- ✅ Antes de compartir el proyecto
- ✅ Antes de hacer commit a Git
- ✅ Después de compilar (si no necesitas debug)
- ✅ Cuando el proyecto ocupa mucho espacio
- ✅ Si hay errores extraños de importación

### No necesitas limpiar:
- ❌ Entre ejecuciones normales del código
- ❌ Si estás debuggeando problemas de compilación

## 🛡️ Protección con Git

El archivo `.gitignore` ya está configurado para ignorar automáticamente:
- Archivos de compilación
- Cache de Python
- Archivos temporales del sistema

## 📊 Espacio Liberado

Típicamente, la limpieza libera:
- `build/`: ~50-100 MB
- `__pycache__/`: ~5-10 MB
- Total: ~55-110 MB

## 🔧 Solución de Problemas

### Si el script de limpieza falla:
1. Cierra todas las instancias de la aplicación
2. Cierra el IDE/editor
3. Ejecuta como administrador si es necesario

### Si quedan archivos:
Algunos archivos pueden estar en uso. Reinicia y vuelve a intentar.

## 💡 Tips

- **Automatiza**: Agrega `clean.bat` a tu flujo de trabajo
- **Git**: Los archivos en `.gitignore` no se subirán al repositorio
- **Compilación**: Después de limpiar, necesitarás recompilar con `build.bat`

---

**Nota**: El ejecutable en `dist/` NO se elimina con el script de limpieza para proteger tu trabajo compilado.
