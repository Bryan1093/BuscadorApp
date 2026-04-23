"""
LoginWidget - Versión widget para QStackedWidget
Versión de LoginView adaptada para usar en stack de ventanas
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from services.auth_service import verificar_credenciales
import config.settings as settings


class LoginWidget(QWidget):
    """
    Widget de login con diseño Flat moderno para usar en QStackedWidget.
    
    Señales:
        login_success(str): Emite el nombre de usuario cuando el login es exitoso
        login_failed(str): Emite el mensaje de error cuando el login falla
    """
    
    login_success = Signal(str)  # Emite el nombre de usuario
    login_failed = Signal(str)  # Emite mensaje de error
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(900, 600)
        self._username = ""
        self._password = ""
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel izquierdo - Información institucional
        left_panel = QFrame(self)
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 50, 30, 50)
        
        # Logo (placeholder visual)
        self.logo_label = QLabel(left_panel)
        self.logo_label.setObjectName("logoPlaceholder")
        self.logo_label.setText("UCE")
        self.logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.logo_label)
        left_layout.addStretch()
        
        # Información institucional
        for texto, es_bold in [("UNIVERSIDAD", True), ("CENTRAL", False), ("DEL ECUADOR", False)]:
            label = QLabel(texto, left_panel)
            label.setObjectName("institutionText")
            if es_bold:
                label.setObjectName("institutionTextBold")
            label.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(label)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Panel derecho - Formulario
        right_panel = QFrame(self)
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 80, 60, 80)
        right_layout.setSpacing(0)
        
        # Espaciador superior
        right_layout.addSpacing(40)
        
        # Título
        title_label = QLabel("BIENVENIDO", right_panel)
        title_label.setObjectName("titleText")
        right_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Unidad de Gestión de Doctorados", right_panel)
        subtitle_label.setObjectName("subtitleText")
        right_layout.addWidget(subtitle_label)
        
        right_layout.addSpacing(40)
        
        # Campo de usuario
        user_label = QLabel("USUARIO", right_panel)
        user_label.setObjectName("fieldLabel")
        right_layout.addWidget(user_label)
        
        self.user_input = QLineEdit(right_panel)
        self.user_input.setObjectName("inputField")
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.textChanged.connect(self._on_user_changed)
        right_layout.addWidget(self.user_input)
        
        right_layout.addSpacing(20)
        
        # Campo de contraseña
        pass_label = QLabel("CONTRASEÑA", right_panel)
        pass_label.setObjectName("fieldLabel")
        right_layout.addWidget(pass_label)
        
        self.password_input = QLineEdit(right_panel)
        self.password_input.setObjectName("inputField")
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self._on_password_changed)
        right_layout.addWidget(self.password_input)
        
        right_layout.addSpacing(30)
        
        # Botón mostrar/ocultar contraseña
        self.toggle_password_btn = QPushButton("Mostrar", right_panel)
        self.toggle_password_btn.setObjectName("togglePasswordBtn")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)
        right_layout.addWidget(self.toggle_password_btn)
        
        right_layout.addSpacing(30)
        
        # Botón de ingreso
        self.login_btn = QPushButton("INGRESAR", right_panel)
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.clicked.connect(self._attempt_login)
        right_layout.addWidget(self.login_btn)
        
        #Etiqueta para errores
        self.error_label = QLabel("", right_panel)
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        right_layout.addWidget(self.error_label)
        
        right_layout.addStretch()
        
        # Footer
        footer_label = QLabel("Sistema de Gestión de Expedientes", right_panel)
        footer_label.setObjectName("footerText")
        right_layout.addWidget(footer_label)
        
        copyright_label = QLabel("© Universidad Central del Ecuador - 2025", right_panel)
        copyright_label.setObjectName("copyrightText")
        right_layout.addWidget(copyright_label)
        
        main_layout.addWidget(right_panel)
        
        # Configurar tab order
        self.setTabOrder(self.user_input, self.password_input)
        self.setTabOrder(self.password_input, self.toggle_password_btn)
        self.setTabOrder(self.toggle_password_btn, self.login_btn)
        
        # Focus inicial
        self.user_input.setFocus()
        
        # Enter key para login
        self.password_input.returnPressed.connect(self._attempt_login)
    
    def _apply_styles(self):
        """Aplica los estilos Flat modernos"""
        self.setStyleSheet("""
            /* Colores principales */
            #2D4B5E Accent: #2D4B5E
            /* Fondo general */
            QWidget {
                background-color: #ffffff;
            }
            
            /* Panel izquierdo */
            #leftPanel {
                background-color: #1a1a2e;
            }
            
            #logoPlaceholder {
                font-family: 'Segoe UI';
                font-size: 48px;
                font-weight: bold;
                color: #2D4B5E;
                padding: 20px;
            }
            
            #institutionText {
                font-family: 'Segoe UI';
                font-size: 24px;
                color: #3498db;
            }
            
            #institutionTextBold {
                font-family: 'Segoe UI';
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
            }
            
            /* Panel derecho */
            #rightPanel {
                background-color: #ffffff;
            }
            
            #titleText {
                font-family: 'Segoe UI';
                font-size: 36px;
                font-weight: bold;
                color: #2c3e50;
            }
            
            #subtitleText {
                font-family: 'Segoe UI';
                font-size: 18px;
                color: #7f8c8d;
            }
            
            #fieldLabel {
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                color: #34495e;
            }
            
            /* Inputs estilo Flat */
            #inputField {
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #2c3e50;
                background-color: #f8f9fa;
                border: none;
                border-radius: 4px;
                padding: 12px 15px;
            }
            
            #inputField:focus {
                background-color: #ffffff;
                border: 2px solid #2D4B5E;
            }
            
            #inputField::placeholder {
                color: #6c757d;
            }
            
            /* Botón toggle password */
            #togglePasswordBtn {
                font-family: 'Segoe UI';
                font-size: 12px;
                background-color: transparent;
                border: none;
                color: #6c757d;
                text-align: left;
                padding: 5px 0px;
            }
            
            #togglePasswordBtn:hover {
                color: #2D4B5E;
            }
            
            #togglePasswordBtn:checked {
                color: #2D4B5E;
            }
            
            /* Botón principal */
            #loginBtn {
                font-family: 'Segoe UI';
                font-size: 16px;
                font-weight: bold;
                background-color: #2D4B5E;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 15px 60px;
            }
            
            #loginBtn:hover {
                background-color: #3d5f70;
            }
            
            #loginBtn:pressed {
                background-color: #1d3b4a;
            }
            
            /* Error label */
            #errorLabel {
                font-family: 'Segoe UI';
                font-size: 12px;
                color: #e74c3c;
                padding: 5px 0px;
            }
            
            /* Footer */
            #footerText {
                font-family: 'Segoe UI';
                font-size: 12px;
                color: #6c757d;
            }
            
            #copyrightText {
                font-family: 'Segoe UI';
                font-size: 10px;
                color: #adb5bd;
            }
        """)
    
    def _on_user_changed(self, text):
        """Captura el cambio en el campo de usuario"""
        self._username = text
        self.error_label.clear()  # Limpiar errores al escribir
    
    def _on_password_changed(self, text):
        """Captura el cambio en el campo de contraseña"""
        self._password = text
        self.error_label.clear()  # Limpiar errores al escribir
    
    def _toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña"""
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("Ocultar")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("Mostrar")
    
    def _attempt_login(self):
        """Intenta iniciar sesión"""
        usuario = self.user_input.text().strip()
        contrasena = self.password_input.text().strip()
        
        if not usuario or not contrasena:
            self.login_failed.emit("Debes ingresar usuario y contraseña")
            return
        
        valido, nombre_real = verificar_credenciales(usuario, contrasena)
        if valido:
            settings.nombre_usuario_actual = nombre_real
            self.login_success.emit(nombre_real)
        else:
            self.login_failed.emit("Usuario o contraseña incorrectos")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_error(self, message):
        """
        Muestra un mensaje de error en la etiqueta de_error.
        Llama esto desde main_window cuando recibe login_failed.
        """
        self.error_label.setText(message)
    
    def clear_error(self):
        """Limpia el mensaje de error"""
        self.error_label.clear()
    
    def get_username(self):
        """Retorna el nombre de usuario"""
        return self._username
    
    def reset(self):
        """Resetea el widget al estado inicial"""
        self.user_input.clear()
        self.password_input.clear()
        self.error_label.clear()
        self._username = ""
        self._password = ""
        self.user_input.setFocus()