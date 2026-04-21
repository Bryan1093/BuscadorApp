"""
Vista principal del módulo de Docentes - Refactorizada con UI moderna
"""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
from PIL import Image, ImageTk

# ==============================================================================
# PALETA PREMIUM FLAT & CLEAN
# ==============================================================================
COLOR_FONDO_MAIN = "#FFFFFF"        # Blanco puro
COLOR_FONDO_SIDEBAR = "#F8F9FA"     # Gris muy claro para sidebar
COLOR_PRIMARY = "#0EA5E9"          # Azul vibrante moderno
COLOR_PRIMARY_DARK = "#0284C7"     # Hover
COLOR_ACCENT = "#F97316"           # Naranja para sincronizar
COLOR_TEXTO = "#1E293B"            # Gris muy oscuro
COLOR_TEXTO_SEC = "#64748B"        # Gris medio para labels
COLOR_BORDE = "#E2E8F0"            # Borde sutil
COLOR_ZEBRA_EVEN = "#FFFFFF"
COLOR_ZEBRA_ODD = "#F1F5F9"        # Azul muy suave
COLOR_SELECCION = "#0EA5E9"

from services.search_service import buscar_documentos
from services.file_service import (abrir_pdf, descargar_expediente, descargar_expediente_multiple,
                                   cargar_documentos)
from utils.path_utils import encontrar_rutas_drive
from utils.file_utils import resource_path
from ui.views.login_view import limpiar_ventana
import config.settings as settings


# ==============================================================================
# FUNCIONES AUXILIARES DE ESTILOS (para compatibilidad hacia atrás)
# ==============================================================================

def aplicar_estilos_profesionales(root):
    """
    Aplica estilos profesionales ttktheme con tema clam
    DEPRECATED: Usar DocentesView._configurar_estilos() en su lugar
    """
    style = ttk.Style(root)
    style.theme_use('clam')

    # Treeview
    style.configure("Treeview",
                  rowheight=35,
                  font=('Segoe UI', 10),
                  borderwidth=0,
                  thickness=0)
    style.map("Treeview", background=[('selected', '#0078D7')], foreground=[('selected', 'white')])

    # Heading
    style.configure("Treeview.Heading",
                     font=('Segoe UI', 10, 'bold'),
                     background="#F0F0F0",
                     relief="flat")

    # Botones
    style.configure("TButton", font=('Segoe UI', 10), padding=5)
    style.configure("Action.TButton", background="#0078D7", foreground="white")


# ==============================================================================
# CLASE PRINCIPAL
# ==============================================================================

