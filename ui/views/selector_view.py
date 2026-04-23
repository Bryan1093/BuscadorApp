"""
SelectorView - Vista de selección de módulos con signals para QStackedWidget.

Proporciona una página completa para elegir entre:
- Docentes (📚)
- Oficios (📄)

Emite signals:
- module_selected(str): cuando se selecciona un módulo ('docentes' o 'oficios')
- about_requested(): cuando se click en "Acerca de"
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt, QEvent, QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon

from ui.styles.render_engine import CyberGridBackground
from ui.styles.shadow_manager import ShadowManager


# Colores del theme Neumórfico
COLOR_BG = "#E8EDF2"
COLOR_CARD = "#E8EDF2"
COLOR_TEXT_PRIMARY = "#2c3e50"
COLOR_TEXT_SECONDARY = "#6c757d"
COLOR_ACCENT = "#2D4B5E"
COLOR_DOCENTES = "#3498db"
COLOR_OFICIOS = "#e74c3c"
COLOR_DOCENTES_HOVER = "#2980b9"
COLOR_OFICIOS_HOVER = "#c0392b"
COLOR_TIMESTAMP = "#95a5a6"


class SelectorView(CyberGridBackground):
    """
    Vista de selección de módulo para usar en QStackedWidget.
    
    Señales:
        module_selected(str): Emitida cuando se selecciona un módulo.
                              'docentes' o 'oficios'
        about_requested(): Emitida cuando se click en "Acerca de".
    """
    
    # Señales para el stack
    module_selected = Signal(str)  # 'docentes' o 'oficios'
    about_requested = Signal()      # cuando click en "Acerca de"
    
    def __init__(self, nombre_usuario: str, parent=None):
        """
        Inicializa la SelectorView.
        
        Args:
            nombre_usuario: Nombre del usuario a mostrar en el header.
            parent: Widget padre (opcional).
        """
        # Determinar tema actual
        is_dark = getattr(parent, '_current_theme', None) == 'dark' if parent else False
        super().__init__(parent, is_dark=is_dark)
        self._nombre = nombre_usuario or "Usuario"
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal - margins 0 para fondo completo
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Inicializar diccionarios para efectos y animaciones
        self._card_shadows = {}  # shadows de tarjetas para animaciones
        self._card_buttons = {}  # botones para glow
        self._glow_effects = {}  # efectos glow por botón
        
        # Aplicar estilos
        self._apply_styles()
        
        # ==== HEADER ====
        header = self._create_header()
        layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Spacer
        layout.addSpacing(30)
        
        # ==== BOTONES PRINCIPALES ====
        buttons = self._create_module_buttons()
        layout.addWidget(buttons, alignment=Qt.AlignCenter)
        
        # Spacer
        layout.addStretch()
        
        # ==== FOOTER ====
        footer = self._create_footer()
        layout.addWidget(footer, alignment=Qt.AlignCenter)
    
    def _apply_styles(self):
        """Aplica los estilos neumórficos."""
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }}
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 40px;
                font: bold 14px 'Segoe UI';
            }}
            QPushButton:pressed {
                opacity: 0.85;
            }}
        """)
    
    def _create_header(self) -> QWidget:
        """
        Crea el header con saludo y título de bienvenida.
        
        Returns:
            QWidget con el layout del header.
        """
        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo UCE + Saludo en fila horizontal
        header_top = QWidget()
        header_top.setAttribute(Qt.WA_TranslucentBackground)
        
        top_layout = QHBoxLayout(header_top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)
        
        # Logo UCE (esquina superior izquierda)
        logo_label = self._load_logo()
        top_layout.addWidget(logo_label, alignment=Qt.AlignLeft)
        
        # Contenedor para textos centrados
        text_container = QWidget()
        text_container.setAttribute(Qt.WA_TranslucentBackground)
        
        text_layout = QVBoxLayout(text_container)
        text_layout.setSpacing(10)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Saludo
        label_saludo = QLabel(f"¡Hola, {self._nombre}!")
        label_saludo.setFont(QFont("Segoe UI", 32, QFont.Bold))
        label_saludo.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        label_saludo.setAlignment(Qt.AlignCenter)
        
        # Subtítulo
        label_sub = QLabel("Selecciona el módulo que deseas consultar")
        label_sub.setFont(QFont("Segoe UI", 16))
        label_sub.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        label_sub.setAlignment(Qt.AlignCenter)
        
        text_layout.addWidget(label_saludo)
        text_layout.addWidget(label_sub)
        
        top_layout.addWidget(text_container, alignment=Qt.AlignCenter)
        
        layout.addWidget(header_top)
        
        return container
    
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
            label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        else:
            # Escalar a 40x40 manteniendo proporción
            label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        return label
    
    def _create_module_buttons(self) -> QWidget:
        """
        Crea los dos botones grandes (tarjetas) para Docentes y Oficios.
        
        Returns:
            QWidget con las tarjetas de módulos.
        """
        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(container)
        layout.setSpacing(40)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tarjeta Docentes
        card_docentes = self._create_module_card(
            emoji="📚",
            titulo="DOCENTES",
            descripcion="Consulta expedientes\nde doctorados y programas",
            color_boton=COLOR_DOCENTES,
            color_hover=COLOR_DOCENTES_HOVER,
            module_name="docentes"
        )
        
        # Tarjeta Oficios
        card_oficios = self._create_module_card(
            emoji="📄",
            titulo="OFICIOS",
            descripcion="Gestiona oficios\ny documentación oficial",
            color_boton=COLOR_OFICIOS,
            color_hover=COLOR_OFICIOS_HOVER,
            module_name="oficios"
        )
        
        layout.addWidget(card_docentes)
        layout.addWidget(card_oficios)
        
        return container
    
    def _create_module_card(self, emoji: str, titulo: str, descripcion: str,
                           color_boton: str, color_hover: str,
                           module_name: str) -> QFrame:
        """
        Crea una tarjeta individual de módulo con estilo neumórfico.
        
        Args:
            emoji: Emoji a mostrar.
            titulo: Título del módulo.
            descripcion: Descripción del módulo.
            color_boton: Color de fondo del botón.
            color_hover: Color al pasar el mouse.
            module_name: Nombre del módulo para la señal ('docentes' o 'oficios').
        
        Returns:
            QFrame con la tarjeta configurada.
        """
        card = QFrame()
        card.setFixedSize(280, 320)
        # Estilo base sin sombras (se aplican con Python)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 20px;
            }}
        """)
        
        # ==== APLICAR SOMBRA NEUMÓRFICA CON SHADOW MANAGER ====
        shadow_mgr = ShadowManager.get_instance()
        shadow = shadow_mgr.apply_card_shadow(card)
        # Guardar para animación
        self._card_shadows[module_name] = shadow
        self._animate_card_entry(shadow)
        
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 30, 20, 20)
        
        # Emoji
        label_emoji = QLabel(emoji)
        label_emoji.setFont(QFont("Segoe UI", 60))
        label_emoji.setAlignment(Qt.AlignCenter)
        label_emoji.setStyleSheet("background-color: transparent;")
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        label_titulo.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        label_titulo.setAlignment(Qt.AlignCenter)
        
        # Descripción
        label_desc = QLabel(descripcion)
        label_desc.setFont(QFont("Segoe UI", 12))
        label_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        label_desc.setAlignment(Qt.AlignCenter)
        
        # Botón con glow según el módulo
        btn = QPushButton("ACCEDER →")
        btn.setObjectName("moduleBtn" if module_name == "docentes" else "oficiosBtn")
        btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        
        if module_name == "docentes":
            btn.setStyleSheet(f"""
                QPushButton#moduleBtn {{
                    background-color: {color_boton};
                    color: white;
                    border-radius: 8px;
                    padding: 12px 40px;
                    font: bold 14px 'Segoe UI';
                    transition: all 0.3s;
                }}
                QPushButton#moduleBtn:hover {{
                    background-color: {color_hover};
                    box-shadow: 0 0 20px rgba(52, 152, 219, 0.6);
                }}
                QPushButton#moduleBtn:pressed {{
                    background-color: {color_hover};
                    box-shadow: 0 0 10px rgba(52, 152, 219, 0.4);
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton#oficiosBtn {{
                    background-color: {color_boton};
                    color: white;
                    border-radius: 8px;
                    padding: 12px 40px;
                    font: bold 14px 'Segoe UI';
                    transition: all 0.3s;
                }}
                QPushButton#oficiosBtn:hover {{
                    background-color: {color_hover};
                    box-shadow: 0 0 20px rgba(231, 76, 60, 0.6);
                }}
                QPushButton#oficiosBtn:pressed {{
                    background-color: {color_hover};
                    box-shadow: 0 0 10px rgba(231, 76, 60, 0.4);
                }}
            """)
        
        # Conectar según el módulo
        if module_name == "docentes":
            btn.clicked.connect(self._on_docentes_clicked)
        else:
            btn.clicked.connect(self._on_oficios_clicked)

        # Aplicar efecto glow al botón
        self._apply_glow_to_button(btn, color_boton)
        self._card_buttons[module_name] = btn

        # Instalar event filter en la tarjeta para hover
        card.installEventFilter(self)

        # ==== LÍNEA DE ACENTO BAJO TÍTULO ====
        accent_line = self._create_accent_line()
        
        # Aplicar efecto neón a la línea de acento
        shadow_mgr.apply_neon_line(accent_line)

        layout.addWidget(label_emoji)
        layout.addWidget(label_titulo)
        layout.addWidget(label_desc)
        layout.addWidget(accent_line)
        layout.addStretch()
        layout.addWidget(btn)
        
        return card
    
    def _create_footer(self) -> QWidget:
        """
        Crea el footer con timestamp y botón Acerca de.
        
        Returns:
            QWidget con el layout del footer.
        """
        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Timestamp
        hora = datetime.now().strftime("%H:%M")
        fecha = datetime.now().strftime("%d de %B, %Y")
        
        label_time = QLabel(f"🕐 {hora} • {fecha}")
        label_time.setFont(QFont("Segoe UI", 11))
        label_time.setStyleSheet(f"color: {COLOR_TIMESTAMP};")
        label_time.setAlignment(Qt.AlignCenter)
        
        # Botón Acerca de
        btn_acerca = QPushButton("ℹ️ Acerca de")
        btn_acerca.setFont(QFont("Segoe UI", 10))
        btn_acerca.setCursor(Qt.PointingHandCursor)
        btn_acerca.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font: 10px 'Segoe UI';
            }}
            QPushButton:hover {{
                color: {COLOR_ACCENT};
                background-color: rgba(45, 75, 94, 0.1);
            }}
        """)
        btn_acerca.clicked.connect(self._on_about_clicked)
        
        layout.addWidget(label_time)
        layout.addWidget(btn_acerca)
        
        return container

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

    # ==================== HANDLERS ====================
    
    def _on_docentes_clicked(self):
        """Emite la señal para seleccionar el módulo Docentes."""
        self.module_selected.emit('docentes')
    
    def _on_oficios_clicked(self):
        """Emite la señal para seleccionar el módulo Oficios."""
        self.module_selected.emit('oficios')
    
    def _on_about_clicked(self):
        """Emite la señal para mostrar Acerca de."""
        self.about_requested.emit()

    # ==================== EFECTOS GLOW ====================

    def _animate_card_entry(self, shadow):
        """
        Animación de entrada para las tarjetas (200ms).
        
        Args:
            shadow: QGraphicsDropShadowEffect a animar.
        """
        # Animación suave del blurRadius
        anim = QPropertyAnimation(shadow, b"blurRadius")
        anim.setDuration(200)
        anim.setStartValue(5)
        anim.setEndValue(20)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def _add_glow_effect(self, button, color="#3498db"):
        """
        Agrega efecto glow a un botón.

        Args:
            button: QPushButton al que se le aplicará el efecto.
            color: Color del glow (por defecto cian).
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 0)
        button.setGraphicsEffect(shadow)

    def _apply_glow_to_button(self, button, color="#3498db"):
        """
        Aplica glow a un botón en hover.

        Args:
            button: QPushButton al que se le aplicará el efecto.
            color: Color del glow (por defecto cian).
        """
        button.installEventFilter(self)
        self._add_glow_effect(button, color)

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
                self._add_glow_effect(obj)
                return True
            elif event.type() == QEvent.HoverLeave:
                # Quitar glow al salir
                obj.setGraphicsEffect(None)
                return True
        return super().eventFilter(obj, event)

    # ==================== MÉTODOS PÚBLICOS ====================
    
    def actualizar_saludo(self, nombre: str):
        """
        Actualiza el nombre de usuario mostrado en el saludo.
        
        Args:
            nombre: Nuevo nombre a mostrar.
        """
        self._nombre = nombre
        # Buscar y actualizar el label de saludo
        self._update_saludo_label()
    
    def _update_saludo_label(self):
        """Actualiza el label de saludo interno."""
        # Rebuild el header con el nuevo nombre
        self._rebuild_header()
    
    def _rebuild_header(self):
        """Rebuild el header con el nombre actual."""
        # Buscar el layout principal
        layout = self.layout()
        if layout is None:
            return
        
        # Buscar el widget de header en el layout (índice 0)
        if layout.count() > 0:
            header = layout.itemAt(0).widget()
            if header is not None:
                # Eliminar header viej
                layout.removeWidget(header)
                header.deleteLater()
        
        # Crear nuevo header
        new_header = self._create_header()
        layout.insertWidget(0, new_header)
    
    def set_theme(self, is_dark: bool):
        """Actualiza el tema del fondo."""
        CyberGridBackground.set_theme(self, is_dark)
        self.update()
    
    def update(self):
        """Actualiza la vista completa (para refresh del UI)."""
        self._rebuild_header()