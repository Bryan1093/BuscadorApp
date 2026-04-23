"""
DriveController - Bridge entre PySide6 UI y el Backend existente.

Este controlador acts como intermediario entre la UI de PySide6 y los servicios
de búsqueda/archivos existentes, usando Signals y Slots para comunicación asíncrona.
"""
from PySide6.QtCore import QObject, Signal, Slot, QThread, QThreadPool, QRunnable
from PySide6.QtWidgets import QApplication
from typing import Optional, Dict, List, Any
import traceback

# Importar servicios del backend
import config.settings as settings
from services.search_service import (
    buscar_documentos,
    buscar_oficios,
    obtener_programas_filtrados,
    obtener_estudiantes_filtrados,
    obtener_items_clave_filtrados
)
from services.file_service import (
    cargar_documentos,
    cargar_documentos_oficios,
    abrir_pdf,
    abrir_carpeta,
    descargar_pdf,
    descargar_expediente,
    descargar_expediente_multiple,
    sincronizar_drive
)
from utils.path_utils import encontrar_rutas_drive


# ==============================================================================
# SEÑALES DEL CONTROLADOR
# ==============================================================================

class DriveControllerSignals(QObject):
    """Señales emitidas por DriveController"""
    
    # Carga de documentos
    load_started = Signal()                          # Inicio de carga
    load_progress = Signal(str, int)                 # (carpeta_actual, num_documentos)
    load_completed = Signal(list)                    # Lista de documentos cargados
    load_error = Signal(str)                         # Error durante carga
    
    # Búsqueda
    search_started = Signal()                        # Inicio de búsqueda
    search_completed = Signal(list)                  # Resultados de búsqueda
    search_error = Signal(str)                       # Error durante búsqueda
    
    # Filtros
    filters_updated = Signal(dict)                   # Opciones actualizadas de filtros
    
    # Estado
    status_updated = Signal(str)                     # Mensaje para status bar
    error_occurred = Signal(str, str)                # (título, mensaje)


# ==============================================================================
# TAREA ASÍNCRONA PARA CARGA DE DOCUMENTOS
# ==============================================================================

class LoadDocumentsTask(QRunnable):
    """Tarea asíncrona para cargar documentos desde Drive"""
    
    def __init__(self, controller: 'DriveController', ruta1: str, ruta2: str, ruta_oficios: str = None):
        super().__init__()
        self.controller = controller
        self.ruta1 = ruta1
        self.ruta2 = ruta2
        self.ruta_oficios = ruta_oficios
        self.setAutoDelete(True)
    
    def run(self):
        """Ejecuta la carga de documentos en thread separado"""
        try:
            # Notificar inicio
            self.controller.signals.load_started.emit()
            self.controller.signals.status_updated.emit("Iniciando carga de documentos...")
            
            documentos = []
            
            # Cargar desde ruta1 (Doctorados)
            if self.ruta1:
                self.controller.signals.status_updated.emit(f"Escaneando {self.ruta1}...")
                self.controller.signals.load_progress.emit(self.ruta1, len(documentos))
                docs1 = cargar_documentos(self.ruta1)
                documentos.extend(docs1)
            
            # Cargar desde ruta2 (Doctorados2)
            if self.ruta2:
                self.controller.signals.status_updated.emit(f"Escaneando {self.ruta2}...")
                self.controller.signals.load_progress.emit(self.ruta2, len(documentos))
                docs2 = cargar_documentos(self.ruta2)
                documentos.extend(docs2)
            
            # Cargar oficios (si se proporciona ruta)
            if self.ruta_oficios:
                self.controller.signals.status_updated.emit(f"Escaneando oficios {self.ruta_oficios}...")
                oficios = cargar_documentos_oficios(self.ruta_oficios)
                settings.documentos_oficios = oficios
                documentos.extend(oficios)
            
            # Actualizar settings global
            settings.documentos_drive = documentos
            settings.documentos_cargados = True
            
            # Notificar éxito
            self.controller.signals.load_completed.emit(documentos)
            self.controller.signals.status_updated.emit(
                f"✓ {len(documentos)} documentos cargados"
            )
            
        except Exception as e:
            error_msg = f"Error al cargar documentos: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(traceback.format_exc())
            self.controller.signals.load_error.emit(error_msg)
            self.controller.signals.error_occurred.emit("Error de carga", error_msg)


