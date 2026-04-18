"""
Paquete de interfaz de usuario para AppBuscador

Contiene todos los componentes de la interfaz gráfica:
- Estilos y temas
- Componentes reutilizables (header, filters, results, details)
- Vistas completas (login, docentes, oficios)
"""

from . import styles
from . import components
from . import views

__all__ = ['styles', 'components', 'views']

