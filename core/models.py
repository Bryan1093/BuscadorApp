"""
Modelo de datos para documentos con soporte de selección mediante CheckBox.

Gestiona una lista de documentos con campos: universidad, programa, estudiante,
nombre, ruta y seleccionada (bool). Provee funcionalidad de CheckBox en la columna 0
para permitir la selección múltiple de documentos.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, Signal, QModelIndex
from PySide6.QtGui import QColor


class DocumentModel(QAbstractTableModel):
    """
    Modelo de tabla para gestionar documentos con selección por CheckBox.
    
    Campos de documento esperados:
        - universidad: str
        - programa: str
        - estudiante: str
        - nombre: str
        - ruta: str
        - seleccionada: bool (default: True)
    
    Señales:
        selection_changed(): Emitida cuando cambia la selección de checkboxes.
    """
    
    selection_changed = Signal()
    
    # Encabezados de columna
    HEADERS = ["", "Universidad", "Programa", "Estudiante", ""]
    
    def __init__(self, documents: list = None, parent=None):
        """
        Inicializa el modelo con una lista opcional de documentos.
        
        Args:
            documents: Lista de diccionarios con datos de documentos.
            parent: Widget padre (opcional).
        """
        super().__init__(parent)
        self._documents = []
        if documents:
            self.set_documents(documents)
    
    # ==================== MÉTODOS ABSTRACTOS REQUERIDOS ====================
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """
        Retorna el número de filas (documentos) en el modelo.
        
        Args:
            parent: Índice padre (ignorado en modelo plano).
        
        Returns:
            int: Número de documentos.
        """
        if parent.isValid():
            return 0
        return len(self._documents)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """
        Retorna el número de columnas en el modelo.
        
        Args:
            parent: Índice padre (ignorado en modelo plano).
        
        Returns:
            int: Siempre 5 columnas.
        """
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    
    def data(self, index: QModelIndex(), role=Qt.ItemDataRole) -> any:
        """
        Retorna los datos para el índice y rol dados.
        
        Args:
            index: Índice de celda.
            role: Rol de datos (DisplayRole, CheckStateRole, etc.).
        
        Returns:
            Datos según el rol solicitado o None si no aplica.
        """
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if row < 0 or row >= len(self._documents):
            return None
        
        document = self._documents[row]
        
        # CheckBox en columna 0
        if col == 0 and role == Qt.CheckStateRole:
            return Qt.Checked if document.get('seleccionada', False) else Qt.Unchecked
        
        # Texto del CheckBox (columna 0 vacía para no mostrar header)
        if col == 0 and role == Qt.DisplayRole:
            return ""
        
        # Columna Nombre (columna 4) también vacía
        if col == 4 and role == Qt.DisplayRole:
            return ""
        
        # Datos de texto para otras columnas
        if role == Qt.DisplayRole:
            if col == 1:
                return document.get('universidad', '')
            elif col == 2:
                return document.get('programa', '')
            elif col == 3:
                return document.get('estudiante', '')
            elif col == 4:
                return document.get('nombre', '')
        
        # Colores alternados para mejor legibilidad
        if role == Qt.BackgroundRole:
            if row % 2 == 0:
                return QColor("#f8f9fa")
            else:
                return QColor("#ffffff")
        
        return None
    
    def headerData(self, section: int, orientation=Qt.Orientation, 
                   role=Qt.ItemDataRole) -> any:
        """
        Retorna los datos del encabezado de columna/fila.
        
        Args:
            section: Índice de columna o fila.
            orientation: Horizontal o Vertical.
            role: Rol de datos.
        
        Returns:
            Encabezado o None si no aplica.
        """
        if role != Qt.DisplayRole:
            return None
        
        if orientation == Qt.Horizontal:
            if section < len(self.HEADERS):
                return self.HEADERS[section]
        
        return None
    
    def setData(self, index: QModelIndex(), value: any, 
                role=Qt.ItemDataRole) -> bool:
        """
        Actualiza los datos en el índice dado.
        
        Args:
            index: Índice de celda.
            value: Nuevo valor.
            role: Rol de datos (EditRole, CheckStateRole, etc.).
        
        Returns:
            bool: True si la actualización fue exitosa.
        """
        if not index.isValid():
            return False
        
        row = index.row()
        col = index.column()
        
        if row < 0 or row >= len(self._documents):
            return False
        
        # Manejar toggle de CheckBox en columna 0
        if col == 0 and role == Qt.CheckStateRole:
            if value == Qt.Checked:
                self._documents[row]['seleccionada'] = True
            else:
                self._documents[row]['seleccionada'] = False
            
            # Notificar cambio de datos
            index_updated = self.index(row, 0)
            self.dataChanged.emit(index_updated, index_updated, [role])
            self.selection_changed.emit()
            return True
        
        return False
    
    def flags(self, index: QModelIndex()) -> Qt.ItemFlag:
        """
        Retorna los flags del ítem para indicar interactividad.
        
        Args:
            index: Índice de celda.
        
        Returns:
            Flags de ítem combinados.
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        col = index.column()
        
        # Columna 0: habilitada para click de CheckBox
        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
        
        # Otras columnas: solo seleccionables
        return Qt.ItemIsSelectable
    
    # ==================== MÉTODOS DE DATOS ====================
    
    def set_documents(self, documents: list) -> None:
        """
        Reemplaza todos los documentos del modelo.
        
        Args:
            documents: Nueva lista de diccionarios de documentos.
        """
        self.beginResetModel()
        self._documents = documents.copy() if documents else []
        self.endResetModel()
        self.selection_changed.emit()
    
    def get_selected_documents(self) -> list:
        """
        Retorna lista de documentos marcados con checkbox.
        
        Returns:
            Lista de diccionarios de documentos seleccionados.
        """
        return [doc for doc in self._documents if doc.get('seleccionada', False)]
    
    def clear(self) -> None:
        """Limpia todos los documentos del modelo."""
        self.beginResetModel()
        self._documents.clear()
        self.endResetModel()
        self.selection_changed.emit()
    
    def get_document_at_row(self, row: int) -> dict:
        """
        Retorna el documento en la fila especificada.
        
        Args:
            row: Índice de fila.
        
        Returns:
            Diccionario del documento o None si no existe.
        """
        if 0 <= row < len(self._documents):
            return self._documents[row]
        return None
    
    def get_ruta_at_row(self, row: int) -> str:
        """
        Retorna la ruta del documento en la fila especificada.
        
        Args:
            row: Índice de fila.
        
        Returns:
            Ruta del documento o string vacío si no existe.
        """
        doc = self.get_document_at_row(row)
        return doc.get('ruta', '') if doc else ''
    
    # ==================== MÉTODOS DE SELECCIÓN ====================
    
    def toggle_selection(self, row: int) -> None:
        """
        Alterna el estado de selección de un documento.
        
        Args:
            row: Índice de fila del documento.
        """
        if 0 <= row < len(self._documents):
            current = self._documents[row].get('seleccionada', False)
            index = self.index(row, 0)
            self.setData(index, Qt.Unchecked if current else Qt.Checked, 
                        Qt.CheckStateRole)
    
    def select_all(self) -> None:
        """Marca todos los documentos como seleccionados."""
        self.beginResetModel()
        for doc in self._documents:
            doc['seleccionada'] = True
        self.endResetModel()
        self.selection_changed.emit()
    
    def deselect_all(self) -> None:
        """Desmarca todos los documentos."""
        self.beginResetModel()
        for doc in self._documents:
            doc['seleccionada'] = False
        self.endResetModel()
        self.selection_changed.emit()
    
    def invert_selection(self) -> None:
        """Invierte el estado de selección de todos los documentos."""
        self.beginResetModel()
        for doc in self._documents:
            doc['seleccionada'] = not doc.get('seleccionada', False)
        self.endResetModel()
        self.selection_changed.emit()
    
    # ==================== UTILIDADES ====================
    
    def insert_document(self, document: dict, row: int = -1) -> None:
        """
        Inserta un documento en la posición especificada.
        
        Args:
            document: Diccionario con datos del documento.
            row: Posición de inserción (-1 para al final).
        """
        if row == -1:
            row = len(self._documents)
        
        if 0 <= row <= len(self._documents):
            self.beginInsertRows(QModelIndex(), row, row)
            self._documents.insert(row, document)
            self.endInsertRows()
            self.selection_changed.emit()
    
    def remove_document(self, row: int) -> None:
        """
        Elimina un documento en la posición especificada.
        
        Args:
            row: Posición del documento a eliminar.
        """
        if 0 <= row < len(self._documents):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._documents.pop(row)
            self.endRemoveRows()
            self.selection_changed.emit()
    
    def get_selected_count(self) -> int:
        """
        Retorna el número de documentos seleccionados.
        
        Returns:
            int: Cantidad de documentos marcados.
        """
        return sum(1 for doc in self._documents if doc.get('seleccionada', False))
    
    def get_total_count(self) -> int:
        """
        Retorna el número total de documentos.
        
        Returns:
            int: Cantidad total de documentos.
        """
        return len(self._documents)