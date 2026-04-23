"""
Módulo Core - Controladores y modelos de datos para PySide6

Contiene:
    - controller.py: DriveController (Bridge UI ↔ Backend)
    - models.py: DocumentModel (QAbstractTableModel)
    - proxy_model.py: DocumentProxyModel (QSortFilterProxyModel)
"""
from .controller import DriveController, DriveControllerSignals
from .models import DocumentModel
from .proxy_model import DocumentProxyModel, COL_CHECK, COL_UNIVERSIDAD, COL_PROGRAMA, COL_ESTUDIANTE, COL_NOMBRE

__all__ = [
    'DriveController',
    'DriveControllerSignals',
    'DocumentModel',
    'DocumentProxyModel',
    'COL_CHECK',
    'COL_UNIVERSIDAD',
    'COL_PROGRAMA',
    'COL_ESTUDIANTE',
    'COL_NOMBRE',
]