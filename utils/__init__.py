"""
Paquete de utilidades para AppBuscador

Este paquete contiene funciones de utilidad para:
- Manejo de rutas de archivos y Google Drive
- Operaciones con archivos y recursos
- Estructura de oficios
"""

from .path_utils import (
    encontrar_rutas_drive,
    obtener_todas_universidades,
    obtener_todas_universidades_combinadas
)

from .file_utils import (
    resource_path,
    obtener_estructura_oficios
)

__all__ = [
    'encontrar_rutas_drive',
    'obtener_todas_universidades',
    'obtener_todas_universidades_combinadas',
    'resource_path',
    'obtener_estructura_oficios'
]

