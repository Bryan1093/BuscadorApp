"""
Componente de encabezado de la aplicación
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.file_utils import resource_path
from services.file_service import sincronizar_drive
import config.settings as settings


def crear_encabezado(ventana, titulo="Buscador de Doctorados", on_cerrar_sesion=None):
    """
    Crea el encabezado de la aplicación con logo, título y botones
    Args:
        ventana: Ventana o frame padre
        titulo: Título a mostrar en el encabezado
        on_cerrar_sesion: Callback para cerrar sesión
    Returns:
        Frame: Frame del encabezado
    """
    frame = tk.Frame(ventana, bg="#ecf0f1", relief='flat', bd=0)
    frame.pack(pady=0, fill="x")

    # Frame izquierdo con logo y botón sincronizar
    frame_izquierdo = tk.Frame(frame, bg="#ecf0f1")
    frame_izquierdo.pack(side="left", padx=20)

    # Logo
    try:
        ruta_imagen = resource_path("imagenes/logouce.png")
        imagen_logo = Image.open(ruta_imagen)
        imagen_logo = imagen_logo.resize((120, 120), Image.LANCZOS)
        ventana.logo_img = ImageTk.PhotoImage(imagen_logo)
        etiqueta_logo = tk.Label(frame_izquierdo, image=ventana.logo_img, bg="#ecf0f1")
        etiqueta_logo.pack(side="left", padx=(0, 15))
    except Exception as e:
        print("No se pudo cargar el logo:", e)

    # Botón sincronizar
    def sincronizar():
        documentos = sincronizar_drive(settings.ruta_doctorados, settings.ruta_doctorados2)
        settings.documentos_drive = documentos
    
    btn_sincronizar = ttk.Button(frame_izquierdo, text="⟳ Sincronizar", 
                                 command=sincronizar, style='Sincronizar.TButton')
    btn_sincronizar.pack(side="left", padx=(0, 15), pady=15)

    # Frame centro con título
    frame_centro = tk.Frame(frame, bg="#ecf0f1")
    frame_centro.pack(side="left", expand=True)
    tk.Label(frame_centro, text=titulo, font=("Segoe UI", 26, "bold"), 
            bg="#ecf0f1", fg="#2c3e50").pack(expand=True)

    # Frame derecho con botón cerrar sesión
    if on_cerrar_sesion:
        frame_derecho = tk.Frame(frame, bg="#ecf0f1")
        frame_derecho.pack(side="right", padx=20)
        btn_cerrar_sesion = ttk.Button(frame_derecho, text="✕ Cerrar Sesión", 
                                       command=on_cerrar_sesion, style='CerrarSesion.TButton')
        btn_cerrar_sesion.pack(pady=15)

    return frame


def crear_resumen(ventana, texto_inicial="Mostrando 0 documentos."):
    """
    Crea la etiqueta de resumen de resultados
    Args:
        ventana: Ventana o frame padre
        texto_inicial: Texto inicial a mostrar
    Returns:
        Label: Etiqueta de resumen
    """
    frame = tk.Frame(ventana, bg="#ecf0f1")
    frame.pack(fill="x", padx=30, pady=(10, 5))
    
    etiqueta = tk.Label(frame, text=texto_inicial, 
                       font=("Segoe UI", 11, 'bold'), 
                       bg="#ecf0f1", fg="#34495e")
    etiqueta.pack(side="right", anchor="e", padx=10)
    
    return etiqueta
