"""
Componentes reutilizables de UI para AppBuscador

Componentes modulares que pueden ser usados en diferentes vistas:
- header: Encabezado con logo y botones
- filters: Filtros de búsqueda
- results: Treeview de resultados
- details: Panel de detalles de documentos
"""

# Importar todos los componentes para facilitar su uso
from . import header
from . import filters
from . import results
from . import details
from . import loading_dialog

__all__ = ['header', 'filters', 'results', 'details', 'loading_dialog']
