"""
Componentes para mostrar detalles de documentos
"""
import tkinter as tk
import fitz  # PyMuPDF
import threading


def crear_texto_detalles(ventana, titulo="📄 Detalles del archivo seleccionado:"):
    """
    Crea el panel de detalles de documentos
    Args:
        ventana: Ventana o frame padre
        titulo: Título del panel de detalles
    Returns:
        Text: Widget de texto para detalles
    """
    frame_detalles = tk.Frame(ventana, bg="#ecf0f1")
    frame_detalles.pack(padx=30, pady=(10, 20), fill='x')
    
    tk.Label(frame_detalles, text=titulo, 
            font=("Segoe UI", 11, 'bold'), bg="#ecf0f1", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
    
    texto_detalles = tk.Text(frame_detalles, height=4, font=("Segoe UI", 10), 
                            relief="solid", bd=1, bg="white", fg="#2c3e50")
    texto_detalles.pack(fill='x')
    texto_detalles.config(state="disabled")
    
    return texto_detalles


def mostrar_detalles_documento(texto_widget, ruta):
    """
    Muestra los detalles de un documento PDF usando threading
    Args:
        texto_widget: Widget de texto donde mostrar los detalles
        ruta: Ruta del archivo PDF
    """
    # Mostrar mensaje de carga inmediatamente
    texto_widget.config(state='normal')
    texto_widget.delete('1.0', tk.END)
    texto_widget.insert(tk.END, "Cargando detalles...")
    texto_widget.config(state='disabled')
    
    def cargar_detalles():
        """Función que se ejecuta en thread de fondo"""
        try:
            doc = fitz.open(ruta)
            num_paginas = doc.page_count
            metadata = doc.metadata
            doc.close()
            
            info = (
                f"Ruta: {ruta}\n"
                f"Páginas: {num_paginas}\n"
                f"Título: {metadata.get('title', 'N/A')}\n"
                f"Herramienta Usada: {metadata.get('author', 'N/A')}\n"
            )
            
            # Actualizar UI en el thread principal
            texto_widget.after(0, lambda: actualizar_detalles(info))
        except Exception as e:
            error_msg = f"No se pudo cargar detalles:\n{e}"
            texto_widget.after(0, lambda: actualizar_detalles(error_msg))
    
    def actualizar_detalles(info):
        """Actualiza el widget con la información cargada"""
        texto_widget.config(state='normal')
        texto_widget.delete('1.0', tk.END)
        texto_widget.insert(tk.END, info)
        texto_widget.config(state='disabled')
    
    # Ejecutar carga en thread de fondo
    thread = threading.Thread(target=cargar_detalles, daemon=True)
    thread.start()


def mostrar_detalles_oficio(texto_widget, doc_info):
    """
    Muestra los detalles de un oficio
    Args:
        texto_widget: Widget de texto donde mostrar los detalles
        doc_info: Diccionario con información del oficio
    """
    info = (
        f"Año: {doc_info['anio']}\n"
        f"Tipo: {doc_info['tipo']}\n"
        f"Nombre: {doc_info['nombre'].title()}\n"
        f"Ruta: {doc_info['ruta']}\n"
    )
    
    texto_widget.config(state='normal')
    texto_widget.delete('1.0', tk.END)
    texto_widget.insert(tk.END, info)
    texto_widget.config(state='disabled')


def limpiar_detalles(texto_widget):
    """
    Limpia el contenido del panel de detalles
    Args:
        texto_widget: Widget de texto a limpiar
    """
    texto_widget.config(state='normal')
    texto_widget.delete('1.0', tk.END)
    texto_widget.config(state='disabled')
