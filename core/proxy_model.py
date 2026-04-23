"""
Proxy model para filtrado instantáneo en PySide6.

Proporciona un QSortFilterProxyModel que permite filtrar datos de documentos
en tiempo real sin recargar los datos del modelo fuente.
"""
from PySide6.QtCore import QSortFilterProxyModel, QObject, Signal


COL_CHECK = 0
COL_UNIVERSIDAD = 1
COL_PROGRAMA = 2
COL_ESTUDIANTE = 3
COL_NOMBRE = 4
COL_ITEMS_CLAVE = 5  # Columna para Docentes
COL_ANO = 5         # Columna para Oficios
COL_TIPO_OFICIO = 6  # Columna para Oficios


class DocumentProxyModel(QSortFilterProxyModel):
    """
    Modelo proxy que se intercala entre DocumentModel y QTableView.

    Permite filtrado en tiempo real por universidad, programa, estudiante,
    nombre e ítem clave. Todos los filtros se combinan con AND.
    
    También soporta filtrado por tipo de carpeta:
    - "docentes": solo documentos de carpeta Doctorados
    - "oficios": solo documentos de carpeta Oficios
    """

    filters_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_universidad = ""
        self._filter_programa = ""
        self._filter_estudiante = ""
        self._filter_nombre = ""
        self._filter_items_clave = ""
        self._filter_tipo = ""  # "docentes" o "oficios"
        # Filtros específicos de oficios
        self._filter_ano = ""
        self._filter_tipo_oficio = ""

    @property
    def filter_universidad(self):
        return self._filter_universidad

    @filter_universidad.setter
    def filter_universidad(self, value):
        self._filter_universidad = value
        self.update_filter()

    @property
    def filter_programa(self):
        return self._filter_programa

    @filter_programa.setter
    def filter_programa(self, value):
        self._filter_programa = value
        self.update_filter()

    @property
    def filter_estudiante(self):
        return self._filter_estudiante

    @filter_estudiante.setter
    def filter_estudiante(self, value):
        self._filter_estudiante = value
        self.update_filter()

    @property
    def filter_nombre(self):
        return self._filter_nombre

    @filter_nombre.setter
    def filter_nombre(self, value):
        self._filter_nombre = value
        self.update_filter()

    @property
    def filter_items_clave(self):
        return self._filter_items_clave

    @filter_items_clave.setter
    def filter_items_clave(self, value):
        self._filter_items_clave = value
        self.update_filter()

    @property
    def filter_tipo(self):
        """Retorna el tipo de filtro: 'docentes', 'oficios', o '' (todos)"""
        return self._filter_tipo

    @filter_tipo.setter
    def filter_tipo(self, value):
        """Establece el tipo de filtro para distinguir carpetas.
        
        Args:
            value: 'docentes' para Doctorados, 'oficios' para Oficios, '' para todos
        """
        self._filter_tipo = value
        self.update_filter()

    @property
    def filter_ano(self):
        return self._filter_ano

    @filter_ano.setter
    def filter_ano(self, value):
        self._filter_ano = value
        self.update_filter()

    @property
    def filter_tipo_oficio(self):
        return self._filter_tipo_oficio

    @filter_tipo_oficio.setter
    def filter_tipo_oficio(self, value):
        self._filter_tipo_oficio = value
        self.update_filter()

    def set_filters(self, filters: dict):
        """
        Establece todos los filtros de una vez.

        Args:
            filters: Diccionario con las claves:
                     - filter_universidad: str
                     - filter_programa: str
                     - filter_estudiante: str
                     - filter_nombre: str
                     - filter_items_clave: str (opcional)
                     - filter_tipo: str (opcional) - "docentes" o "oficios"
                     - filter_ano: str (opcional) - para oficios
                     - filter_tipo_oficio: str (opcional) - para oficios
        """
        self._filter_universidad = filters.get("filter_universidad", "")
        self._filter_programa = filters.get("filter_programa", "")
        self._filter_estudiante = filters.get("filter_estudiante", "")
        self._filter_nombre = filters.get("filter_nombre", "")
        self._filter_items_clave = filters.get("filter_items_clave", "")
        self._filter_tipo = filters.get("filter_tipo", "")
        self._filter_ano = filters.get("filter_ano", "")
        self._filter_tipo_oficio = filters.get("filter_tipo_oficio", "")
        self.update_filter()

    def clear_filters(self):
        """Limpia todos los filtros establecidos."""
        self._filter_universidad = ""
        self._filter_programa = ""
        self._filter_estudiante = ""
        self._filter_nombre = ""
        self._filter_items_clave = ""
        self._filter_tipo = ""
        self._filter_ano = ""
        self._filter_tipo_oficio = ""
        self.update_filter()

    def update_filter(self):
        """Invalida el filtro para forzar un recálculo de la vista."""
        self.invalidateFilter()
        self.filters_changed.emit()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        """
        Determina si una fila del modelo fuente debe ser incluida en el modelo proxy.

        Aplica todos los filtros activos usando lógica AND:
        - Universidad: coincide exactamente (ignora si vacío o "(Todos)")
        - Programa: coincide exactamente (ignora si vacío o "(Todos)")
        - Estudiante: coincide exactamente (ignora si vacío o "(Todos)")
        - Nombre: búsqueda parcial case-insensitive
        - Tipo: filtrar por carpeta (docentes=Doctorados, oficios=Oficios)

        Args:
            source_row: Índice de la fila en el modelo fuente.
            source_parent: Índice padre en el modelo fuente.

        Returns:
            bool: True si la fila cumple todos los filtros activos, False en caso contrario.
        """
        model = self.sourceModel()
        if not model:
            return True

        # Obtener valores del modelo
        universidad = model.index(source_row, COL_UNIVERSIDAD, source_parent).data()
        programa = model.index(source_row, COL_PROGRAMA, source_parent).data()
        estudiante = model.index(source_row, COL_ESTUDIANTE, source_parent).data()
        nombre = model.index(source_row, COL_NOMBRE, source_parent).data()
        
        # Obtener ruta del documento para filtrar por tipo
        # La ruta está en el documento fuente, no en las columnas
        doc = model._documents[source_row] if hasattr(model, '_documents') else None
        ruta = doc.get('ruta', '') if doc else ''

        # Filtro por tipo (carpeta Docentes/Oficios)
        if self._filter_tipo:
            if self._filter_tipo == "docentes":
                # Solo documentos con "Doctorados" en la ruta
                if "Doctorados" not in ruta:
                    return False
            elif self._filter_tipo == "oficios":
                # Solo documentos con "Oficios" en la ruta
                if "Oficios" not in ruta:
                    return False

        # Filtro por universidad
        if self._filter_universidad and self._filter_universidad != "(Todos)":
            if universidad != self._filter_universidad:
                return False

        # Filtro por programa
        if self._filter_programa and self._filter_programa != "(Todos)":
            if programa != self._filter_programa:
                return False

        # Filtro por estudiante
        if self._filter_estudiante and self._filter_estudiante != "(Todos)":
            if estudiante != self._filter_estudiante:
                return False

        # Filtro por nombre
        if self._filter_nombre:
            if nombre is None:
                return False
            if self._filter_nombre.lower() not in nombre.lower():
                return False

        # Filtros específicos de oficios (si aplica el tipo)
        if self._filter_tipo == "oficios":
            # Obtener datos del documento dict (más flexible que columnas)
            doc = model._documents[source_row] if hasattr(model, '_documents') else None
            
            # Filtro por año
            ano = str(doc.get('ano', '')) if doc else ""
            if self._filter_ano and self._filter_ano != "(Todos)":
                if ano != self._filter_ano:
                    return False

            # Filtro por tipo de oficio
            tipo = doc.get('tipo_oficio', '') if doc else ""
            if self._filter_tipo_oficio and self._filter_tipo_oficio != "(Todos)":
                if tipo != self._filter_tipo_oficio:
                    return False

        return True