class DocentesView:
    """Vista del módulo de Docentes - Diseño moderno con Sidebar"""

    def __init__(self, ventana, on_volver, on_cerrar_sesion):
        """
        Inicializa la vista de docentes
        Args:
            ventana: Ventana principal
            on_volver: Callback para volver a selección
            on_cerrar_sesion: Callback para cerrar sesión
        """
        # ======================
        # ESTILOS - Forzar siempre (Bug fix persistencia)
        # ======================
        style = ttk.Style(ventana)
        style.theme_use('clam')

        # Header - Azul permanente sin hover
        style.configure("Treeview.Heading",
            background="#2D4B5E",    # Azul oscuro permanente
            foreground="#FFFFFF",      # Blanco puro
            relief="flat",
            font=('Segoe UI', 10, 'bold'))

        # Forzar mismo color en todos los estados (eliminar hover)
        style.map("Treeview.Heading",
            background=[('!active', '#2D4B5E'),
                         ('active', '#2D4B5E'),
                         ('pressed', '#2D4B5E'),
                         ('!pressed', '#2D4B5E')],
            foreground=[('!active', '#FFFFFF'),
                        ('active', '#FFFFFF'),
                        ('pressed', '#FFFFFF'),
                        ('!pressed', '#FFFFFF')])

        # Tabla principal
        style.configure("Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            fieldbackground="#FFFFFF",
            rowheight=45,
            font=('Segoe UI', 10),
            borderwidth=0,
            relief="flat")

        # Selection
        style.map("Treeview",
            background=[('selected', '#0EA5E9')],
            foreground=[('selected', 'white')])

        # Zebra Stripes
        style.configure("Treeview",
            rowheight=45,
            font=('Segoe UI', 10))

        # ======================
        # Continuar con __init__ normal
        # ======================
        self.ventana = ventana
        self.on_volver = on_volver
        self.on_cerrar_sesion = on_cerrar_sesion

        # Widgets que necesitamos referenciar
        self.resultados = None
        self.combo_universidad = None
        self.combo_programa = None
        self.combo_estudiante = None
        self.combo_item_clave = None
        self.entrada_busqueda = None

        # State
        self.selecciones = {}  # {iid: True/False}
        self.after_id = None
        self._seleccionar_todos = False  # Estado del toggle seleccionar todos

        # Fuente para iconos de checkbox - intentar Segoe UI Symbol, sino fallback
        self.font_checkbox = None
        try:
            self.font_checkbox = tkfont.Font(family='Segoe UI Symbol', size=16)
        except Exception as e:
            print(f"[WARN] No se pudo cargar font_checkbox: {e}")
            # Fallback a fuente por defecto - no usar fuente personalizada

        # Variable para búsqueda reactiva
        self.search_text = tk.StringVar()

        # Configurar estilos modernos
        self._configurar_estilos()

        # Crear interfaz
        self.crear_interfaz()

    def _configurar_estilos(self):
        """Configura estilos visuales Premium Flat & Clean"""
        style = ttk.Style(self.ventana)
        style.theme_use('clam')

        # ======================
        # Treeview (La Tabla Premium)
        # ======================
        style.configure("Treeview",
            background=COLOR_FONDO_MAIN,
            foreground=COLOR_TEXTO,
            fieldbackground=COLOR_FONDO_MAIN,
            rowheight=45,  # Estándar profesional
            font=('Segoe UI', 10),
            borderwidth=0,
            relief="flat")

        # La cabecera se configuró en el __init__ con azul oscuro, 
        # así que aquí solo actualizamos lo estrictamente necesario sin pisar los colores
        # o preservamos el azul oscuro.
        style.configure("Treeview.Heading",
            font=('Segoe UI', 10, 'bold'),
            background="#2D4B5E",
            foreground="#FFFFFF",
            relief="flat",
            borderwidth=0)

        # Zebra Stripes refined
        style.map("Treeview",
            background=[('selected', COLOR_SELECCION)],
            foreground=[('selected', 'white')])

        # ==============================================================================
        # Header Diferenciado para columna de selección
        # ==============================================================================
        style.configure("Treeview.Selection",
            background="#2D4B5E",
            foreground="#FFFFFF",
            relief="flat",
            font=('Segoe UI', 10, 'bold'))

        style.map("Treeview.Selection",
            background=[('active', '#3D647A')],
            foreground=[('active', '#FFFFFF')])

        # Estilo para heading de checkbox con cursor de mano
        style.configure("Treeview.CheckboxHeading",
            background="#2D4B5E",
            foreground="#FFFFFF",
            relief="flat",
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2')

        style.map("Treeview.CheckboxHeading",
            background=[('!active', '#2D4B5E'),
                         ('active', '#3D647A'),
                         ('pressed', '#2D4B5E')])

        # ======================
        # Botones Outline (Acción)
        # ======================
        style.configure("Outline.TButton",
            font=('Segoe UI', 10),
            padding=(15, 8),
            relief="flat",
            background="transparent",
            foreground=COLOR_PRIMARY,
            borderwidth=2,
            bordercolor=COLOR_PRIMARY)

        style.map("Outline.TButton",
            background=[('active', COLOR_PRIMARY)],
            foreground=[('active', 'white')])

        # ======================
        # Botón Sincronizar (Accent - Naranja)
        # ======================
        style.configure("Accent.TButton",
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 10),
            relief="flat",
            background=COLOR_ACCENT,
            foreground="white")

        style.map("Accent.TButton",
            background=[('active', '#EA580C')])

        # ======================
        # Botón Primary
        # ======================
        style.configure("Primary.TButton",
            font=('Segoe UI', 10),
            padding=(20, 10),
            relief="flat",
            background=COLOR_PRIMARY,
            foreground="white")

        style.map("Primary.TButton",
            background=[('active', COLOR_PRIMARY_DARK)])

        # ======================
        # Combobox
        # ======================
        style.configure("TCombobox",
            font=('Segoe UI', 10),
            padding=(10, 5),
            relief="flat")

        style.configure("TCombobox.Field",
            background=COLOR_FONDO_MAIN,
            borderwidth=1,
            lightcolor=COLOR_BORDE,
            darkcolor=COLOR_BORDE)

        # ======================
        # Labels
        # ======================
        style.configure("TLabel",
            font=('Segoe UI', 10),
            foreground=COLOR_TEXTO,
            background=COLOR_FONDO_MAIN)

        style.configure("Label.Titulo",
            font=('Segoe UI', 14, 'bold'),
            foreground=COLOR_TEXTO)

        style.configure("Label.Filtro",
            font=('Segoe UI', 9, 'bold'),
            foreground=COLOR_TEXTO_SEC,
            background=COLOR_FONDO_SIDEBAR)

    def crear_interfaz(self):
        """Crea toda la interfaz de la vista de docentes"""
        limpiar_ventana(self.ventana)

        # Configurar ventana
        self.ventana.title("Buscador de Doctorados - Docentes")
        self.ventana.state('zoomed')
        self.ventana.configure(bg=COLOR_FONDO_MAIN)

        # ==============================================================================
        # CONTENEDOR PRINCIPAL CON GRID
        # ==============================================================================
        container = tk.Frame(self.ventana, bg=COLOR_FONDO_MAIN)
        container.pack(fill='both', expand=True)

        # ==============================================================================
        # SIDEBAR (280px fijo) - Fondo Gris Claro
        # ==============================================================================
        sidebar = tk.Frame(container, bg=COLOR_FONDO_SIDEBAR, width=280)
        sidebar.pack(side='left', fill='y', padx=0, pady=0)
        sidebar.pack_propagate(False)  # Mantener ancho fijo

        # --- Logo en Sidebar ---
        logo_frame = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        logo_frame.pack(pady=15)

        try:
            ruta_imagen = resource_path("imagenes/logouce.png")
            imagen_logo = Image.open(ruta_imagen)
            imagen_logo = imagen_logo.resize((60, 60), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            logo_label = tk.Label(logo_frame, image=self.logo_img, bg=COLOR_FONDO_SIDEBAR)
            logo_label.pack()
        except Exception as e:
            print("No se pudo cargar el logo:", e)

        # --- Botón Sincronizar - Naranja vibrante ---
        btn_sincro = tk.Button(
            sidebar,
            text="🔄 Sincronizar Documentos",
            font=('Segoe UI', 11, 'bold'),
            bg="#F59E0B",  # Naranja vibrante
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self._cargar_documentos
        )
        btn_sincro.pack(pady=10, padx=20, fill='x')

        # --- Separator ---
        tk.Frame(sidebar, bg=COLOR_BORDE, height=1).pack(pady=10, padx=20, fill='x')

        # --- Filtros en Sidebar ---
        filtros_label = tk.Label(
            sidebar,
            text="FILTROS",
            font=('Segoe UI', 11, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        )
        filtros_label.pack(pady=(10, 5), padx=20, anchor='w')

        # Universidad
        frame_filtro_u = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_u.pack(fill='x', pady=8)

        tk.Label(
            frame_filtro_u,
            text="UNIVERSIDAD",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_universidad = ttk.Combobox(frame_filtro_u, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_universidad.pack(fill='x', padx=20)

        # Programa
        frame_filtro_p = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_p.pack(fill='x', pady=8)

        tk.Label(
            frame_filtro_p,
            text="PROGRAMA",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_programa = ttk.Combobox(frame_filtro_p, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_programa.pack(fill='x', padx=20)

        # Estudiante
        frame_filtro_e = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_e.pack(fill='x', pady=8)

        tk.Label(
            frame_filtro_e,
            text="ESTUDIANTE",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_estudiante = ttk.Combobox(frame_filtro_e, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_estudiante.pack(fill='x', padx=20)

        # Item Clave
        frame_filtro_item = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_item.pack(fill='x', pady=8)

        tk.Label(
            frame_filtro_item,
            text="ÍTEM CLAVE",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_item_clave = ttk.Combobox(frame_filtro_item, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_item_clave.pack(fill='x', padx=20)

        # --- Información de usuario ---
        tk.Frame(sidebar, bg=COLOR_BORDE, height=1).pack(pady=10, padx=20, fill='x')

        user_info = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        user_info.pack(pady=10, padx=20, fill='x')

        tk.Label(
            user_info,
            text=f"Usuario: {settings.nombre_usuario_actual}",
            font=('Segoe UI', 10),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w')

        # --- Botones al fondo del sidebar ---
        frame_botones_fondo = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_botones_fondo.pack(side='bottom', fill='x', pady=10)

        btn_volver = tk.Button(
            frame_botones_fondo,
            text="← Volver",
            font=('Segoe UI', 10, 'bold'),
            bg="#0369A1",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.on_volver
        )
        btn_volver.pack(side='left', padx=5, pady=5)

        btn_cerrar = tk.Button(
            frame_botones_fondo,
            text="Cerrar sesión",
            font=('Segoe UI', 10, 'bold'),
            bg="#DC2626",  # Rojo para cerrar sesión
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.on_cerrar_sesion
        )
        btn_cerrar.pack(side='right', padx=5, pady=5)

        # ==============================================================================
        # MAIN CONTENT (derecha, expande) - Fondo Blanco con Padding 30px
        # ==============================================================================
        # Main content con espaciado global de 40px
        main = tk.Frame(container, bg=COLOR_FONDO_MAIN)
        main.pack(side='left', fill='both', expand=True, padx=40, pady=40)

        # --- Toolbar con frame contenedor de altura fija ---
        toolbar = tk.Frame(main, bg=COLOR_FONDO_MAIN, height=50)
        toolbar.pack(fill='x', pady=(0, 15))
        toolbar.pack_propagate(False)  # Mantener altura

        tk.Label(
            toolbar,
            text="BUSCADOR DE DOCTORADOS",
            font=('Segoe UI', 16, 'bold'),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN
        ).pack(side='left')

        # Toolbar simplificada - Solo botón Descargar
        # Botón Descargar - Cuadrado pequeño con icono
        btn_descargar = tk.Button(
            toolbar,
            text="💾",  # Símbolo de guardar/descargar
            font=('Segoe UI', 14),
            bg="#0369A1",  # Azul oscuro
            fg="white",
            relief="flat",
            bd=0,
            width=4,
            height=1,
            cursor="hand2",
            command=self.descargar_seleccionados
        )
        btn_descargar.pack(side='right')

        # --- Buscador Moderno con Borde ---
        # Frame contenedor con borde (usando un frame subyacente)
        buscador_frame_outer = tk.Frame(main, bg=COLOR_BORDE, padx=1, pady=1, relief="flat", bd=0)
        buscador_frame_outer.pack(fill='x', pady=(0, 20))  # Espaciado buscador-tabla 20px

        # Entry sin bordes internos
        self.entrada_busqueda = tk.Entry(
            buscador_frame_outer,
            font=('Segoe UI', 11),
            relief="flat",
            bd=0,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN,
            insertbackground=COLOR_PRIMARY
        )
        self.entrada_busqueda.pack(fill='x', padx=10, pady=10)

        # Placeholder text" mediante un widget canvas o StringVar"
        self.entrada_busqueda.insert(0, "🔍 Buscar documentos...")
        self.entrada_busqueda.config(fg=COLOR_TEXTO_SEC)

        def on_focus_in(event):
            if self.entrada_busqueda.get() == "🔍 Buscar documentos...":
                self.entrada_busqueda.delete(0, tk.END)
                self.entrada_busqueda.config(fg=COLOR_TEXTO)

        def on_focus_out(event):
            if self.entrada_busqueda.get() == "":
                self.entrada_busqueda.insert(0, "🔍 Buscar documentos...")
                self.entrada_busqueda.config(fg=COLOR_TEXTO_SEC)

        self.entrada_busqueda.bind("<FocusIn>", on_focus_in)
        self.entrada_busqueda.bind("<FocusOut>", on_focus_out)

        # Sincronizar texto con StringVar para debounce (KeyRelease ya hace la búsqueda)
        self.entrada_busqueda.bind("<KeyRelease>", self._sync_search_text)

        # Configurar búsqueda reactiva con trace (para cambios vía código)
        self.search_text.trace_add('write', self.on_search_change)

        # --- Treeview de Resultados ---
        resultados_frame = tk.Frame(main, bg=COLOR_FONDO_MAIN)
        resultados_frame.pack(fill='both', expand=True)

        columnas = ("Seleccion", "Universidad", "Programa", "Estudiante", "Nombre")

        # Scrollbar moderna - ESTILO SEGURO
        try:
            scrollbar = ttk.Scrollbar(resultados_frame, orient="vertical", style="Vertical.TScrollbar")
        except:
            scrollbar = ttk.Scrollbar(resultados_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Treeview
        self.resultados = ttk.Treeview(resultados_frame, columns=columnas, show="headings",
                                     yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.resultados.yview)
        self.resultados.pack(fill="both", expand=True)

        # Configurar columnas - distribución proporcional (25/20/25/30)
        # Checkbox: ancho fijo de 50px
        self.resultados.heading("Seleccion", text="☑", command=self.toggle_seleccionar_todos)
        self.resultados.column("Seleccion", anchor="center", width=50, minwidth=50, stretch=False)

        # Universidad: 25% - stretch=True para proporcionalidad
        self.resultados.heading("Universidad", text="Universidad")
        self.resultados.column("Universidad", anchor="w", width=200, minwidth=150, stretch=True)

        # Programa: 20% - stretch=True para proporcionalidad
        self.resultados.heading("Programa", text="Programa")
        self.resultados.column("Programa", anchor="w", width=160, minwidth=120, stretch=True)

        # Estudiante: 25% - stretch=True para proporcionalidad
        self.resultados.heading("Estudiante", text="Estudiante")
        self.resultados.column("Estudiante", anchor="w", width=200, minwidth=150, stretch=True)

        # Nombre: 30% - stretch=True para proporcionalidad (header vacío)
        self.resultados.heading("Nombre", text="")
        self.resultados.column("Nombre", anchor="w", width=240, minwidth=180, stretch=True)

        # Columna vacía extra para que el header cubra hasta el scrollbar
        self.resultados.column("#0", anchor="w", width=0, minwidth=0, stretch=True)
        self.resultados.heading("#0", text="")

        # Zebra stripes con los nuevos colores
        self.resultados.tag_configure('odd', background=COLOR_ZEBRA_ODD)
        self.resultados.tag_configure('even', background=COLOR_ZEBRA_EVEN)

        # Zebra Stripes - Forzar siempre (Bug fix persistencia)
        self.resultados.tag_configure('odd', background='#F1F5F9')
        self.resultados.tag_configure('even', background='#FFFFFF')
        self.resultados.tag_configure('selected', background='#0EA5E9', foreground='white')

        # ==============================================================================
        # Checkbox Tags con fuente grande
        # ==============================================================================
        self.resultados.tag_configure('checkbox', font=self.font_checkbox)
        self.resultados.tag_configure('header_check', font=self.font_checkbox)

        # ==============================================================================
        # INTERACTIVIDAD - Checkboxes Funcionales
        # ==============================================================================
        # Configurar columna de selección (centrada y fija)
        self.resultados.column("Seleccion", width=50, anchor='center', minwidth=50, stretch=False)

        # Binding para clic en checkbox
        self.resultados.bind('<Button-1>', self.on_tree_click)

        # --- Status Bar ---
        status_bar_frame = tk.Frame(main, bg=COLOR_FONDO_SIDEBAR, relief="sunken", bd=0, height=30)
        status_bar_frame.pack(fill='x', pady=(10, 0))
        status_bar_frame.pack_propagate(False)

        self.status_bar = tk.Label(
            status_bar_frame,
            text="Listo",
            anchor="w",
            font=('Segoe UI', 9),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        )
        self.status_bar.pack(fill='x', padx=10, pady=0)

        # ==============================================================================
        # EVENTOS Y BINDINGS
        # ==============================================================================
        # Seleccionar resultado
        self.resultados.bind("<<TreeviewSelect>>", self.on_select_result)
        # Doble click para abrir
        self.resultados.bind("<Double-1>", self.on_double_click)

        # Atajos de teclado
        self.ventana.bind('<Control-f>', lambda e: self.entrada_busqueda.focus_set())
        self.ventana.bind('<Return>', lambda e: self.abrir_pdf_handler())
        self.ventana.bind('<Delete>', lambda e: self.limpiar_filtros())

        #Bindings para actualizar combos dependientes Y aplicar filtros automáticamente
        self.combo_universidad.bind("<<ComboboxSelected>>", lambda e: (self.actualizar_programas(), self.buscar()))
        self.combo_programa.bind("<<ComboboxSelected>>", lambda e: (self.actualizar_estudiantes(), self.buscar()))
        self.combo_estudiante.bind("<<ComboboxSelected>>", lambda e: (self.actualizar_items_clave(), self.buscar()))

        # Binding para ítem clave - buscar al seleccionar
        self.combo_item_clave.bind("<<ComboboxSelected>>", lambda e: self.buscar())

        # Inicializar filtros
        self._inicializar_filtros()

        # Mensaje si no hay rutas
        if not settings.ruta_doctorados and not settings.ruta_doctorados2:
            self.status_bar.config(text="No se encontró ninguna ruta de doctorados. No hay documentos cargados.")
        else:
            # Cargar documentos (usará caché si ya está cargado)
            self._cargar_documentos()
            # Si ya están en caché, poblar resultados después de un pequeño delay
            if settings.documentos_cargados:
                self.ventana.after(200, self.buscar)

    # ==============================================================================
    # MÉTODOS DE BÚSQUEDA CON DEBOUNCE
    # ==============================================================================

    def _sync_search_text(self, event):
        """Sincroniza el texto del Entry con el StringVar para debounce"""
        texto = self.entrada_busqueda.get()
        # Ignorar el placeholder
        if texto == "🔍 Buscar documentos...":
            self.search_text.set("")
        else:
            self.search_text.set(texto)
        self.ejecutar_busqueda()

    def on_search_change(self, *args):
        """Callback cuando cambia el texto de búsqueda - implementa debounce"""
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(300, self.ejecutar_busqueda)

    def ejecutar_busqueda(self):
        """Ejecuta búsqueda en thread separado para no bloquear UI"""
        texto = self.search_text.get().strip().lower()

        # Verificar si los filters combos tienen filtros activos
        filtro_u = self.combo_universidad.get()
        filtro_p = self.combo_programa.get()
        filtro_e = self.combo_estudiante.get()
        filtro_item = self.combo_item_clave.get()

        # Si no hay filtros activos y el search está vacío, limpiar y salir
        if not texto and filtro_u == '(Todos)' and filtro_p == '(Todos)' and filtro_e == '(Todos)' and filtro_item == '(Todos)':
            self.buscar_con_filtros('', filtro_u, filtro_p, filtro_e, filtro_item)
            return

        # Usar threading para no bloquear UI
        thread = threading.Thread(
            target=self._busqueda_async,
            args=(texto, filtro_u, filtro_p, filtro_e, filtro_item),
            daemon=True
        )
        thread.start()

    def _busqueda_async(self, texto, filtro_u, filtro_p, filtro_e, filtro_item):
        """Método ejecutado en thread separado"""
        # Usar after() para actualizar UI de forma segura
        self.ventana.after(0, lambda: self.buscar_con_filtros(texto, filtro_u, filtro_p, filtro_e, filtro_item))

    def buscar_con_filtros(self, filtro_nombre, filtro_u, filtro_p, filtro_e, filtro_item):
        """Ejecuta la búsqueda con los filtros dados"""
        encontrados = buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item)
        self._poblar_resultados(encontrados)

    def buscar(self):
        """Ejecuta la búsqueda de documentos"""
        filtro_u = self.combo_universidad.get()
        filtro_p = self.combo_programa.get()
        filtro_e = self.combo_estudiante.get()
        filtro_nombre = self.search_text.get().strip().lower()
        filtro_item = self.combo_item_clave.get()

        encontrados = buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item)
        self._poblar_resultados(encontrados)

    def _poblar_resultados(self, documentos_encontrados):
        """Puebla el treeview con resultados"""
        try:
            # Limpiar resultados anteriores
            self.resultados.delete(*self.resultados.get_children())
            settings.ruta_por_iid.clear()
            self.selecciones.clear()

            if not documentos_encontrados:
                self.status_bar.config(text="Sin resultados")
                return

            # Insertar resultados con zebra stripes
            for i, doc in enumerate(documentos_encontrados):
                tag = 'even' if i % 2 == 0 else 'odd'

                # Convertir nombre del archivo a nombre del glosario
                nombre_mostrar = self._convertir_nombre_a_glosario(doc['nombre'])

                # Agregar tag - intentar con checkbox, sino solo tag simple
                if self.font_checkbox:
                    checkbox_tag = ('checkbox', tag)
                else:
                    checkbox_tag = (tag,)

                iid = self.resultados.insert("", "end", values=(
                    "☐",
                    doc['universidad'].title(),
                    doc['programa'].title(),
                    doc['estudiante'].title(),
                    nombre_mostrar
                ), tags=checkbox_tag)
                settings.ruta_por_iid[iid] = doc['ruta']
                self.selecciones[iid] = True

            # Actualizar status bar
            self.status_bar.config(text=f"Mostrando {len(documentos_encontrados)} documento(s)")

        except Exception as e:
            print(f"[ERROR] Error al poblar resultados: {e}")
            # Reintentar sin tags complicadas
            try:
                self.resultados.delete(*self.resultados.get_children())
                for doc in documentos_encontrados:
                    nombre_mostrar = self._convertir_nombre_a_glosario(doc['nombre'])
                    iid = self.resultados.insert("", "end", values=(
                        "☐",
                        doc['universidad'].title(),
                        doc['programa'].title(),
                        doc['estudiante'].title(),
                        nombre_mostrar
                    ))
                    settings.ruta_por_iid[iid] = doc['ruta']
                    self.selecciones[iid] = True
                self.status_bar.config(text=f"Mostrando {len(documentos_encontrados)} documento(s)")
            except Exception as e2:
                print(f"[ERROR] Reintento sin tags también falló: {e2}")
                self.status_bar.config(text=f"Error al mostrar: {e2}")

    def _convertir_nombre_a_glosario(self, nombre_archivo):
        """Convierte el nombre del archivo a su nombre completo del glosario"""
        nombre_lower = nombre_archivo.lower()

        # Buscar en el glosario
        for nombre_completo, aliases in settings.items_clave.items():
            for alias in aliases:
                if alias.lower() in nombre_lower:
                    partes = nombre_lower.split(alias.lower())
                    if len(partes) > 1:
                        sufijo = partes[1]
                        nombre_limpio = nombre_completo.split('. ', 1)[-1]
                        return f"{nombre_limpio}{sufijo}".title()
                    else:
                        nombre_limpio = nombre_completo.split('. ', 1)[-1]
                        return nombre_limpio

        return nombre_archivo.title()

    def _inicializar_filtros(self):
        """Inicializa los filtros cargando las opciones"""
        from ui.components.filters import (
            actualizar_universidades,
            actualizar_programas,
            actualizar_estudiantes,
            actualizar_items_clave,
            configurar_autocompletado
        )

        try:
            # Actualizar universidades
            actualizar_universidades(self.combo_universidad, self.combo_programa, self.combo_estudiante)

            # Items clave - inicializar con todos los items
            opciones_items = ['(Todos)'] + list(settings.items_clave.keys())
            self.combo_item_clave['values'] = opciones_items
            self.combo_item_clave.set('(Todos)')
            configurar_autocompletado(self.combo_item_clave, opciones_items)
        except Exception as e:
            print(f"[ERROR] Error al inicializar filtros: {e}")
            # Valores por defecto
            ops_default = ['(Todos)']
            self.combo_universidad['values'] = ops_default
            self.combo_programa['values'] = ops_default
            self.combo_estudiante['values'] = ops_default
            self.combo_item_clave['values'] = ops_default
            for combo in [self.combo_universidad, self.combo_programa, self.combo_estudiante, self.combo_item_clave]:
                combo.set('(Todos)')

    def actualizar_programas(self):
        """Actualiza los programas cuando cambia la universidad"""
        from ui.components.filters import actualizar_programas
        actualizar_programas(self.combo_universidad, self.combo_programa, self.combo_estudiante)

    def actualizar_estudiantes(self):
        """Actualiza los estudiantes cuando cambia el programa"""
        from ui.components.filters import actualizar_estudiantes
        actualizar_estudiantes(self.combo_universidad, self.combo_programa, self.combo_estudiante)

    def actualizar_items_clave(self):
        """Actualiza los ítems clave cuando cambia el estudiante"""
        from ui.components.filters import actualizar_items_clave
        actualizar_items_clave(self.combo_universidad, self.combo_programa,
                              self.combo_estudiante, self.combo_item_clave)

    def limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.search_text.set('')
        self.combo_universidad.set('(Todos)')
        self.combo_programa.set('(Todos)')
        self.combo_estudiante.set('(Todos)')
        self.combo_item_clave.set('(Todos)')
        self.buscar()

    # ==============================================================================
    # EVENT HANDLERS
    # ==============================================================================

    def on_select_result(self, event):
        """Maneja la selección de un resultado"""
        # Limpiar detalles al cambiar selección
        pass

    def on_tree_click(self, event):
        """Maneja clic en el Treeview - alterna checkbox"""
        column = self.resultados.identify_column(event.x)

        # Solo primera columna
        if column == '#1' or column == '#0':
            region = self.resultados.identify_region(event.x, event.y)
            if region in ('cell', 'tree'):
                item = self.resultados.identify_row(event.y)
                if item:
                    valores = list(self.resultados.item(item)['values'])
                    if valores:
                        checkbox_actual = valores[0]
                        if checkbox_actual == '☑':
                            valores[0] = '☐'
                        else:
                            valores[0] = '☑'
                        self.resultados.item(item, values=valores)

    def toggle_seleccionar_todos(self):
        """Marca/desmarca todos los checkbox"""
        if not self._seleccionar_todos:
            # Seleccionar todos
            for item in self.resultados.get_children():
                valores = list(self.resultados.item(item)['values'])
                valores[0] = '☑'
                self.resultados.item(item, values=valores)
            self._seleccionar_todos = True
        else:
            # Deseleccionar todos
            for item in self.resultados.get_children():
                valores = list(self.resultados.item(item)['values'])
                valores[0] = '☐'
                self.resultados.item(item, values=valores)
            self._seleccionar_todos = False

    def descargar_seleccionados(self):
        """Descarga archivos marcados prioritariamente"""
        # PRIORIDAD 1: Archivos marcados
        marcados = []
        for item in self.resultados.get_children():
            valores = self.resultados.item(item)['values']
            if valores and valores[0] == '☑':
                # Obtener ruta del documento (columna 5 = index 4)
                if len(valores) >= 5:
                    iid = item
                    if iid in settings.ruta_por_iid:
                        ruta = settings.ruta_por_iid[iid]
                        if ruta:
                            marcados.append(ruta)

        if marcados:
            # Descarga masiva
            self._descarga_masiva(marcados)
            return

        # PRIORIDAD 2: Archivo con foco
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid:
            ruta = settings.ruta_por_iid[item]
            if ruta:
                abrir_pdf(ruta)
        else:
            messagebox.showwarning("Sin selección", "Selecciona un documento para descargar.")

    def _descarga_masiva(self, rutas):
        """Descarga múltiples archivos"""
        if messagebox.askyesno("Descargar", f"¿Descargar {len(rutas)} archivos?"):
            # Mostrar progreso
            progress = tk.Toplevel(self.ventana)
            progress.title("Descargando...")
            label = tk.Label(progress, text="Preparando descarga...").pack(padx=20, pady=20)

            # Usar threading para no bloquear UI
            def descarga_background():
                from services.file_service import descargar_expediente_multiple
                try:
                    descargar_expediente_multiple(rutas)
                except Exception as e:
                    self.ventana.after(0, lambda: messagebox.showerror("Error", f"Error al descargar:\n{e}"))
                finally:
                    self.ventana.after(0, progress.destroy)

            thread = threading.Thread(target=descarga_background, daemon=True)
            thread.start()

            # Cerrar progress después de iniciar thread
            progress.destroy()
            messagebox.showinfo("Éxito", f"Descarga iniciada para {len(rutas)} archivos.")

    def on_double_click(self, event):
        """Maneja el doble click en un resultado"""
        self.abrir_pdf_handler()

    def abrir_pdf_handler(self):
        """Abre el PDF seleccionado"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid:
            ruta = settings.ruta_por_iid[item]
            abrir_pdf(ruta)
        else:
            messagebox.showwarning("Selecciona algo", "Debes seleccionar un resultado.")

    def descargar_expediente_handler(self):
        """Descarga el expediente completo del estudiante"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid:
            ruta = settings.ruta_por_iid[item]
            descargar_expediente(ruta)
        else:
            messagebox.showwarning("Selecciona algo",
                                "Debes seleccionar un resultado para descargar el expediente.")

    def _cargar_documentos(self):
        """Carga los documentos desde las rutas configuradas usando threading"""
        # Verificar si las rutas están disponibles
        if not settings.ruta_doctorados and not settings.ruta_doctorados2:
            retry = messagebox.askretrycancel(
                "Rutas no encontradas",
                "Las rutas de Google Drive no están disponibles.\n"
                "El sincronizador de Google Drive puede que no haya terminado.\n\n"
                "¿Deseas reintentar?"
            )
            if retry:
                settings.ruta_doctorados, settings.ruta_oficios, settings.ruta_doctorados2 = \
                    encontrar_rutas_drive()

                if not settings.ruta_doctorados and not settings.ruta_doctorados2:
                    messagebox.showwarning(
                        "Rutas no encontradas",
                        "No se pudieron encontrar las rutas de Google Drive.\n"
                        "Asegúrate de que Google Drive Sync esté ejecutándose."
                    )
                    return
            else:
                return

        # Si ya está en caché Y hay documentos reales, solo actualizar el label y poblar resultados
        if settings.documentos_cargados and settings.documentos_drive:
            total_docs = len(settings.documentos_drive)
            self.status_bar.config(text=f"✓ {total_docs} documentos cargados (en caché)")
            # Poblar treeview con documentos en caché
            self.buscar()
            return

        # Si documentos_cargados es True pero documentos_drive está vacío,
        # forzar recarga
        if settings.documentos_cargados and not settings.documentos_drive:
            print("[WARN] documentos_cargados=True pero documentos_drive vacío - forzando recarga")
            settings.documentos_cargados = False

        # Mostrar mensaje de carga
        self.status_bar.config(text="Cargando documentos...")

        # Variables para compartir entre threads
        resultado = {'docs_cargados': 0, 'error': None}

        def cargar_en_background():
            """Función que se ejecuta en el thread de fondo"""
            try:
                settings.documentos_drive = []
                docs_cargados = 0

                print("\n[CARGA] Iniciando carga de documentos...")

                # Cargar desde ruta_doctorados
                if settings.ruta_doctorados:
                    self.ventana.after(0, lambda: self.status_bar.config(
                        text="Escaneando ruta principal..."
                    ))
                    docs1 = cargar_documentos(settings.ruta_doctorados, None)
                    settings.documentos_drive.extend(docs1)
                    docs_cargados += len(docs1)
                    print(f"[CARGA] Documentos desde ruta_doctorados: {len(docs1)}")

                # Cargar desde ruta_doctorados2
                if settings.ruta_doctorados2:
                    self.ventana.after(0, lambda: self.status_bar.config(
                        text="Escaneando ruta secundaria..."
                    ))
                    docs2 = cargar_documentos(settings.ruta_doctorados2, None)
                    settings.documentos_drive.extend(docs2)
                    docs_cargados += len(docs2)
                    print(f"[CARGA] Documentos desde ruta_doctorados2: {len(docs2)}")

                print(f"[CARGA] TOTAL documentos cargados: {docs_cargados}\n")
                resultado['docs_cargados'] = docs_cargados

            except Exception as e:
                print(f"[ERROR] Error al cargar documentos: {e}")
                resultado['error'] = str(e)

        def on_complete():
            """Callback cuando termina la carga"""
            # Verificar si hubo error
            if resultado['error']:
                self.status_bar.config(text=f"Error: {resultado['error']}")
                messagebox.showerror("Error",
                                   f"Error al cargar documentos:\n{resultado['error']}")
                return

            docs_cargados = resultado['docs_cargados']

            # Marcar como cargados para evitar re-escaneo
            settings.documentos_cargados = True

            # Actualizar status bar
            mensaje = f"✓ {docs_cargados} documentos cargados"
            self.status_bar.config(text=mensaje)

            # Poblar treeview con todos los documentos inicialmente
            self.buscar()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Sincronización",
                               f"¡Documentos cargados exitosamente!\n\n"
                               f"Total: {docs_cargados} documentos")

        # Iniciar thread de carga
        thread = threading.Thread(target=cargar_en_background, daemon=True)
        thread.start()

        # Monitorear el thread y ejecutar callback cuando termine
        def check_thread():
            if thread.is_alive():
                self.ventana.after(100, check_thread)
            else:
                on_complete()

        self.ventana.after(100, check_thread)

    def refrescar_vista(self):
        """Recrea la interfaz cuando se vuelve a entrar a la vista."""
        self.crear_interfaz()


def mostrar_docentes(ventana, on_volver, on_cerrar_sesion):
    """
    Función helper para mostrar la vista de docentes
    Args:
        ventana: Ventana principal
        on_volver: Callback para volver
        on_cerrar_sesion: Callback para cerrar sesión
    """
    DocentesView(ventana, on_volver, on_cerrar_sesion)