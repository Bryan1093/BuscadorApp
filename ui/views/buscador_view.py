"""
BuscadorView - Vista principal del buscador de documentos.

Widget contenedor que integra:
- Panel lateral izquierdo con filtros (QFrame con sombra neumórfica)
- Área derecha con toolbar integrada y tabla de resultados
- Layout horizontal: [Filtros | Resultados+Toolbar]

Signals:
    back_requested: Emitido cuando el usuario quiere volver al selector.
    document_opened: Emitido cuando se abre un documento (con ruta).
    theme_toggled: Emitido cuando se togglea el tema claro/oscuro.
    sync_requested: Emitido cuando se sincroniza documentos.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QToolBar, 
    QFrame, QLabel, QPushButton, QGraphicsDropShadowEffect, QComboBox,
    QTabWidget, QStackedWidget
)
from PySide6.QtCore import Signal, QEvent, Qt
from PySide6.QtGui import QAction, QColor, QBrush, QPainter, QLinearGradient, QPen, QPixmap, QLinearGradient

from ui.components.sidebar import FiltersSidebar
from ui.components.results_table import ResultsTable
from ui.styles.render_engine import CyberGridBackground


class BuscadorView(CyberGridBackground):
    """
    Vista del buscador - integra panel de filtros y tabla de resultados.

    Widget principal para browsing de documentos con filtrado en cascada
    (Universidad → Programa → Estudiante) y apertura de PDFs.

    Anatomía:
        ┌─────────────────────────────────────────────────────────┐
        │  UCE    📚 DOCENTES           [Theme] [Volver]        │
        ├─────────────────────────────────────────────────────────┤
        │                  │                                      │
        │  PANEL FILTROS  │      RESULTS TABLE                 │
        │  (QFrame con   │      (QStackedWidget)               │
        │   sombra)     │      [Docentes | Oficios toggle]    │
        │                  │                                      │
        │  Universidad   │                                      │
        │  Programa      │                                      │
        │  Estudiante    │                                      │
        │  Item Clave   │                                      │
        │                  │                                      │
        ├─────────────────┴──────────────────────────────────┤
        │   [👨‍🏫 Docentes]      [📋 Oficios]                    │
        └─────────────────────────────────────────────────────────┘

    Attributes:
        back_requested: Signal() — Cuando usuario hace click en "Volver".
        document_opened: Signal(str) — Cuando se abre un documento (ruta).
        theme_toggled: Signal() — Cuando se cambia el tema.
        sync_requested: Signal() — Cuando se sincroniza documentos.
    """

    # ==================== SEÑALES ====================
    back_requested = Signal()
    document_opened = Signal(str)
    theme_toggled = Signal()
    sync_requested = Signal()

    def __init__(self, controller, proxy_model, parent=None):
        """
        Inicializa la vista del buscador.

        Args:
            controller: DriveController para operaciones de datos.
            proxy_model: DocumentProxyModel para filtrado.
            parent: Widget padre (opcional).
        """
        # Determinar tema actual
        is_dark = getattr(parent, '_current_theme', None) == 'dark' if parent else False
        super().__init__(parent, is_dark=is_dark)
        self._controller = controller
        self._proxy = proxy_model
        self._modulo = "docentes"

        self._setup_ui()
        self._connect_signals()

    # ==================== UI ====================

    def _setup_ui(self):
        """
        Configura el layout y widgets internos.
        
        Estructura:
            - QHBoxLayout principal
            - Panel izquierdo: QFrame con filtros (280px fijo, sombra)
            - Panel derecho: QVBoxLayout con toolbar + tabla
        """
        # ==== LAYOUT PRINCIPAL (HORIZONTAL) ====
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # ==== PANEL IZQUIERDO: FILTROS (QFrame con sombra) ====
        self._panel_filtros = self._create_filters_panel()
        main_layout.addWidget(self._panel_filtros)

        # ==== PANEL DERECHO: TOOLBAR + RESULTADOS ====
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)

    def _create_filters_panel(self) -> QFrame:
        """
        Crea el panel de filtros como QFrame con sombra neumórfica.
        
        Returns:
            QFrame: Panel de filtros con shadow effect.
        """
        # Frame contenedor
        panel = QFrame()
        panel.setFixedWidth(280)
        
        # Efecto de sombra neumórfica
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(3, 3)
        shadow.setColor(QColor(0, 0, 0, 60))  # rgba(0,0,0,60)
        panel.setGraphicsEffect(shadow)

        # Layout interno
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ==== TÍTULO CON LÍNEA DE ACENTO ====
        title_label = QLabel("Filtros")
        font_titulo = title_label.font()
        font_titulo.setBold(True)
        font_titulo.setPointSize(13)
        title_label.setFont(font_titulo)
        layout.addWidget(title_label)

        # Línea de acento cian
        accent_line = QWidget()
        accent_line.setFixedSize(60, 3)
        accent_line.setStyleSheet("""
            background-color: #3498db;
            border-radius: 2px;
        """)
        layout.addWidget(accent_line)

        #Espacio
        layout.addSpacing(8)

        # ==== COMBOS DE FILTROS ====
        # Usar el FiltersSidebar existente para la lógica
        self._sidebar = FiltersSidebar(self._proxy, self._controller)
        layout.addWidget(self._sidebar)

        layout.addStretch()

        # ==== ESTILOS DEL PANEL ====
        # Fondo sólido para que el grid no se vea a través
        panel.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
            }
        """)

        return panel

    def _create_right_panel(self) -> QWidget:
        """
        Crea el panel derecho con toolbar integrada, tabla y tabs inferiores.
        
        Estructura:
            - Toolbar con título y logo UCE
            - Línea de acento cian
            - Tabla de resultados (contenido del tab)
            - Tabs en la parte inferior
        
        Returns:
            QWidget: Panel derecho con layout vertical.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ==== TOOLBAR INTEGRADA ====
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # ==== LÍNEA DE ACENTO BAJO TÍTULO ====
        self._accent_line = self._create_accent_line()
        layout.addWidget(self._accent_line)

        # ==== CONTENIDO (StackedWidget para cambiar entre Docentes/Oficios) ====
        self._content_stack = QStackedWidget()
        
        # Página de Docentes
        self._results_docentes = ResultsTable(self._proxy, self._controller)
        self._content_stack.addWidget(self._results_docentes)
        
        # Página de Oficios
        self._results_oficios = ResultsTable(self._proxy, self._controller)
        self._results_oficios.set_modulo("oficios")
        self._content_stack.addWidget(self._results_oficios)
        
        layout.addWidget(self._content_stack, 1)

        # ==== TABS EN LA PARTE INFERIOR ====
        self._tabs_bar = self._create_tabs_bar()
        layout.addWidget(self._tabs_bar)

        return panel

    def _create_toolbar(self) -> QToolBar:
        """
        Crea y retorna la toolbar integrada.

        Toolbar con:
        - Título del módulo con l��nea de acento
        - Botón Sincronizar con glow
        - Botón Abrir PDF
        - Botón Volver
        - Botón Theme toggle
        
        Returns:
            QToolBar: Toolbar configurada con acciones.
        """
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Logo UCE a la izquierda del título
        logo_widget = self._load_logo()
        toolbar.addWidget(logo_widget)

        # Título dinámico según módulo
        icono = "📚"
        self._title_action = QAction(f"{icono} DOCENTES", self)
        self._title_action.setEnabled(False)
        toolbar.addAction(self._title_action)

        toolbar.addSeparator()

        # ===== BOTONES PRINCIPALES =====

        # Botón: Sincronizar (antes "Actualizar")
        act_sincronizar = QAction("🔄 Sincronizar", self)
        act_sincronizar.setToolTip("Sincronizar documentos")
        act_sincronizar.triggered.connect(self._on_sync)
        toolbar.addAction(act_sincronizar)

        # Botón: Abrir PDF
        act_abrir = QAction("📄 Abrir PDF", self)
        act_abrir.setToolTip("Abrir documento seleccionado")
        act_abrir.triggered.connect(self._on_abrir)
        toolbar.addAction(act_abrir)

        toolbar.addSeparator()

        # Botón: Volver al selector
        act_volver = QAction("↩️ Volver", self)
        act_volver.setToolTip("Volver a la selección de módulo")
        act_volver.triggered.connect(self._on_back)
        toolbar.addAction(act_volver)

        toolbar.addSeparator()

        # Theme toggle
        self._theme_action = QAction("☀️", self)
        self._theme_action.setToolTip("Cambiar tema claro/oscuro")
        self._theme_action.triggered.connect(self._on_theme_toggle)
        toolbar.addAction(self._theme_action)

        # Aplicar glow a los botones de la toolbar
        self._apply_toolbar_glow(toolbar)

        return toolbar

    def _create_accent_line(self) -> QWidget:
        """
        Crea la línea de acento cian debajo del título.
        
        Línea: 60px width, 3px height, color #3498db, border-radius: 2px

        Returns:
            QWidget con la línea de acento.
        """
        line = QWidget()
        line.setFixedSize(60, 3)
        line.setStyleSheet("""
            background-color: #3498db;
            border-radius: 2px;
        """)
        return line

    def _create_tabs_bar(self) -> QFrame:
        """
        Crea la barra de tabs en la parte inferior.
        
        Tabs: "Docentes" | "Oficios"
        - Estilo moderno con highlight cian en tab activo
        - Cambio de contenido al tocar un tab
        
        Returns:
            QFrame con los botones de tabs.
        """
        tabs_frame = QFrame()
        tabs_frame.setFixedHeight(50)
        tabs_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-top: 1px solid #d0d0d0;
            }
        """)
        
        layout = QHBoxLayout(tabs_frame)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Botón Docentes (por defecto activo)
        self._tab_docentes = QPushButton("👨‍🏫 Docentes")
        self._tab_docentes.setCheckable(True)
        self._tab_docentes.setChecked(True)
        self._tab_docentes.setFixedSize(140, 36)
        self._tab_docentes.clicked.connect(lambda: self._on_tab_changed("docentes"))
        self._style_tab_button(self._tab_docentes, active=True)
        
        # Botón Oficios
        self._tab_oficios = QPushButton("📋 Oficios")
        self._tab_oficios.setCheckable(True)
        self._tab_oficios.setFixedSize(140, 36)
        self._tab_oficios.clicked.connect(lambda: self._on_tab_changed("oficios"))
        self._style_tab_button(self._tab_oficios, active=False)
        
        layout.addStretch()
        layout.addWidget(self._tab_docentes)
        layout.addWidget(self._tab_oficios)
        layout.addStretch()

        return tabs_frame

    def _style_tab_button(self, button: QPushButton, active: bool):
        """
        Aplica estilo moderno a un botón de tab.
        
        Args:
            button: QPushButton al que aplicar el estilo.
            active: True si es el tab activo (destacado).
        """
        if active:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 18px;
                    font: bold 13px 'Segoe UI';
                    padding: 8px 16px;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #666666;
                    border: 2px solid #cccccc;
                    border-radius: 18px;
                    font: 13px 'Segoe UI';
                    padding: 8px 16px;
                }
            """)

    def _on_tab_changed(self, modulo: str):
        """
        Cambia entre Docentes y Oficios cuando se toca un tab.
        
        Args:
            modulo: "docentes" o "oficios".
        """
        self._modulo = modulo
        
        # Actualizar estilo de botones
        self._style_tab_button(self._tab_docentes, active=(modulo == "docentes"))
        self._style_tab_button(self._tab_oficios, active=(modulo == "oficios"))
        
        # Actualizar título en toolbar
        icono = "📚" if modulo == "docentes" else "📋"
        self._title_action.setText(f"{icono} {modulo.upper()}")
        
        # Cambiar contenido en stacked widget
        index = 0 if modulo == "docentes" else 1
        self._content_stack.setCurrentIndex(index)
        
        # Actualizar filtro del proxy model
        self._proxy.filter_tipo = modulo
        
        # Actualizar sidebar
        self._sidebar.set_modo(modulo)

    def _add_glow_effect(self, button):
        """
        Agrega efecto glow cian a un botón.

        Args:
            button: QPushButton al que se le aplicará el efecto.
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#3498db"))
        shadow.setOffset(0, 0)
        button.setGraphicsEffect(shadow)

    def _apply_toolbar_glow(self, toolbar: QToolBar):
        """
        Aplica efecto glow a los botones de la toolbar en hover.

        Args:
            toolbar: QToolBar con los botones.
        """
        for action in toolbar.actions():
            widget = toolbar.widgetForAction(action)
            if widget is not None and isinstance(widget, QPushButton):
                widget.installEventFilter(self)
                self._add_glow_effect(widget)

    # ==================== CONEXIONES ====================

    def _connect_signals(self):
        """Conecta señales internas y del controller."""
        # Señales de ambas tablas (docentes y oficios)
        self._results_docentes.document_selected.connect(self._on_document_selected)
        self._results_oficios.document_selected.connect(self._on_document_selected)
        
        # Señales del sidebar
        self._sidebar.filter_changed.connect(self._on_filter_changed)

        # Señales del controller
        self._controller.signals.load_started.connect(self._on_load_started)
        self._controller.signals.load_completed.connect(self._on_load_completed)

    def _get_current_results(self) -> ResultsTable:
        """Retorna la tabla de resultados activa según el tab."""
        if self._content_stack.currentIndex() == 0:
            return self._results_docentes
        return self._results_oficios

    # ==================== HANDLERS ====================

    def _on_back(self):
        """Handler para acción de volver al selector."""
        self.back_requested.emit()

    def _on_sync(self):
        """Handler para acción de sincronizar documentos."""
        self._controller.load_documents()
        self.sync_requested.emit()

    def _on_abrir(self):
        """Handler para acción de abrir PDF del documento actual."""
        results = self._get_current_results()
        ruta = results.get_current_route()
        if ruta:
            self._controller.open_pdf(ruta)

    def _on_theme_toggle(self):
        """Handler para toggle de tema."""
        self.theme_toggled.emit()

    def _on_document_selected(self, ruta: str):
        """
        Handler cuando se selecciona un documento en la tabla.

        Args:
            ruta: Ruta del documento seleccionado.
        """
        self.document_opened.emit(ruta)

    def _on_filter_changed(self, filters: dict):
        """
        Handler cuando cambian los filtros.

        Args:
            filters: Diccionario con valores de filtros.
        """
        # Los filtros ya están aplicados al proxy_model por FiltersSidebar
        pass

    def _on_load_started(self):
        """Handler cuando inicia carga de documentos."""
        pass

    def _on_load_completed(self, documentos):
        """
        Handler cuando se completan de cargar documentos.

        Args:
            documentos: Lista de documentos cargados.
        """
        pass

    # ==================== APIS PÚBLICAS ====================

    def set_modulo(self, modulo: str):
        """
        Cambiar entre módulos "docentes" / "oficios".

        Args:
            modulo: Nombre del módulo ("docentes" o "oficios").
        """
        self._modulo = modulo
        icono = "📚" if modulo == "docentes" else "📋"
        self._title_action.setText(f"{icono} {modulo.upper()}")
        self._proxy.filter_tipo = modulo

        # Cambiar tab activo
        self._on_tab_changed(modulo)

    def set_theme_icon(self, is_dark: bool):
        """
        Actualizar icono del botón de tema.

        Args:
            is_dark: True si el tema actual es oscuro.
        """
        self._theme_action.setText("🌙" if is_dark else "☀️")

    def refresh(self):
        """Refresca los datos de la vista."""
        self._controller.load_documents()

    def eventFilter(self, obj, event):
        """
        Filtro de eventos para glow en hover de botones.

        Args:
            obj: Objeto que recibe el evento.
            event: QEvent procesado.

        Returns:
            bool: True si el evento fue manejado.
        """
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.HoverEnter:
                # Activar glow en hover
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(20)
                shadow.setColor(QColor("#3498db"))
                shadow.setOffset(0, 0)
                obj.setGraphicsEffect(shadow)
                return True
            elif event.type() == QEvent.HoverLeave:
                # Quitar glow al salir
                obj.setGraphicsEffect(None)
                return True
        return super().eventFilter(obj, event)

    def _load_logo(self) -> QLabel:
        """
        Carga el logo de la UCE desde resources.
        
        Returns:
            QLabel con el pixmap del logo o texto fallback.
        """
        label = QLabel()
        pixmap = QPixmap("ui/resources/images/logo_uce.png")
        
        if pixmap.isNull():
            # Fallback: texto si no existe la imagen
            label.setText("UCE")
            label.setStyleSheet("font: bold 14px 'Segoe UI'; color: #2c3e50;")
        else:
            # Escalar a 48x48 manteniendo proporción
            label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        return label
    
    def set_theme(self, is_dark: bool):
        """Actualiza el tema del fondo."""
        CyberGridBackground.set_theme(self, is_dark)
        self.update()