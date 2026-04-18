# AppBuscador - Sistema de Gestión de Doctorados

## Descripción
Sistema modular para la búsqueda y gestión de documentos de doctorados y oficios de la Universidad Central del Ecuador.

## Estructura del Proyecto

```
AppBuscador/
├── main.py                          # Punto de entrada principal
├── Buscador.py                      # [LEGACY] Script original (mantener como referencia)
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuración global, rutas, constantes
├── models/
│   └── __init__.py                  # (Reservado para futuros modelos de datos)
├── services/
│   ├── __init__.py
│   ├── auth_service.py              # Servicio de autenticación
│   ├── file_service.py              # Operaciones con archivos
│   └── search_service.py            # Lógica de búsqueda
├── ui/
│   ├── __init__.py
│   ├── styles.py                    # Estilos y temas de UI
│   ├── components/
│   │   ├── __init__.py
│   │   ├── header.py                # Componente de encabezado
│   │   ├── filters.py               # Componentes de filtros
│   │   ├── results.py               # Componente de resultados
│   │   └── details.py               # Componente de detalles
│   └── views/
│       ├── __init__.py
│       ├── login_view.py            # Vista de login
│       ├── docentes_view.py         # Vista principal de docentes
│       └── oficios_view.py          # Vista de oficios
├── utils/
│   ├── __init__.py
│   ├── file_utils.py                # Utilidades para archivos
│   └── path_utils.py                # Utilidades para rutas
├── data/
│   ├── cifrador.py                  # Script para hashear contraseñas
│   └── usuarios.json                # Base de datos de usuarios
└── imagenes/
    └── logouce.png                  # Logo de la universidad
```

## Características

### Modularización
- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Reutilización de código**: Componentes UI y servicios reutilizables
- **Mantenibilidad**: Código organizado y fácil de mantener
- **Escalabilidad**: Fácil agregar nuevas funcionalidades

### Módulos Principales

#### Config
- `settings.py`: Variables globales, constantes y configuración

#### Services
- `auth_service.py`: Autenticación de usuarios con SHA-256
- `file_service.py`: Carga, apertura y descarga de documentos
- `search_service.py`: Búsqueda y filtrado de documentos

#### UI Components
- `header.py`: Encabezado con logo y botones
- `filters.py`: Filtros de búsqueda (universidad, programa, estudiante, etc.)
- `results.py`: Treeview de resultados
- `details.py`: Panel de detalles de documentos

#### UI Views
- `login_view.py`: Pantalla de login y selección de módulo
- `docentes_view.py`: Vista completa del módulo de docentes
- `oficios_view.py`: Vista completa del módulo de oficios

#### Utils
- `path_utils.py`: Búsqueda de rutas de Google Drive
- `file_utils.py`: Utilidades para recursos y estructura de archivos

## Instalación

### Requisitos
```bash
pip install tkinter pillow PyMuPDF
```

### Ejecución
```bash
python main.py
```

## Compilación a Ejecutable

Para distribuir la aplicación en computadoras sin Python instalado:

### Método Rápido
```bash
# 1. Instalar PyInstaller
pip install pyinstaller

# 2. Ejecutar script de compilación
build.bat
```

El ejecutable estará en `dist/AppBuscador.exe`

### Documentación Completa
- **Guía rápida**: Ver [COMPILACION_RAPIDA.md](COMPILACION_RAPIDA.md)
- **Guía completa**: Ver [GUIA_EJECUTABLE.md](GUIA_EJECUTABLE.md)

### Archivos de Compilación
- `build.bat`: Script automatizado de compilación
- `AppBuscador.spec`: Configuración de PyInstaller
- `requirements-build.txt`: Dependencias para compilar

## Mantenimiento y Limpieza

Para mantener el proyecto limpio de archivos temporales y caché:

### Limpieza Automática
```bash
.\clean.bat
```

### Documentación de Limpieza
- **Guía completa**: Ver [GUIA_LIMPIEZA.md](GUIA_LIMPIEZA.md)



## Uso

1. **Login**: Ingresa tus credenciales de usuario
2. **Selección de Módulo**: Elige entre Docentes u Oficios
3. **Búsqueda**: Usa los filtros y campo de búsqueda
4. **Acciones**: 
   - Abrir PDF
   - Descargar PDF
   - Descargar expediente completo (solo docentes)

## Ventajas de la Nueva Estructura

### Antes (Monolítico)
- ❌ 1392 líneas en un solo archivo
- ❌ 68 funciones mezcladas
- ❌ Variables globales dispersas
- ❌ Difícil de mantener y escalar

### Ahora (Modular)
- ✅ Código organizado en 20+ archivos
- ✅ Separación clara de responsabilidades
- ✅ Componentes reutilizables
- ✅ Fácil de mantener y extender
- ✅ Mejor legibilidad
- ✅ Facilita el trabajo en equipo

## Futuras Mejoras

- [ ] Agregar logging
- [ ] Implementar tests unitarios
- [ ] Agregar manejo de errores mejorado
- [ ] Crear modelos de datos con clases
- [ ] Implementar caché de búsquedas
- [ ] Agregar exportación a Excel
- [ ] Implementar búsqueda avanzada

## Notas

- El archivo `Buscador.py` original se mantiene como referencia
- Todas las funcionalidades del código original están preservadas
- La nueva estructura facilita futuras implementaciones

## Autor

Universidad Central del Ecuador - Unidad de Gestión de Doctorados
