"""
Configuración de estilos y temas de la interfaz de usuario
"""
from tkinter import ttk


def configurar_estilos():
    """
    Configura todos los estilos ttk de la aplicación
    """
    style = ttk.Style()
    style.theme_use('clam')
    
    # Treeview moderno con mejor diseño
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#2c3e50",
                    rowheight=35,
                    fieldbackground="#ffffff",
                    font=('Segoe UI', 10),
                    borderwidth=0,
                    relief='flat')
    
    style.configure("Treeview.Heading",
                    background="#34495e",
                    foreground="white",
                    font=('Segoe UI', 11, 'bold'),
                    borderwidth=0,
                    relief='flat')
    
    style.map('Treeview.Heading',
              background=[('active', '#2c3e50')])
    
    style.map('Treeview', 
              background=[('selected', '#3498db')], 
              foreground=[('selected', 'white')])
    
    # Botones principales con diseño moderno
    style.configure('TButton', 
                    font=('Segoe UI', 11, 'bold'), 
                    padding=10,
                    relief='flat',
                    background='#3498db',
                    foreground='white',
                    borderwidth=0)
    
    style.map('TButton',
              background=[('active', '#2980b9'), ('pressed', '#1f6f9e')],
              foreground=[('active', 'white'), ('pressed', 'white')])
    
    # Combobox mejorado
    style.configure('TCombobox', 
                    font=('Segoe UI', 10),
                    fieldbackground='white',
                    background='white',
                    selectbackground='#3498db',
                    selectforeground='white',
                    borderwidth=1,
                    relief='solid')
    
    style.map('TCombobox',
              fieldbackground=[('readonly', 'white')],
              selectbackground=[('readonly', '#3498db')],
              selectforeground=[('readonly', 'white')])
    
    # Botón Cerrar Sesión moderno
    style.configure('CerrarSesion.TButton', 
                    font=('Segoe UI', 10, 'bold'), 
                    padding=10,
                    background='#e74c3c',
                    foreground='white',
                    relief='flat',
                    borderwidth=0)
    
    style.map('CerrarSesion.TButton',
              background=[('active', '#c0392b'), ('pressed', '#a93226')],
              foreground=[('active', 'white'), ('pressed', 'white')])
    
    # Botón Sincronizar moderno
    style.configure('Sincronizar.TButton', 
                    font=('Segoe UI', 10, 'bold'), 
                    padding=10,
                    background='#27ae60',
                    foreground='white',
                    relief='flat',
                    borderwidth=0)
    
    style.map('Sincronizar.TButton',
              background=[('active', '#229954'), ('pressed', '#1e8449')],
              foreground=[('active', 'white'), ('pressed', 'white')])
    
    # Botón de Login
    style.configure('Login.TButton', 
                    font=('Segoe UI', 13, 'bold'), 
                    padding=12,
                    background='#3498db',
                    foreground='white',
                    relief='flat',
                    borderwidth=0)
    
    style.map('Login.TButton',
              background=[('active', '#2980b9'), ('pressed', '#1f6f9e')])