# ==============================================================================
# TAREA ASÍNCRONA PARA BÚSQUEDA
# ==============================================================================

class SearchDocumentsTask(QRunnable):
    """Tarea asíncrona para buscar documentos"""
    
    def __init__(self, controller: 'DriveController', 
                 filtro_u: str, filtro_p: str, filtro_e: str, 
                 filtro_nombre: str, filtro_item: str):
        super().__init__()
        self.controller = controller
        self.filtro_u = filtro_u
        self.filtro_p = filtro_p
        self.filtro_e = filtro_e
        self.filtro_nombre = filtro_nombre
        self.filtro_item = filtro_item
        self.setAutoDelete(True)
    
    def run(self):
        """Ejecuta la búsqueda en thread separado"""
        try:
            self.controller.signals.search_started.emit()
            
            resultados = buscar_documentos(
                self.filtro_u,
                self.filtro_p,
                self.filtro_e,
                self.filtro_nombre,
                self.filtro_item
            )
            
            self.controller.signals.search_completed.emit(resultados)
            self.controller.signals.status_updated.emit(
                f"Mostrando {len(resultados)} resultado(s)"
            )
            
        except Exception as e:
            error_msg = f"Error en búsqueda: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(traceback.format_exc())
            self.controller.signals.search_error.emit(error_msg)


# ==============================================================================
# CONTROLADOR PRINCIPAL
# ==============================================================================

