"""
Vista de Acerca de - Información de la aplicación
"""
import tkinter as tk
from tkinter import ttk
from ui.views.login_view import limpiar_ventana
from utils.file_utils import resource_path
from PIL import Image, ImageTk


# ==============================================================================
# PALETA PREMIUM
# ==============================================================================
COLOR_FONDO_MAIN = "#FFFFFF"
COLOR_FONDO_SIDEBAR = "#F8F9FA"
COLOR_PRIMARY = "#0EA5E9"
COLOR_PRIMARY_DARK = "#0284C7"
COLOR_ACCENT = "#F97316"
COLOR_TEXTO = "#1E293B"
COLOR_TEXTO_SEC = "#64748B"
COLOR_BORDE = "#E2E8F0"


class AcercaDeView:
    """Vista de Acerca de - Información de la aplicación"""
    
    def __init__(self, ventana, on_volver):
        """Inicializa la vista deAcerca de"""
        self.ventana = ventana
        self.on_volver = on_volver
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def _configurar_estilos(self):
        """Configura estilos visuales Premium Flat & Clean"""
        style = ttk.Style(self.ventana)
        style.theme_use('clam')
        
        # Labels
        style.configure("TLabel",
            font=('Segoe UI', 10),
            foreground=COLOR_TEXTO,
            background=COLOR_FONDO_MAIN)
        
        style.configure("Titulo.TLabel",
            font=('Segoe UI', 18, 'bold'),
            foreground=COLOR_TEXTO,
            background=COLOR_FONDO_MAIN)
        
        style.configure("Subtitulo.TLabel",
            font=('Segoe UI', 14, 'bold'),
            foreground=COLOR_PRIMARY,
            background=COLOR_FONDO_MAIN)
        
        style.configure("Info.TLabel",
            font=('Segoe UI', 11),
            foreground=COLOR_TEXTO_SEC,
            background=COLOR_FONDO_MAIN)
        
        style.configure("Nombre.TLabel",
            font=('Segoe UI', 12, 'bold'),
            foreground=COLOR_TEXTO,
            background=COLOR_FONDO_MAIN)
    
    def crear_interfaz(self):
        """Crea toda la interfaz deAcerca de"""
        limpiar_ventana(self.ventana)
        
        # Configurar ventana
        self.ventana.title("Acerca de - Buscador de Documentos")
        self.ventana.state('zoomed')
        self.ventana.configure(bg=COLOR_FONDO_MAIN)
        
        # ==============================================================================
        # CONTENEDOR PRINCIPAL
        # ==============================================================================
        container = tk.Frame(self.ventana, bg=COLOR_FONDO_MAIN)
        container.pack(fill='both', expand=True)
        
        # ==============================================================================
        # SIDEBAR (280px fijo)
        # ==============================================================================
        sidebar = tk.Frame(container, bg=COLOR_FONDO_SIDEBAR, width=280)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # --- Logo ---
        logo_frame = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        logo_frame.pack(pady=30)
        
        try:
            ruta_imagen = resource_path("imagenes/logouce.png")
            imagen_logo = Image.open(ruta_imagen)
            imagen_logo = imagen_logo.resize((80, 80), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            logo_label = tk.Label(logo_frame, image=self.logo_img, bg=COLOR_FONDO_SIDEBAR)
            logo_label.pack()
        except Exception as e:
            print("No se pudo cargar el logo:", e)
        
        # --- Nombre de la app ---
        tk.Label(
            sidebar,
            text="Buscador de\nDocumentos",
            font=('Segoe UI', 14, 'bold'),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_SIDEBAR,
            justify='center'
        ).pack(pady=(10, 5))
        
        # --- Separator ---
        tk.Frame(sidebar, bg=COLOR_BORDE, height=1).pack(pady=20, padx=30, fill='x')
        
        # --- Botón volver ---
        btn_volver = tk.Button(
            sidebar,
            text="← Volver",
            font=('Segoe UI', 11, 'bold'),
            bg="#0369A1",
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.on_volver
        )
        btn_volver.pack(pady=20, padx=30, fill='x')
        
        # ==============================================================================
        # MAIN CONTENT (derecha)
        # ==============================================================================
        main = tk.Frame(container, bg=COLOR_FONDO_MAIN)
        main.pack(side='left', fill='both', expand=True, padx=60, pady=60)
        
        # --- Título principal ---
        tk.Label(
            main,
            text="Acerca de la Aplicación",
            font=('Segoe UI', 24, 'bold'),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=(20, 30))
        
        # --- Card de información ---
        card = tk.Frame(main, bg=COLOR_FONDO_MAIN, relief="solid", bd=1)
        card.pack(fill='x', pady=(0, 30))
        
        # --- Versión ---
        self._crear_info_row(card, "Versión", "1.0.0", 0)
        
        # --- Separator ---
        tk.Frame(card, bg=COLOR_BORDE, height=1).pack(pady=10, padx=30, fill='x')
        
        # --- Lenguaje ---
        self._crear_info_row(card, "Lenguaje de Programación", "Python 3.14", 2)
        
        # --- Separator ---
        tk.Frame(card, bg=COLOR_BORDE, height=1).pack(pady=10, padx=30, fill='x')
        
        # --- Framework ---
        self._crear_info_row(card, "Interfaz Gráfica", "Tkinter", 4)
        
        # --- Separator ---
        tk.Frame(card, bg=COLOR_BORDE, height=1).pack(pady=10, padx=30, fill='x')
        
        # --- Desarrolladores ---
        tk.Label(
            card,
            text="Desarrolladores",
            font=('Segoe UI', 11, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=(15, 5), padx=30, anchor='w')
        
        # Nombres de desarrolladores
        tk.Label(
            card,
            text="• Bryan Loya",
            font=('Segoe UI', 12),
            fg=COLOR_PRIMARY,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=2, padx=30, anchor='w')
        
        tk.Label(
            card,
            text="• Wulfer Quiguango",
            font=('Segoe UI', 12),
            fg=COLOR_PRIMARY,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=2, padx=30, anchor='w')
        
        # --- Separator ---
        tk.Frame(card, bg=COLOR_BORDE, height=1).pack(pady=15, padx=30, fill='x')
        
        # --- Carrera ---
        self._crear_info_row(card, "Carrera", "Ingeniería en Ciencias de la Computación", 9)
        
        # --- Separator ---
        tk.Frame(card, bg=COLOR_BORDE, height=1).pack(pady=10, padx=30, fill='x')
        
        # --- Universidad ---
        tk.Label(
            card,
            text="Universidad",
            font=('Segoe UI', 11, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=(10, 5), padx=30, anchor='w')
        
        tk.Label(
            card,
            text="Universidad Central del Ecuador",
            font=('Segoe UI', 12),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=2, padx=30, anchor='w')
        
        # --- Pie de página ---
        tk.Label(
            main,
            text="© 2024 - Todos los derechos reservados",
            font=('Segoe UI', 9),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=20)
    
    def _crear_info_row(self, parent, label, valor, row):
        """Crea una fila de información label: valor"""
        tk.Label(
            parent,
            text=label,
            font=('Segoe UI', 11, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=(5, 2), padx=30, anchor='w')
        
        tk.Label(
            parent,
            text=valor,
            font=('Segoe UI', 12),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN
        ).pack(pady=2, padx=30, anchor='w')
    
    def refrescar_vista(self):
        """Recrea la interfaz"""
        self.crear_interfaz()


def mostrar_acerca_de(ventana, on_volver):
    """Función helper para mostrar la vista deAcerca de"""
    AcercaDeView(ventana, on_volver)
