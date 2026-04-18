"""
Paquete de servicios para AppBuscador

Contiene la lógica de negocio de la aplicación:
- Autenticación de usuarios
- Operaciones con archivos y documentos
- Búsqueda y filtrado de datos
"""

from .auth_service import verificar_credenciales
from .file_service import (
    cargar_documentos,
    cargar_documentos_oficios,
    abrir_pdf,
    abrir_carpeta,
    descargar_pdf,
    descargar_expediente,
    sincronizar_drive
)
from .search_service import (
    buscar_documentos,
    buscar_oficios,
    obtener_programas_filtrados,
    obtener_estudiantes_filtrados,
    obtener_tipos_oficios_filtrados
)

__all__ = [
    'verificar_credenciales',
    'cargar_documentos',
    'cargar_documentos_oficios',
    'abrir_pdf',
    'abrir_carpeta',
    'descargar_pdf',
    'descargar_expediente',
    'sincronizar_drive',
    'buscar_documentos',
    'buscar_oficios',
    'obtener_programas_filtrados',
    'obtener_estudiantes_filtrados',
    'obtener_tipos_oficios_filtrados'
]

