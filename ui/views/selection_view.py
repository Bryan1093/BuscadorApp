"""
Vista de selección de módulos
"""
import tkinter as tk
from datetime import datetime


def mostrar_seleccion(ventana, nombre_usuario, on_docentes, on_oficios, on_acerca_de):
    """
    Muestra pantalla de selección de módulo
    Args:
        ventana: Ventana principal
        nombre_usuario: Nombre del usuario
        on_docentes: Callback para módulo de docentes
        on_oficios: Callback para módulo de oficios
        on_acerca_de: Callback para ver información de la app
    """
    from ui.views.login_view import limpiar_ventana
    limpiar_ventana(ventana)
    
    ventana.title("Seleccione una opción")
    ventana.state('zoomed')
    ventana.configure(bg="#f5f7fa")

    main_frame = tk.Frame(ventana, bg="#f5f7fa")
    main_frame.pack(fill='both', expand=True)

    content = tk.Frame(main_frame, bg="#f5f7fa")
    content.place(relx=0.5, rely=0.5, anchor='center')

    # Header
    header = tk.Frame(content, bg="#f5f7fa")
    header.pack(pady=(0, 50))

    tk.Label(header, text=f"¡Hola, {nombre_usuario}!", font=("Segoe UI", 32, "bold"),
            bg="#f5f7fa", fg="#2c3e50").pack(pady=(0, 10))
    
    tk.Label(header, text="Selecciona el módulo que deseas consultar",
            font=("Segoe UI", 16), bg="#f5f7fa", fg="#6c757d").pack()

    # Tarjetas
    cards = tk.Frame(content, bg="#f5f7fa")
    cards.pack(pady=20)

    # Tarjeta Docentes
    card_doc = tk.Frame(cards, bg="#ffffff", relief="flat", bd=0,
                       highlightthickness=2, highlightbackground="#e9ecef")
    card_doc.pack(side='left', padx=20, ipadx=40, ipady=30)

    tk.Label(card_doc, text="📚", font=("Segoe UI", 60), bg="#ffffff").pack(pady=(20, 15))
    tk.Label(card_doc, text="DOCENTES", font=("Segoe UI Bold", 22),
            bg="#ffffff", fg="#2c3e50").pack(pady=(0, 10))
    tk.Label(card_doc, text="Consulta expedientes\nde doctorados y programas",
            font=("Segoe UI", 12), bg="#ffffff", fg="#6c757d", 
            justify='center').pack(pady=(0, 25))
    
    btn_doc = tk.Button(card_doc, text="ACCEDER →", command=on_docentes,
                       font=("Segoe UI Bold", 14), bg="#3498db", fg="white",
                       relief="flat", bd=0, padx=40, pady=12, cursor="hand2",
                       activebackground="#2980b9", activeforeground="white")
    btn_doc.pack(pady=(0, 20))

    # Tarjeta Oficios
    card_of = tk.Frame(cards, bg="#ffffff", relief="flat", bd=0,
                      highlightthickness=2, highlightbackground="#e9ecef")
    card_of.pack(side='left', padx=20, ipadx=40, ipady=30)

    tk.Label(card_of, text="📄", font=("Segoe UI", 60), bg="#ffffff").pack(pady=(20, 15))
    tk.Label(card_of, text="OFICIOS", font=("Segoe UI Bold", 22),
            bg="#ffffff", fg="#2c3e50").pack(pady=(0, 10))
    tk.Label(card_of, text="Gestiona oficios\ny documentación oficial",
            font=("Segoe UI", 12), bg="#ffffff", fg="#6c757d",
            justify='center').pack(pady=(0, 25))
    
    btn_of = tk.Button(card_of, text="ACCEDER →", command=on_oficios,
                      font=("Segoe UI Bold", 14), bg="#e74c3c", fg="white",
                      relief="flat", bd=0, padx=40, pady=12, cursor="hand2",
                      activebackground="#c0392b", activeforeground="white")
    btn_of.pack(pady=(0, 20))

    # Efectos hover
    def on_enter_doc(e):
        card_doc.config(highlightbackground="#3498db", highlightthickness=3)
        btn_doc.config(bg="#2980b9")
    
    def on_leave_doc(e):
        card_doc.config(highlightbackground="#e9ecef", highlightthickness=2)
        btn_doc.config(bg="#3498db")

    def on_enter_of(e):
        card_of.config(highlightbackground="#e74c3c", highlightthickness=3)
        btn_of.config(bg="#c0392b")
    
    def on_leave_of(e):
        card_of.config(highlightbackground="#e9ecef", highlightthickness=2)
        btn_of.config(bg="#e74c3c")

    card_doc.bind("<Enter>", on_enter_doc)
    card_doc.bind("<Leave>", on_leave_doc)
    for w in card_doc.winfo_children():
        w.bind("<Enter>", on_enter_doc)
        w.bind("<Leave>", on_leave_doc)

    card_of.bind("<Enter>", on_enter_of)
    card_of.bind("<Leave>", on_leave_of)
    for w in card_of.winfo_children():
        w.bind("<Enter>", on_enter_of)
        w.bind("<Leave>", on_leave_of)

    # Footer
    footer = tk.Frame(content, bg="#f5f7fa")
    footer.pack(pady=(50, 0))

    hora = datetime.now().strftime("%H:%M")
    fecha = datetime.now().strftime("%d de %B, %Y")
    
    tk.Label(footer, text=f"🕐 {hora} • {fecha}", font=("Segoe UI", 11),
            bg="#f5f7fa", fg="#95a5a6").pack()
    
    # Botón Acerca de
    btn_acerca = tk.Button(
        footer,
        text="ℹ️ Acerca de",
        command=on_acerca_de,
        font=("Segoe UI", 10),
        bg="#f5f7fa",
        fg="#6c757d",
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=15,
        pady=8
    )
    btn_acerca.pack(pady=(15, 0))
    
    # Efecto hover
    def on_enter_acerca(e):
        btn_acerca.config(fg="#0EA5E9")
    
    def on_leave_acerca(e):
        btn_acerca.config(fg="#6c757d")
    
    btn_acerca.bind("<Enter>", on_enter_acerca)
    btn_acerca.bind("<Leave>", on_leave_acerca)
