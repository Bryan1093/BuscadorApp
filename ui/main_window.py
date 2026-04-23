"""
MainWindow - Ventana principal de PySide6 para BuscadorApp.

Sistema de navegación con QStackedWidget de 4 índices:
- Índice 0: LoginWidget (wrapper de LoginView)
- Índice 1: SplashView (pantalla de carga)
- Índice 2: SelectorView (selección Docentes/Oficios)
- Índice 3: BuscadorView (resultados + filtros)

Flujo:
  LoginWidget (index 0)
      ↓ (signal login_success)
  SplashView (index 1) 
      ↓ (signal load_complete)
  SelectorView (index 2)
      ↓ (signal module_selected='docentes'|'oficios')
  BuscadorView (index 3)
      ↓ (signal back_requested)
  Volver a SelectorView (index 2)
"""

from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QLabel, QMessageBox,
    QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, Slot, QSize, Signal
from PySide6.QtGui import QAction
import os

from core import DriveController, DocumentModel, DocumentProxyModel
from ui.views.login_view import LoginView
from ui.views.splash_view import SplashView
from ui.views.selector_view import SelectorView
from ui.views.buscador_view import BuscadorView
from ui.views.acerca_de_view import AcercaDeView
from ui.components.status_footer import StatusFooter
import config.settings as settings


class LoginWidget(QWidget):
    """
    Wrapper para integrar LoginView (QDialog) en el QStackedWidget.
    
    Emite señal login_success cuando el usuario completas el login.
    """
    
    login_success = Signal(str)  # nombre de usuario
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Envuelve LoginView en un widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear el diálogo de login (NO modal para el wrapper)
        self._login_view = LoginView()
        self._login_view.setModal(False)
        
        # Conectar señal interna
        self._login_view.login_success.connect(self._on_login_success)
        
        # Agregar al layout
        layout.addWidget(self._login_view)
    
    def _on_login_success(self, nombre_usuario: str):
        """Re-emite la señal para el stack."""
        self.login_success.emit(nombre_usuario)


