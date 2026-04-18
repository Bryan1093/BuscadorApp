"""
Componente de diálogo de carga con barra de progreso
"""
import tkinter as tk
from tkinter import ttk


class LoadingDialog:
    """Diálogo modal de carga con barra de progreso"""
    
    def __init__(self, parent, title="Cargando..."):
        """
        Inicializa el diálogo de carga
        Args:
            parent: Ventana padre
            title: Título del diálogo
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar ventana
        self.dialog.resizable(False, False)
        
        # Centrar en la ventana padre
        self._center_on_parent(parent)
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Prevenir cierre manual
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def _center_on_parent(self, parent):
        """Centra el diálogo en la ventana padre"""
        # Actualizar para obtener dimensiones correctas
        self.dialog.update_idletasks()
        
        # Obtener dimensiones
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Dimensiones más grandes para mejor visibilidad
        dialog_width = 500
        dialog_height = 180
        
        # Calcular posición centrada
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        # Frame principal con padding
        main_frame = tk.Frame(self.dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Cargando documentos...",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 15))
        
        # Barra de progreso indeterminada (animada) - más ancha
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=440  # Aumentado de 340 a 440
        )
        self.progress.pack(pady=(0, 15))
        self.progress.start(10)  # Velocidad de animación
        
        # Label de estado con wraplength para evitar cortes
        self.status_label = tk.Label(
            main_frame,
            text="Iniciando escaneo...",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            wraplength=420,  # Permitir que el texto se ajuste
            justify='center'
        )
        self.status_label.pack(pady=(0, 5))
        
        # Label de contador de documentos
        self.count_label = tk.Label(
            main_frame,
            text="0 documentos encontrados",
            font=('Segoe UI', 9),
            bg='white',
            fg='#95a5a6'
        )
        self.count_label.pack()
    
    def update_status(self, status_text, count=None):
        """
        Actualiza el texto de estado y opcionalmente el contador
        Args:
            status_text: Texto de estado a mostrar
            count: Número de documentos encontrados (opcional)
        """
        self.status_label.config(text=status_text)
        if count is not None:
            self.count_label.config(
                text=f"{count} documento{'s' if count != 1 else ''} encontrado{'s' if count != 1 else ''}"
            )
        self.dialog.update()
    
    def close(self):
        """Cierra el diálogo"""
        self.progress.stop()
        self.dialog.grab_release()
        self.dialog.destroy()


def mostrar_loading(parent, title="Cargando..."):
    """
    Función helper para crear un diálogo de carga
    Args:
        parent: Ventana padre
        title: Título del diálogo
    Returns:
        LoadingDialog: Instancia del diálogo de carga
    """
    return LoadingDialog(parent, title)
