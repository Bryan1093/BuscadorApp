"""
SplashView - Pantalla de carga simple para el stack de navegación.

Muestra una pantalla de carga mientras se cargan los documentos desde Drive.
Se integra con DriveController via señales.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


class SplashView(QWidget):
    """
    Pantalla de carga - se muestra mientras se cargan los documentos.
    
    Señales:
        load_complete: Emitido cuando termina de cargar exitosamente.
        load_failed: Emitido si hay error durante la carga (str: mensaje de error).
    """
    
    # Señales para通知 UI externa
    load_complete = Signal()    # Carga completada exitosamente
    load_failed = Signal(str)   # Error durante carga (mensaje)
    
    def __init__(self, parent=None):
        """
        Inicializa el SplashView.
        
        Args:
            parent: Widget padre (opcional).
        """
        super().__init__(parent)
        self._controller = None
        self._documentos_cargados = 0
        self._timer_animacion = None
        self._timer_progreso = 0
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Estilo base
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignCenter)
        
        # Logo/título con branding (icono de reloj de arena)
        titulo = QLabel("⏳ Buscador de Documentos")
        titulo_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: #2D4B5E;
                background-color: transparent;
                padding: 16px;
            }
        """)
        layout.addWidget(titulo, alignment=Qt.AlignCenter)
        
        # Progress bar (rango 0-100)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setFixedHeight(24)
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #e9ecef;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: #2D4B5E;
                font: bold 12px Segoe UI;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._progress, alignment=Qt.AlignCenter)
        
        # Status label
        self._status = QLabel("Inicializando...")
        self._status.setFont(QFont("Segoe UI", 12))
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet("""
            QLabel {
                color: #6c757d;
                background-color: transparent;
            }
        """)
        layout.addWidget(self._status, alignment=Qt.AlignCenter)
        
        # Agregar stretch para centrar contenido
        layout.addStretch()
    
    # ==========================================================================
    # MÉTODOS PÚBLICOS
    # ==========================================================================
    
    def start_loading(self):
        """
        Inicia la carga de documentos a través del controller.
        Conecta las señales del controller y comienza carga asíncrona.
        Además inicia animación fallback con QTimer por si el controller no responde.
        """
        # Importar aquí para evitar dependencias circulares
        from core import DriveController
        
        # Obtener instancia singleton del controller
        self._controller = DriveController.get_instance()
        
        # Conectar señales del controller a nuestros handlers
        self._controller.signals.load_started.connect(self._on_started)
        self._controller.signals.load_progress.connect(self._on_progress)
        self._controller.signals.load_completed.connect(self._on_completed)
        self._controller.signals.load_error.connect(self._on_error)
        
        # === INICIAR ANIMACIÓN FALLBACK CON QTIMER ===
        # Si el controller no responde en 5 segundos, simulamos progreso
        self._timer_progreso = 0
        self._timer_animacion = QTimer(self)
        self._timer_animacion.timeout.connect(self._animar_progreso_fallback)
        self._timer_animacion.start(200)  # Actualizar cada 200ms
        
        # Timeout para detener animación fallback después de 5 segundos
        self._timeout_fallback = QTimer(self)
        self._timeout_fallback.setSingleShot(True)
        self._timeout_fallback.timeout.connect(self._on_timeout_fallback)
        self._timeout_fallback.start(5000)  # 5 segundos máximo
        
        # Inicializar rutas y comenzar carga
        self._controller.initialize_routes()
        self._controller.load_documents()
    
    def _animar_progreso_fallback(self):
        """Anima el progreso simulado mientras el controller carga."""
        if self._timer_progreso < 85:  # Máximo 85% mientras esperamos
            self._timer_progreso += 2
            self._progress.setValue(self._timer_progreso)
            # Mensaje dinámico
            mensajes = [
                "Conectando...",
                "Cargando documentos...",
                "Procesando archivos...",
                "Casi listo...",
            ]
            idx = min(len(mensajes) - 1, self._timer_progreso // 20)
            self._status.setText(mensajes[idx])
    
    def _on_timeout_fallback(self):
        """Handler cuando expira el timeout de animación fallback."""
        # El controller debería haber respondido, pero si no, continuamos
        if self._timer_progreso < 100:
            self._timer_progreso = 85
            self._progress.setValue(85)
            self._status.setText("Esperando respuesta...")
    
    def reset(self):
        """Resetea el estado inicial del splash."""
        # Detener timers de animación si existen
        self._detener_animacion_fallback()
        
        self._progress.setValue(0)
        self._status.setText("Inicializando...")
        self._documentos_cargados = 0
        self._timer_progreso = 0
    
    # ==========================================================================
    # HANDLERS DE SEÑALES DEL CONTROLLER
    # ==========================================================================
    
    def _on_started(self):
        """Handler cuando inicia la carga."""
        # Detener animación fallback
        self._detener_animacion_fallback()
        
        self._progress.setValue(10)
        self._status.setText("Conectando con Drive...")
    
    def _on_progress(self, ruta: str, count: int):
        """
        Handler durante la carga de documentos.
        
        Args:
            ruta: Carpeta actual siendo procesada.
            count: Cantidad de documentos encontrados hasta ahora.
        """
        # Detener animación fallback si está activa
        self._detener_animacion_fallback()
        
        self._documentos_cargados = count
        # Calcular progreso: 10% inicio + hasta 80% durante carga
        # Asumimos un máximo estimado de 500 documentos
        max_docs = 500
        progress = min(90, int((count / max_docs) * 80) + 10)
        self._progress.setValue(progress)
        self._status.setText(f"Cargando: {count} documentos")
    
    def _on_completed(self, documentos: list):
        """
        Handler cuando termina la carga exitosamente.
        
        Args:
            documentos: Lista de documentos cargados.
        """
        # Detener animación fallback si está activa
        self._detener_animacion_fallback()
        
        self._documentos_cargados = len(documentos)
        self._progress.setValue(100)
        self._status.setText(f"✓ {len(documentos)} documentos cargados")
        # Emitir señal de éxito
        self.load_complete.emit()
    
    def _on_error(self, msg: str):
        """
        Handler cuando hay error en la carga.
        
        Args:
            msg: Mensaje de error.
        """
        # Detener animación fallback si está activa
        self._detener_animacion_fallback()
        
        self._progress.setValue(0)
        self._status.setText(f"Error: {msg}")
        # Emitir señal de error
        self.load_failed.emit(msg)
    
    def _detener_animacion_fallback(self):
        """Detiene los timers de animación fallback."""
        if self._timer_animacion:
            self._timer_animacion.stop()
            self._timer_animacion.deleteLater()
            self._timer_animacion = None
        if hasattr(self, '_timeout_fallback') and self._timeout_fallback:
            self._timeout_fallback.stop()
            self._timeout_fallback.deleteLater()
            self._timeout_fallback = None