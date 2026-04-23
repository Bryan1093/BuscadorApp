"""
ResultsTable - Vista de tabla de resultados de búsqueda.

Componente QTableView que presenta los documentos encontrados con soporte de:
- Selección de fila completa (no por celda)
- Multi-selección extendida (Shift+Click, Ctrl+Click)
- Ordenamiento por header click
- Señales para doble-click y cambios de selección
"""

from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt, Signal, QModelIndex
from PySide6.QtGui import QMouseEvent

from core import DocumentProxyModel, DriveController
from core.proxy_model import (
    COL_CHECK, COL_UNIVERSIDAD, COL_PROGRAMA, COL_ESTUDIANTE, COL_NOMBRE,
    COL_ITEMS_CLAVE, COL_ANO, COL_TIPO_OFICIO
)


# Configuraciones de columnas por módulo
COLUMNS_DOCENTES = [
    {"idx": COL_CHECK, "width": 50, "label": "", "stretch": False},
    {"idx": COL_UNIVERSIDAD, "width": 150, "label": "Universidad", "stretch": False},
    {"idx": COL_PROGRAMA, "width": 150, "label": "Programa", "stretch": False},
    {"idx": COL_ESTUDIANTE, "width": 150, "label": "Estudiante", "stretch": False},
    {"idx": COL_ITEMS_CLAVE, "width": 150, "label": "Ítem Clave", "stretch": False},
    {"idx": COL_NOMBRE, "width": 0, "label": "", "stretch": True},
]

COLUMNS_OFICIOS = [
    {"idx": COL_CHECK, "width": 50, "label": "", "stretch": False},
    {"idx": COL_ANO, "width": 80, "label": "Año", "stretch": False},
    {"idx": COL_TIPO_OFICIO, "width": 150, "label": "Tipo de Oficio", "stretch": False},
    {"idx": COL_NOMBRE, "width": 0, "label": "Nombre del Archivo", "stretch": True},
]


class ResultsTable(QTableView):
    """
    Vista de tabla para visualizar y seleccionar documentos de resultados.

    Integración con DocumentProxyModel. Maneja la presentación visual de
    documentos con selección de fila completa y emite señales para
    interacciones del usuario.

    Attributes:
        document_selected: Signal(str) — Emitida en doble-click con ruta del documento.
        selection_changed: Signal(list) — Emitida al cambiar selección con lista de rutas.
    """

    # ==================== SEÑALES ====================
    document_selected = Signal(str)
    selection_changed = Signal(list)

    def __init__(
        self,
        proxy_model: DocumentProxyModel,
        controller: DriveController = None,
        parent=None,
    ):
        """
        Inicializa la vista de tabla.

        Args:
            proxy_model: DocumentProxyModel conectado a DocumentModel.
            controller: DriveController para acceso (opcional, no usado directamente).
            parent: Widget padre (opcional).
        """
        super().__init__(parent)
        self._proxy_model = proxy_model
        self._controller = controller

        # Configurar tabla
        self.setModel(proxy_model)
        self._configure_selection()
        self._configure_headers("docentes")  # Por defecto docentes

        # Conectar signals internas
        # IMPORTANTE: selectionModel() solo existe DESPUÉS de setModel
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    # ==================== CONFIGURACIÓN ====================

    def _configure_selection(self) -> None:
        """Configura el comportamiento de selección de la tabla."""
        # Seleccionar fila completa, no celdas individuales
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Permitir multi-selección con Shift+Click y Ctrl+Click
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # Habilitar ordenamiento por click en header
        self.setSortingEnabled(True)
        # Ocultar números de fila
        self.verticalHeader().setVisible(False)

    def set_columns_config(self, columns_config: list):
        """
        Configura las columnas de la tabla según el módulo.

        Args:
            columns_config: Lista de dicts con idx, width, label, stretch.
        """
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        
        for col in columns_config:
            idx = col["idx"]
            width = col["width"]
            label = col["label"]
            stretch = col["stretch"]

            if stretch:
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Fixed)
                self.setColumnWidth(idx, width)

            # Establecer texto del header
            model = self.model()
            if model:
                model.setHeaderData(idx, Qt.Horizontal, label, Qt.DisplayRole)

    def _configure_headers(self, modulo: str = "docentes") -> None:
        """
        Configura el resize mode, anchos y texto de cada columna según el módulo.

        Args:
            modulo: "docentes" o "oficios"
        """
        config = COLUMNS_DOCENTES if modulo == "docentes" else COLUMNS_OFICIOS
        self.set_columns_config(config)

    # ==================== EVENTOS ====================

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Override del evento de doble-click.

        Emite document_selected con la ruta del documento clickeado.

        Args:
            event: Evento de mouse.
        """
        super().mouseDoubleClickEvent(event)
        index = self.indexAt(event.pos())
        if index.isValid():
            route = self.get_current_route()
            if route:
                self.document_selected.emit(route)

    # ==================== HANDLERS INTERNOS ====================

    def _on_selection_changed(
        self,
        selected: QModelIndex,
        deselected: QModelIndex,
    ) -> None:
        """
        Manejador de cambio de selección.

        Calcula las rutas seleccionadas y emite la señal.

        Args:
            selected: Índices recién seleccionados.
            deselected: Índices recién deseleccionados.
        """
        del selected, deselected  # Ignored — recalculamos todo
        self.selection_changed.emit(self.get_selected_routes())

    # ==================== APIs DE UTILIDAD ====================

    def get_selected_routes(self) -> list:
        """
        Retorna la lista de rutas de los documentos seleccionados visualmente.

        Returns:
            list: Lista de strings con rutas seleccionadas.
        """
        routes = []
        proxy_model = self.model()
        if not proxy_model:
            return routes

        source_model = proxy_model.sourceModel()
        if not source_model:
            return routes

        for proxy_index in self.selectionModel().selectedRows():
            # Mapear índice proxy -> source
            source_index = proxy_model.mapToSource(proxy_index)
            if source_index.isValid():
                route = source_model.get_ruta_at_row(source_index.row())
                if route:
                    routes.append(route)

        return routes

    def get_current_route(self) -> str:
        """
        Retorna la ruta del documento en la fila actual.

        Returns:
            str: Ruta del documento actual o string vacío.
        """
        proxy_model = self.model()
        if not proxy_model:
            return ""

        current_index = self.currentIndex()
        if not current_index.isValid():
            return ""

        source_model = proxy_model.sourceModel()
        if not source_model:
            return ""

        source_index = proxy_model.mapToSource(current_index)
        if source_index.isValid():
            return source_model.get_ruta_at_row(source_index.row())

        return ""

    def select_all(self) -> None:
        """Marca todos los documentos del modelo fuente como seleccionados."""
        proxy_model = self.model()
        if proxy_model:
            source = proxy_model.sourceModel()
            if source and hasattr(source, "select_all"):
                source.select_all()

    def deselect_all(self) -> None:
        """Desmarca todos los documentos del modelo fuente."""
        proxy_model = self.model()
        if proxy_model:
            source = proxy_model.sourceModel()
            if source and hasattr(source, "deselect_all"):
                source.deselect_all()

    def invert_selection(self) -> None:
        """Invierte la selección de todos los documentos del modelo fuente."""
        proxy_model = self.model()
        if proxy_model:
            source = proxy_model.sourceModel()
            if source and hasattr(source, "invert_selection"):
                source.invert_selection()

    def set_modulo(self, modulo: str):
        """
        Cambia la configuración de columnas según el módulo.

        Args:
            modulo: "docentes" o "oficios"
        """
        self._configure_headers(modulo)