class MainWindow(QMainWindow):
    """
    Ventana principal de BuscadorApp.
    
    Gestiona la navegación con QStackedWidget:
    - LoginWidget (index 0): Login integrado
    - SplashView (index 1): Pantalla de carga
    - SelectorView (index 2): Selección de módulo
    - BuscadorView (index 3): Resultados y filtros
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Tema actual
        self._current_theme = "light"
        
        # Controlador singleton
        self._controller = DriveController.get_instance()
        
        # Modelos
        self._model = DocumentModel()
        self._proxy = DocumentProxyModel()
        self._proxy.setSourceModel(self._model)
        
        # Nombre de usuario
        self._nombre_usuario = "Usuario"
        
        # Módulo seleccionado
        self._modulo_actual = None  # 'docentes' o 'oficios'
        
        # Referencias del stack
        self._stack: QStackedWidget = None
        self._login_widget: LoginWidget = None
        self._splash_view: SplashView = None
        self._selector_view: SelectorView = None
        self._buscador_view: BuscadorView = None
        
        # Footer
        self._status_footer: StatusFooter = None
        
        # Referencias de toolbar
        self._action_theme: QAction = None
        
        # Status label
        self._status_label: QLabel = None
        
        # Configurar UI
        self._setup_ui()
        
        # Conectar señales
        self._connect_signals()
        
        # Aplicar tema inicial
        self._apply_theme(self._current_theme)

    # ==================== SETUP UI ====================
    
    def _setup_ui(self):
        """Configura la interfaz de usuario completa."""
        # Configuración de ventana
        self.setWindowTitle("BuscadorApp")
        self.resize(1200, 700)
        self.setMinimumSize(900, 500)
        
        # Toolbar principal
        toolbar = self._create_toolbar()
        self.addToolBar(toolbar)
        
        # Crear QStackedWidget
        self._stack = QStackedWidget()
        self._stack.setContentsMargins(0, 0, 0, 0)
        
        # Índice 0: LoginWidget
        self._login_widget = LoginWidget()
        self._stack.addWidget(self._login_widget)
        
        # Índice 1: SplashView
        self._splash_view = SplashView()
        self._stack.addWidget(self._splash_view)
        
        # Índice 2: SelectorView
        self._selector_view = SelectorView(nombre_usuario=self._nombre_usuario)
        self._stack.addWidget(self._selector_view)
        
        # Índice 3: BuscadorView
        self._buscador_view = BuscadorView(
            controller=self._controller,
            proxy_model=self._proxy
        )
        self._stack.addWidget(self._buscador_view)
        
        # Configurar stack inicial (mostrar login)
        self._stack.setCurrentIndex(0)
        
        # Widget central con footer
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Stack de vistas
        central_layout.addWidget(self._stack, 1)
        
        # Footer de estado
        self._status_footer = StatusFooter()
        central_layout.addWidget(self._status_footer)
        
        self.setCentralWidget(central_widget)
        
        # StatusBar
        self._status_label = QLabel("Listo")
        self.statusBar().addWidget(self._status_label)
    
    def _create_toolbar(self) -> QToolBar:
        """
        Crea la toolbar principal.
        
        Returns:
            QToolBar configurada.
        """
        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Acción: Toggle Theme
        self._action_theme = QAction(
            "☀️" if self._current_theme == "light" else "🌙",
            self
        )
        self._action_theme.setToolTip("Cambiar tema claro/oscuro")
        self._action_theme.triggered.connect(self.toggle_theme)
        toolbar.addAction(self._action_theme)
        
        return toolbar
    
    # ==================== CONEXIÓN DE SEÑALES ====================
    
    def _connect_signals(self):
        """Conecta todas las señales del sistema de navegación."""
        
        # Señales del LoginWidget
        self._login_widget.login_success.connect(self._on_login_success)
        
        # Señales del SplashView
        self._splash_view.load_complete.connect(self._on_load_complete)
        self._splash_view.load_failed.connect(self._on_load_failed)
        
        # Señales del SelectorView
        self._selector_view.module_selected.connect(self._on_module_selected)
        self._selector_view.about_requested.connect(self._on_acerca_de_clicked)
        
        # Señales del BuscadorView
        self._buscador_view.back_requested.connect(self._on_back_to_selector)
        self._buscador_view.theme_toggled.connect(self.toggle_theme)
        
        # Señales del Controller
        self._controller.signals.load_started.connect(self._on_load_started)
        self._controller.signals.load_completed.connect(self._on_documents_loaded)
        self._controller.signals.load_error.connect(self._on_load_error)
        self._controller.signals.status_updated.connect(self._on_status_updated)
    
    # ==================== HANDLERS DE NAVEGACIÓN ====================
    
    def _on_login_success(self, nombre_usuario: str):
        """
        Handler cuando el login es exitoso.
        
        Args:
            nombre_usuario: Nombre del usuario logueado.
        """
        self._nombre_usuario = nombre_usuario
        settings.nombre_usuario_actual = nombre_usuario
        
        # Actualizar footer con usuario
        self._status_footer.set_usuario(nombre_usuario)
        
        self._status_label.setText(f"Bienvenido, {nombre_usuario}")
        
        # Ir al splash
        self._stack.setCurrentIndex(1)
        
        # Iniciar carga
        self._splash_view.start_loading()
    
    def _on_load_complete(self):
        """Handler cuando la carga del splash termina."""
        # Actualizar modelo con los documentos ya cargados por SplashView
        # (el SplashView ya los cargó en el controller)
        
        # Ir al selector
        self._stack.setCurrentIndex(2)
        
        # Actualizar saludo en el selector
        self._selector_view.actualizar_saludo(self._nombre_usuario)
        
        self._status_label.setText("Selecciona un módulo")
    
    def _on_load_failed(self, error_msg: str):
        """
        Handler cuando la carga falla.
        
        Args:
            error_msg: Mensaje de error.
        """
        QMessageBox.critical(
            self,
            "Error de Carga",
            f"Error al cargar documentos:\n{error_msg}"
        )
        
        # Volver al selector
        self._stack.setCurrentIndex(2)
        self._status_label.setText("Error en carga")
    
    def _on_module_selected(self, modulo: str):
        """
        Handler cuando se selecciona un módulo.
        
        Args:
            modulo: 'docentes' o 'oficios'
        """
        self._modulo_actual = modulo
        
        # Configurar el filtro en el proxy
        self._proxy.filter_tipo = modulo
        
        # Actualizar título del buscador
        self._buscador_view.set_modulo(modulo)
        
        # Ir al buscador
        self._stack.setCurrentIndex(3)
        
        self._status_label.setText(f"Módulo: {modulo.capitalize()}")
    
    def _on_back_to_selector(self):
        """Handler para volver al selector."""
        self._stack.setCurrentIndex(2)
        self._status_label.setText("Selecciona un módulo")
    
    def _on_acerca_de_clicked(self):
        """Muestra el diálogo Acerca de."""
        acerca = AcercaDeView(self)
        acerca.exec()
    
    # ==================== HANDLERS DEL CONTROLLER ====================
    
    def _on_load_started(self):
        """Handler cuando inicia la carga de documentos."""
        self._status_label.setText("Cargando...")
    
    def _on_documents_loaded(self, documents: list):
        """
        Handler cuando se completan de cargar los documentos.
        
        Args:
            documents: Lista de documentos cargados.
        """
        # Actualizar modelo
        self._model.set_documents(documents)
        
        # Actualizar label de estado
        total = self._model.get_total_count()
        self._status_label.setText(f"{total} documentos cargados")
    
    def _on_load_error(self, error_msg: str):
        """
        Handler cuando hay error en carga.
        
        Args:
            error_msg: Mensaje de error.
        """
        QMessageBox.critical(
            self,
            "Error de Carga",
            f"Error al cargar documentos:\n{error_msg}"
        )
        self._status_label.setText("Error en carga")
    
    def _on_status_updated(self, message: str):
        """
        Handler para mensajes de estado.
        
        Args:
            message: Mensaje a mostrar.
        """
        self._status_label.setText(message)
    
    # ==================== TEMA ====================
    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro."""
        self._current_theme = "dark" if self._current_theme == "light" else "light"
        self._apply_theme(self._current_theme)
        
        # Actualizar icono del botón de tema
        nuevo_icono = "🌙" if self._current_theme == "dark" else "☀️"
        self._action_theme.setText(nuevo_icono)
        
        # Actualizar icono en el buscador
        is_dark = self._current_theme == "dark"
        self._buscador_view.set_theme_icon(is_dark)
        
        # Actualizar fondo grid en SelectorView y BuscadorView
        if hasattr(self._selector_view, 'set_theme'):
            self._selector_view.set_theme(is_dark)
        if hasattr(self._buscador_view, 'set_theme'):
            self._buscador_view.set_theme(is_dark)
    
    def _apply_theme(self, theme: str):
        """
        Aplica el tema especificado.
        
        Args:
            theme: "light" o "dark".
        """
        # Construir ruta al archivo QSS
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qss_path = os.path.join(
            base_dir,
            "ui",
            "components",
            "styles",
            f"{theme}.qss"
        )
        
        # Leer y aplicar QSS
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss_content = f.read()
            self.setStyleSheet(qss_content)
            print(f"[MainWindow] Tema aplicado: {theme}")
        except FileNotFoundError:
            print(f"[MainWindow] ERROR: No se encontró {qss_path}")
        except Exception as e:
            print(f"[MainWindow] ERROR al aplicar tema: {e}")
    
    # ==================== UTILIDADES ====================
    
    def center(self):
        """Centra la ventana en la pantalla."""
        screen_geometry = self.screen().geometry()
        window_geometry = self.frameGeometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(screen_geometry.x() + x, screen_geometry.y() + y)