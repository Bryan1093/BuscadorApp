"""
Vista de carga - Pantalla intermedia
"""
import tkinter as tk
from datetime import datetime


def mostrar_carga_y_abrir_main(ventana, nombre_usuario, on_complete):
    """
    Muestra pantalla de carga moderna
    Args:
        ventana: Ventana principal
        nombre_usuario: Nombre del usuario
        on_complete: Callback al completar
    """
    from ui.views.login_view import limpiar_ventana
    limpiar_ventana(ventana)
    
    ventana.title("Cargando Sistema...")
    ventana.state('zoomed')
    ventana.configure(bg="#f5f7fa")

    main_frame = tk.Frame(ventana, bg="#f5f7fa")
    main_frame.pack(fill='both', expand=True)

    content = tk.Frame(main_frame, bg="#f5f7fa")
    content.place(relx=0.5, rely=0.5, anchor='center')

    # Tarjeta de carga
    card = tk.Frame(content, bg="#ffffff", relief="flat", bd=0,
                   highlightthickness=2, highlightbackground="#e9ecef")
    card.pack(padx=60, pady=40, ipadx=80, ipady=60)

    # Icono
    tk.Label(card, text="⏳", font=("Segoe UI", 70), 
            bg="#ffffff", fg="#3498db").pack(pady=(30, 20))

    # Título
    tk.Label(card, text="CARGANDO SISTEMA", font=("Segoe UI Bold", 32),
            bg="#ffffff", fg="#2c3e50").pack(pady=(0, 15))
    
    tk.Label(card, text="Sistema de Gestión de Expedientes", 
            font=("Segoe UI", 16), bg="#ffffff", fg="#7f8c8d").pack(pady=(0, 10))

    # Separador
    tk.Frame(card, height=2, bg="#e9ecef", bd=0).pack(fill='x', padx=60, pady=30)

    # Info del usuario
    info_card = tk.Frame(card, bg="#f8f9fa", relief="flat", bd=0)
    info_card.pack(fill='x', padx=40, pady=(0, 30))

    user_frame = tk.Frame(info_card, bg="#f8f9fa")
    user_frame.pack(pady=15)
    tk.Label(user_frame, text="👤", font=("Segoe UI", 20), bg="#f8f9fa").pack(side='left', padx=(20, 10))
    tk.Label(user_frame, text=f"{nombre_usuario}", font=("Segoe UI Bold", 16),
            bg="#f8f9fa", fg="#2c3e50").pack(side='left')

    hora = datetime.now().strftime("%H:%M:%S")
    fecha = datetime.now().strftime("%d de %B, %Y")
    
    time_frame = tk.Frame(info_card, bg="#f8f9fa")
    time_frame.pack(pady=(0, 15))
    tk.Label(time_frame, text="🕐", font=("Segoe UI", 20), bg="#f8f9fa").pack(side='left', padx=(20, 10))
    tk.Label(time_frame, text=f"{hora} • {fecha}", font=("Segoe UI", 14),
            bg="#f8f9fa", fg="#6c757d").pack(side='left')

    # Barra de progreso
    progress_container = tk.Frame(card, bg="#ffffff")
    progress_container.pack(pady=(10, 20))

    progress_bg = tk.Canvas(progress_container, width=500, height=8,
                           bg="#e9ecef", highlightthickness=0)
    progress_bg.pack(pady=(0, 15))

    progress_bar = progress_bg.create_rectangle(0, 0, 0, 8, fill="#3498db", outline="")

    status_label = tk.Label(progress_container, text="Inicializando módulos...",
                           font=("Segoe UI", 12), bg="#ffffff", fg="#95a5a6")
    status_label.pack()

    # Animación
    def animar_barra(width=0):
        if width <= 500:
            progress_bg.coords(progress_bar, 0, 0, width, 8)
            
            if width < 150:
                status_label.config(text="Inicializando módulos...")
            elif width < 300:
                status_label.config(text="Cargando configuración...")
            elif width < 450:
                status_label.config(text="Preparando interfaz...")
            else:
                status_label.config(text="¡Casi listo!")
            
            ventana.after(15, lambda: animar_barra(width + 5))
    
    animar_barra()

    def finalizar():
        on_complete(ventana, nombre_usuario)

    ventana.after(3000, finalizar)
