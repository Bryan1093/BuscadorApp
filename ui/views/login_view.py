"""
Vista de inicio de sesión - Modularizada
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.file_utils import resource_path
from services.auth_service import verificar_credenciales
import config.settings as settings


def limpiar_ventana(ventana):
    """Limpia todos los widgets de una ventana"""
    for widget in ventana.winfo_children():
        widget.destroy()


def mostrar_login(ventana, on_login_success):
    """
    Muestra la pantalla de inicio de sesión
    Args:
        ventana: Ventana principal
        on_login_success: Callback al iniciar sesión exitosamente
    """
    limpiar_ventana(ventana)
    ventana.title("Unidad Administrativa de Gestión de Doctorados - Login")
    ventana.state('zoomed')
    ventana.configure(bg="#f5f7fa")

    # Contenedor principal
    main_frame = tk.Frame(ventana, bg="#f5f7fa")
    main_frame.pack(fill='both', expand=True)

    # Panel izquierdo con información institucional
    left_panel = tk.Frame(main_frame, bg="#1a1a2e", width=400)
    left_panel.pack(side='left', fill='y', padx=(0, 20))
    left_panel.pack_propagate(False)

    # Logo
    try:
        ruta_imagen = resource_path("imagenes/logouce.png")
        imagen_logo = Image.open(ruta_imagen)
        imagen_logo = imagen_logo.resize((120, 120), Image.LANCZOS)
        ventana.logo_img = ImageTk.PhotoImage(imagen_logo)
        tk.Label(left_panel, image=ventana.logo_img, bg="#1a1a2e").pack(pady=50)
    except Exception as e:
        print("No se pudo cargar el logo:", e)

    # Información institucional
    info_frame = tk.Frame(left_panel, bg="#1a1a2e")
    info_frame.pack(expand=True)

    for texto, color in [("UNIVERSIDAD", "#3498db"), ("CENTRAL", "#ffffff"), ("DEL ECUADOR", "#3498db")]:
        tk.Label(info_frame, text=texto, font=("Segoe UI Bold", 24), 
                bg="#1a1a2e", fg=color).pack(pady=5)

    # Panel derecho con formulario
    right_panel = tk.Frame(main_frame, bg="#ffffff")
    right_panel.pack(side='right', fill='both', expand=True, padx=(0, 20))

    form_frame = tk.Frame(right_panel, bg="#ffffff")
    form_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Título
    tk.Label(form_frame, text="BIENVENIDO", font=("Segoe UI Bold", 36),
            bg="#ffffff", fg="#2c3e50").pack(pady=(0, 10))
    tk.Label(form_frame, text="Unidad de Gestión de Doctorados", 
            font=("Segoe UI", 18), bg="#ffffff", fg="#7f8c8d").pack(pady=(0, 40))

    # Campo de usuario
    tk.Label(form_frame, text="USUARIO", font=("Segoe UI Bold", 12),
            bg="#ffffff", fg="#34495e").pack(anchor='w', pady=(0, 5))
    
    user_container = tk.Frame(form_frame, bg="#f8f9fa", relief="flat", bd=0)
    user_container.pack(fill='x', pady=(0, 15))
    
    tk.Label(user_container, text="👤", font=("Segoe UI", 14), 
            bg="#f8f9fa", fg="#3498db").pack(side='left', padx=(10, 5), pady=5)
    
    entrada_usuario = tk.Entry(user_container, font=("Segoe UI", 14), relief="flat",
                              bd=0, bg="#f8f9fa", fg="#2c3e50", 
                              insertbackground="#2c3e50", highlightthickness=0)
    entrada_usuario.pack(side='left', fill='x', expand=True, padx=(5, 10), pady=5)
    entrada_usuario.insert(0, "Usuario")

    # Campo de contraseña
    tk.Label(form_frame, text="CONTRASEÑA", font=("Segoe UI Bold", 12),
            bg="#ffffff", fg="#34495e").pack(anchor='w', pady=(0, 5))
    
    pass_container = tk.Frame(form_frame, bg="#f8f9fa", relief="flat", bd=0)
    pass_container.pack(fill='x', pady=(0, 15))
    
    tk.Label(pass_container, text="🔒", font=("Segoe UI", 14),
            bg="#f8f9fa", fg="#e74c3c").pack(side='left', padx=(10, 5), pady=5)
    
    entrada_contra = tk.Entry(pass_container, font=("Segoe UI", 14), show="•",
                             relief="flat", bd=0, bg="#f8f9fa", fg="#2c3e50",
                             insertbackground="#2c3e50", highlightthickness=0)
    entrada_contra.pack(side='left', fill='x', expand=True, padx=(5, 5), pady=5)
    entrada_contra.insert(0, "Contraseña")

    # Botón mostrar/ocultar contraseña
    mostrar_contra = tk.BooleanVar(value=False)
    
    def toggle_contra():
        if mostrar_contra.get():
            entrada_contra.config(show="•")
            boton_ojo.config(text="👁", fg="#6c757d")
            mostrar_contra.set(False)
        else:
            entrada_contra.config(show="")
            boton_ojo.config(text="🔒", fg="#3498db")
            mostrar_contra.set(True)

    boton_ojo = tk.Button(pass_container, text="👁", command=toggle_contra,
                         relief="flat", bg="#f8f9fa", bd=0, font=("Segoe UI", 14),
                         cursor="hand2", activebackground="#f8f9fa", 
                         fg="#6c757d", padx=5)
    boton_ojo.pack(side='right', padx=(0, 10), pady=5)

    # Separador
    tk.Frame(form_frame, height=2, bg="#e9ecef", bd=0).pack(fill='x', pady=30)

    # Función de login
    def intentar_login():
        usuario = entrada_usuario.get().strip()
        contrasena = entrada_contra.get().strip()
        
        if usuario == "Usuario" or contrasena == "Contraseña" or not usuario or not contrasena:
            messagebox.showwarning("Campos requeridos", 
                                 "Debes ingresar usuario y contraseña.")
            return
        
        valido, nombre_real = verificar_credenciales(usuario, contrasena)
        if valido:
            settings.nombre_usuario_actual = nombre_real
            # Importar aquí para evitar dependencias circulares
            from ui.views.loading_view import mostrar_carga_y_abrir_main
            mostrar_carga_y_abrir_main(ventana, nombre_real, on_login_success)
        else:
            messagebox.showerror("Error de autenticación", 
                               "Usuario o contraseña incorrectos.")

    # Botón de ingreso
    btn_ingresar = tk.Button(form_frame, text="INGRESAR →", command=intentar_login,
                            font=("Segoe UI Bold", 16), bg="#3498db", fg="white",
                            relief="flat", bd=0, padx=60, pady=15, cursor="hand2",
                            activebackground="#2980b9", activeforeground="white")
    btn_ingresar.pack(pady=20)

    # Efectos hover
    btn_ingresar.bind("<Enter>", lambda e: btn_ingresar.config(bg="#2980b9"))
    btn_ingresar.bind("<Leave>", lambda e: btn_ingresar.config(bg="#3498db"))

    # Footer
    footer = tk.Frame(form_frame, bg="#ffffff")
    footer.pack(pady=(40, 0))
    tk.Label(footer, text="Sistema de Gestión de Expedientes", 
            font=("Segoe UI", 12), bg="#ffffff", fg="#6c757d").pack()
    tk.Label(footer, text="© Universidad Central del Ecuador - 2025",
            font=("Segoe UI", 10), bg="#ffffff", fg="#adb5bd").pack(pady=(5, 0))

    # Placeholders
    def on_user_focus_in(e):
        if entrada_usuario.get() == "Usuario":
            entrada_usuario.delete(0, "end")
            entrada_usuario.config(fg="#2c3e50")

    def on_user_focus_out(e):
        if entrada_usuario.get() == "":
            entrada_usuario.insert(0, "Usuario")
            entrada_usuario.config(fg="#6c757d")

    def on_pass_focus_in(e):
        if entrada_contra.get() == "Contraseña":
            entrada_contra.delete(0, "end")
            entrada_contra.config(fg="#2c3e50", show="•")

    def on_pass_focus_out(e):
        if entrada_contra.get() == "":
            entrada_contra.insert(0, "Contraseña")
            entrada_contra.config(fg="#6c757d", show="")

    entrada_usuario.bind("<FocusIn>", on_user_focus_in)
    entrada_usuario.bind("<FocusOut>", on_user_focus_out)
    entrada_contra.bind("<FocusIn>", on_pass_focus_in)
    entrada_contra.bind("<FocusOut>", on_pass_focus_out)

    ventana.bind('<Return>', lambda e: intentar_login())
    entrada_usuario.focus()


def cerrar_sesion(ventana, on_logout):
    """Cierra la sesión del usuario"""
    if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar sesión?"):
        settings.nombre_usuario_actual = ""
        on_logout(ventana)