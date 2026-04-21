"""
Paquete de vistas de la aplicación

Este paquete contiene todas las vistas de la interfaz de usuario:
- login_view: Vista de inicio de sesión
- loading_view: Vista de carga intermedia
- selection_view: Vista de selección de módulos
- docentes_view: Vista del módulo de docentes
- oficios_view: Vista del módulo de oficios
- acerca_de_view: Vista de información de la aplicación
"""

from .login_view import mostrar_login, cerrar_sesion
from .loading_view import mostrar_carga_y_abrir_main
from .selection_view import mostrar_seleccion
from .docentes_view import mostrar_docentes
from .oficios_view import mostrar_oficios
from .acerca_de_view import mostrar_acerca_de

__all__ = [
    'mostrar_login',
    'mostrar_carga_y_abrir_main',
    'mostrar_seleccion',
    'cerrar_sesion',
    'mostrar_docentes',
    'mostrar_oficios',
    'mostrar_acerca_de'
]