class DriveController(QObject):
    """
    Controlador principal que gestiona la comunicación entre UI y servicios.
    
    Uso:
        controller = DriveController()
        controller.load_documents(ruta1, ruta2)
        
        # Conectar señales
        controller.signals.load_completed.connect(self.on_documents_loaded)
        controller.signals.search_completed.connect(self.on_search_results)
    """
    
    # Instancia singleton
    _instance: Optional['DriveController'] = None
    
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        
        # Señales
        self.signals = DriveControllerSignals()
        
        # Thread pool para tareas asíncronas
        self._thread_pool = QThreadPool.globalInstance()
        
        # Rutas de Drive
        self._ruta_doctorados: Optional[str] = None
        self._ruta_doctorados2: Optional[str] = None
        self._ruta_oficios: Optional[str] = None
        
        # Rutas por documento (para abrir PDFs)
        self._ruta_por_iid: Dict[str, str] = {}
        
        # Singleton
        DriveController._instance = self
    
    @classmethod
    def instance(cls) -> Optional['DriveController']:
        """Retorna la instancia singleton del controlador"""
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'DriveController':
        """Retorna la instancia, creándola si no existe"""
        if cls._instance is None:
            cls._instance = DriveController()
        return cls._instance
    
    # ==========================================================================
    # MÉTODOS PÚBLICOS - CARGA DE DOCUMENTOS
    # ==========================================================================
    
    def initialize_routes(self):
        """Inicializa las rutas de Drive"""
        (self._ruta_doctorados, 
         self._ruta_oficios, 
         self._ruta_doctorados2) = encontrar_rutas_drive()
        
        print(f"[DriveController] Rutas inicializadas:")
        print(f"  Doctorados: {self._ruta_doctorados}")
        print(f"  Doctorados2: {self._ruta_doctorados2}")
        print(f"  Oficios: {self._ruta_oficios}")
        
        return (self._ruta_doctorados, self._ruta_oficios, self._ruta_doctorados2)
    
    def load_documents(self, ruta1: str = None, ruta2: str = None, ruta_oficios: str = None):
        """
        Carga documentos de forma asíncrona.
        
        Args:
            ruta1: Primera ruta de doctorados (opcional, usa la guardada)
            ruta2: Segunda ruta de doctorados (opcional, usa la guardada)
            ruta_oficios: Ruta de oficios (opcional, usa la guardada)
        """
        if ruta1 is None:
            ruta1 = self._ruta_doctorados
        if ruta2 is None:
            ruta2 = self._ruta_doctorados2
        if ruta_oficios is None:
            ruta_oficios = self._ruta_oficios
        
        # Usar thread pool para carga asíncrona
        task = LoadDocumentsTask(self, ruta1, ruta2, ruta_oficios)
        self._thread_pool.start(task)
    
    def load_documents_sync(self, ruta1: str = None, ruta2: str = None) -> List[Dict]:
        """
        Carga documentos de forma síncrona (bloqueante).
        Útil para inicialización rápida sin UI.
        """
        if ruta1 is None:
            ruta1 = self._ruta_doctorados
        if ruta2 is None:
            ruta2 = self._ruta_doctorados2
        
        documentos = []
        
        try:
            if ruta1:
                documentos.extend(cargar_documentos(ruta1))
            if ruta2:
                documentos.extend(cargar_documentos(ruta2))
            
            # Actualizar settings
            settings.documentos_drive = documentos
            settings.documentos_cargados = True
            
            return documentos
            
        except Exception as e:
            print(f"[ERROR] Error en carga síncrona: {e}")
            self.signals.load_error.emit(str(e))
            return []
    
    # ==========================================================================
    # MÉTODOS PÚBLICOS - BÚSQUEDA
    # ==========================================================================
    
    def search(self, filtro_u: str = "(Todos)", 
               filtro_p: str = "(Todos)",
               filtro_e: str = "(Todos)",
               filtro_nombre: str = "",
               filtro_item: str = "(Todos)"):
        """
        Busca documentos de forma asíncrona.
        
        Args:
            filtro_u: Filtro de universidad
            filtro_p: Filtro de programa
            filtro_e: Filtro de estudiante
            filtro_nombre: Texto a buscar en nombre
            filtro_item: Filtro de ítem clave
        """
        task = SearchDocumentsTask(
            self, filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item
        )
        self._thread_pool.start(task)
    
    def search_sync(self, filtro_u: str = "(Todos)", 
                    filtro_p: str = "(Todos)",
                    filtro_e: str = "(Todos)",
                    filtro_nombre: str = "",
                    filtro_item: str = "(Todos)") -> List[Dict]:
        """
        Busca documentos de forma síncrona (bloqueante).
        """
        try:
            return buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item)
        except Exception as e:
            print(f"[ERROR] Error en búsqueda: {e}")
            self.signals.search_error.emit(str(e))
            return []
    
    # ==========================================================================
    # MÉTODOS PÚBLICOS - OBTENER FILTROS
    # ==========================================================================
    
    def get_universidades(self) -> List[str]:
        """Retorna lista de universidades disponibles"""
        universidades = set()
        for doc in settings.documentos_drive:
            # Intentar múltiples claves posibles para institución
            uni = (doc.get('universidad') or doc.get('universidad_docente') 
                  or doc.get('institucion') or doc.get('universidad_oficios'))
            if uni:
                universidades.add(uni)
        return sorted(universidades)
    
    def get_programas(self, universidad: str = "(Todos)") -> List[str]:
        """Retorna programas filtrados por universidad"""
        return obtener_programas_filtrados(universidad)
    
    def get_estudiantes(self, universidad: str, programa: str) -> List[str]:
        """Retorna estudiantes filtrados"""
        return obtener_estudiantes_filtrados(universidad, programa)
    
    def get_items_clave(self, universidad: str, programa: str, estudiante: str) -> List[str]:
        """Retorna ítems clave filtrados"""
        return obtener_items_clave_filtrados(universidad, programa, estudiante)
    
    # ==========================================================================
    # MÉTODOS PÚBLICOS - ACCIONES SOBRE DOCUMENTOS
    # ==========================================================================
    
    def open_pdf(self, ruta: str):
        """Abre un PDF con la aplicación predeterminada"""
        try:
            abrir_pdf(ruta)
        except Exception as e:
            self.signals.error_occurred.emit("Error", f"No se pudo abrir el PDF:\n{e}")
    
    def open_folder(self, ruta: str):
        """Abre la carpeta que contiene el documento"""
        try:
            abrir_carpeta(ruta)
        except Exception as e:
            self.signals.error_occurred.emit("Error", f"No se pudo abrir la carpeta:\n{e}")
    
    def download_pdf(self, ruta: str):
        """Descarga una copia del PDF"""
        try:
            descargar_pdf(ruta)
        except Exception as e:
            self.signals.error_occurred.emit("Error", f"No se pudo descargar:\n{e}")
    
    def download_expediente(self, ruta_pdf: str):
        """Descarga el expediente completo del estudiante"""
        try:
            descargar_expediente(ruta_pdf)
        except Exception as e:
            self.signals.error_occurred.emit("Error", f"No se pudo descargar expediente:\n{e}")
    
    def download_multiple(self, rutas: List[str]):
        """Descarga múltiples documentos como ZIP"""
        try:
            descargar_expediente_multiple(rutas)
        except Exception as e:
            self.signals.error_occurred.emit("Error", f"No se pudo crear ZIP:\n{e}")
    
    # ==========================================================================
    # MÉTODOS DE UTILIDAD
    # ==========================================================================
    
    def get_ruta_by_iid(self, iid: str) -> Optional[str]:
        """Retorna la ruta de un documento por su ID"""
        return self._ruta_por_iid.get(iid)
    
    def set_ruta_by_iid(self, iid: str, ruta: str):
        """Asocia una ruta a un ID de documento"""
        self._ruta_por_iid[iid] = ruta
    
    def clear_ruta_por_iid(self):
        """Limpia el diccionario de rutas"""
        self._ruta_por_iid.clear()
    
    @property
    def ruta_doctorados(self) -> Optional[str]:
        return self._ruta_doctorados
    
    @property
    def ruta_doctorados2(self) -> Optional[str]:
        return self._ruta_doctorados2
    
    @property
    def ruta_oficios(self) -> Optional[str]:
        return self._ruta_oficios
    
    @property
    def documentos_count(self) -> int:
        return len(settings.documentos_drive)
    
    @property
    def is_loaded(self) -> bool:
        return settings.documentos_cargados and settings.documentos_drive

    # ==========================================================================
    # MÉTODOS PÚBLICOS - FILTROS DE OFICIOS
    # ==========================================================================

    def get_anios_oficios(self) -> List[str]:
        """Retorna lista de años únicos de los documentos de oficios"""
        # Obtener documentos de oficios
        if hasattr(settings, 'documentos_oficios') and settings.documentos_oficios:
            docs = settings.documentos_oficios
        else:
            # Si no hay oficios cargados,返回 vacío o buscar en documentos_drive
            return []
        
        # Extraer año de la ruta o fecha
        anios = set()
        for doc in docs:
            ruta = doc.get('ruta', '')
            # El año puede estar en la ruta (ej: /2024/)
            import re
            match = re.search(r'/(\d{4})/', ruta)
            if match:
                anios.add(match.group(1))
            # O del campo año si existe
            elif doc.get('ano'):
                anios.add(str(doc['ano']))
        
        return sorted(anios, reverse=True)

    def get_tipos_oficio(self) -> List[str]:
        """Retorna lista de tipos únicos de oficios"""
        # Obtener documentos de oficios
        if hasattr(settings, 'documentos_oficios') and settings.documentos_oficios:
            docs = settings.documentos_oficios
        else:
            return []
        
        # Extraer tipo del nombre del archivo o ruta
        tipos = set()
        for doc in docs:
            nombre = doc.get('nombre', '')
            # El tipo puede estar al inicio del nombre
            if nombre:
                # Buscar patrón como "Tipo - Nombre.pdf"
                parts = nombre.split(' - ', 1)
                if len(parts) > 1:
                    tipos.add(parts[0].strip())
                # O usar el nombre completo si no hay patrón claro
                else:
                    tipos.add(nombre.split('.')[0].strip())
        
        return sorted(tipos)