"""
StatusFooter - Barra de estado global.
Muestra información de sesión en estilo técnico.
"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from datetime import datetime


class StatusFooter(QFrame):
    """
    Barra de estado inferior que muestra:
    - Usuario actual
    - Hora en tiempo real
    - Fecha
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._start_clock()
    
    def _setup_ui(self):
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QFrame {
                background-color: #0a1929;
                border-top: 1px solid #1a3150;
            }
            QLabel {
                color: #3498db;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        # Usuario
        self._user_label = QLabel("Usuario: ---")
        self._user_label.setStyleSheet("color: #00ffff;")
        
        # Hora
        self._time_label = QLabel("00:00:00")
        
        # Fecha
        self._date_label = QLabel("--/--/----")
        
        # Separadores
        sep1 = QLabel(" | ")
        sep2 = QLabel(" | ")
        
        layout.addWidget(self._user_label)
        layout.addStretch()
        layout.addWidget(self._time_label)
        layout.addWidget(sep1)
        layout.addWidget(self._date_label)
        
        # Actualizar tiempo cada segundo
        self._update_time()
    
    def _start_clock(self):
        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(1000)
    
    def _update_time(self):
        now = datetime.now()
        self._time_label.setText(now.strftime("%H:%M:%S"))
        self._date_label.setText(now.strftime("%d/%m/%Y"))
    
    def set_usuario(self, nombre: str):
        self._user_label.setText(f"Usuario: {nombre}")