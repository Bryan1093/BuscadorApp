"""
Vista principal del módulo de Oficios - Diseño moderno con Sidebar (mismo que DocentesView)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ui.styles import configurar_estilos
from ui.views.login_view import limpiar_ventana
from utils.file_utils import resource_path
from services.search_service import buscar_oficios
from services.file_service import abrir_pdf, descargar_pdf
from services.file_service import cargar_documentos_oficios
from utils.path_utils import encontrar_rutas_drive
from utils.text_utils import normalizar_texto
import config.settings as settings
from PIL import Image, ImageTk


# ==============================================================================
# PALETA PREMIUM FLAT & CLEAN (misma que DocentesView)
# ==============================================================================
COLOR_FONDO_MAIN = "#FFFFFF"
COLOR_FONDO_SIDEBAR = "#F8F9FA"
COLOR_PRIMARY = "#0EA5E9"
COLOR_PRIMARY_DARK = "#0284C7"
COLOR_ACCENT = "#F97316"
COLOR_TEXTO = "#1E293B"
COLOR_TEXTO_SEC = "#64748B"
COLOR_BORDE = "#E2E8F0"
COLOR_ZEBRA_EVEN = "#FFFFFF"
COLOR_ZEBRA_ODD = "#F1F5F9"
COLOR_SELECCION = "#0EA5E9"


def obtener_sugerencias_oficio(texto):
    """Retorna sugerencias de nombres de oficios que contienen el texto."""
    if not texto or not settings.documentos_oficios:
        return []
    
    texto_norm = normalizar_texto(texto)
    nombres = set()
    
    for doc in settings.documentos_oficios:
        nombre = doc.get('nombre', '')
        if nombre and texto_norm in normalizar_texto(nombre):
            nombre_corto = nombre[:50] + '...' if len(nombre) > 50 else nombre
            nombres.add(nombre_corto)
    
    return sorted(nombres)[:5]


class OficiosView:
    """Vista del módulo de Oficios - Diseño moderno con Sidebar"""
    
    def __init__(self, ventana, on_volver, on_cerrar_sesion):
        """Inicializa la vista de oficios"""
        self.ventana = ventana
        self.on_volver = on_volver
        self.on_cerrar_sesion = on_cerrar_sesion
        
        # Widgets
        self.resultados = None
        self.combo_anio = None
        self.combo_tipo = None
        self.entrada_busqueda = None
        self.status_bar = None
        self.font_checkbox = None
        
        # State
        self.search_text = tk.StringVar()
        self.after_id = None
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def _configurar_estilos(self):
        """Configura estilos visuales Premium Flat & Clean"""
        style = ttk.Style(self.ventana)
        style.theme_use('clam')
        
        # Header - Azul oscuro permanente
        style.configure("Treeview.Heading",
            background="#2D4B5E",
            foreground="#FFFFFF",
            relief="flat",
            font=('Segoe UI', 10, 'bold'))
        
        style.map("Treeview.Heading",
            background=[('!active', '#2D4B5E'),
                         ('active', '#2D4B5E'),
                         ('pressed', '#2D4B5E'),
                         ('!pressed', '#2D4B5E')],
            foreground=[('!active', '#FFFFFF'),
                        ('active', '#FFFFFF'),
                        ('pressed', '#FFFFFF'),
                        ('!pressed', '#FFFFFF')])
        
        # Tabla
        style.configure("Treeview",
            background=COLOR_FONDO_MAIN,
            foreground=COLOR_TEXTO,
            fieldbackground=COLOR_FONDO_MAIN,
            rowheight=45,
            font=('Segoe UI', 10),
            borderwidth=0,
            relief="flat")
        
        style.map("Treeview",
            background=[('selected', COLOR_SELECCION)],
            foreground=[('selected', 'white')])
        
        # Checkbox heading
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
        
        # Combobox
        style.configure("TCombobox",
            font=('Segoe UI', 10),
            padding=(10, 5),
            relief="flat")
        
        style.configure("TCombobox.Field",
            background=COLOR_FONDO_MAIN,
            borderwidth=1,
            lightcolor=COLOR_BORDE,
            darkcolor=COLOR_BORDE)
    
    def crear_interfaz(self):
        """Crea toda la interfaz de la vista de oficios"""
        limpiar_ventana(self.ventana)
        
        # Configurar ventana
        self.ventana.title("Buscador de Oficios")
        self.ventana.state('zoomed')
        self.ventana.configure(bg=COLOR_FONDO_MAIN)
        
        # ==============================================================================
        # CONTENEDOR PRINCIPAL CON GRID
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
        
        # --- Botón Sincronizar ---
        btn_sincro = tk.Button(
            sidebar,
            text="🔄 Sincronizar Documentos",
            font=('Segoe UI', 11, 'bold'),
            bg="#F59E0B",
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self._cargar_datos
        )
        btn_sincro.pack(pady=10, padx=20, fill='x')
        
        # --- Separator ---
        tk.Frame(sidebar, bg=COLOR_BORDE, height=1).pack(pady=10, padx=20, fill='x')
        
        # --- Filtros ---
        filtros_label = tk.Label(
            sidebar,
            text="FILTROS",
            font=('Segoe UI', 11, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        )
        filtros_label.pack(pady=(10, 5), padx=20, anchor='w')
        
        # Año
        frame_filtro_anio = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_anio.pack(fill='x', pady=8)
        
        tk.Label(
            frame_filtro_anio,
            text="AÑO",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_anio = ttk.Combobox(frame_filtro_anio, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_anio.pack(fill='x', padx=20)
        
        # Tipo
        frame_filtro_tipo = tk.Frame(sidebar, bg=COLOR_FONDO_SIDEBAR)
        frame_filtro_tipo.pack(fill='x', pady=8)
        
        tk.Label(
            frame_filtro_tipo,
            text="TIPO",
            font=('Segoe UI', 9, 'bold'),
            fg=COLOR_TEXTO_SEC,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(anchor='w', padx=20)
        self.combo_tipo = ttk.Combobox(frame_filtro_tipo, state="normal", font=('Segoe UI', 10), height=9)
        self.combo_tipo.pack(fill='x', padx=20)
        
        # --- Separator ---
        tk.Frame(sidebar, bg=COLOR_BORDE, height=1).pack(pady=10, padx=20, fill='x')
        
        # --- Usuario ---
        tk.Label(
            sidebar,
            text=f"Usuario: {settings.nombre_usuario_actual}",
            font=('Segoe UI', 10),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_SIDEBAR
        ).pack(pady=10, padx=20, anchor='w')
        
        # --- Botones al fondo ---
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
            bg="#DC2626",
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
        # MAIN CONTENT (derecha)
        # ==============================================================================
        main = tk.Frame(container, bg=COLOR_FONDO_MAIN)
        main.pack(side='left', fill='both', expand=True, padx=40, pady=40)
        
        # --- Toolbar ---
        toolbar = tk.Frame(main, bg=COLOR_FONDO_MAIN, height=50)
        toolbar.pack(fill='x', pady=(0, 15))
        toolbar.pack_propagate(False)
        
        tk.Label(
            toolbar,
            text="BUSCADOR DE OFICIOS",
            font=('Segoe UI', 16, 'bold'),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO_MAIN
        ).pack(side='left')
        
        # Botón Descargar
        btn_descargar = tk.Button(
            toolbar,
            text="💾",
            font=('Segoe UI', 14),
            bg="#0369A1",
            fg="white",
            relief="flat",
            bd=0,
            width=4,
            height=1,
            cursor="hand2",
            command=self.descargar_pdf_handler
        )
        btn_descargar.pack(side='right')
        
        # --- Buscador con borde ---
        buscador_frame_outer = tk.Frame(main, bg=COLOR_BORDE, padx=1, pady=1, relief="flat", bd=0)
        buscador_frame_outer.pack(fill='x', pady=(0, 20))
        
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
        
        self.entrada_busqueda.insert(0, "🔍 Buscar por nombre o número...")
        self.entrada_busqueda.config(fg=COLOR_TEXTO_SEC)
        
        def on_focus_in(event):
            if self.entrada_busqueda.get() == "🔍 Buscar por nombre o número...":
                self.entrada_busqueda.delete(0, tk.END)
                self.entrada_busqueda.config(fg=COLOR_TEXTO)
        
        def on_focus_out(event):
            if self.entrada_busqueda.get() == "":
                self.entrada_busqueda.insert(0, "🔍 Buscar por nombre o número...")
                self.entrada_busqueda.config(fg=COLOR_TEXTO_SEC)
        
        self.entrada_busqueda.bind("<FocusIn>", on_focus_in)
        self.entrada_busqueda.bind("<FocusOut>", on_focus_out)
        self.entrada_busqueda.bind("<KeyRelease>", self._sync_search_text)
        
        self.search_text.trace_add('write', self.on_search_change)
        
        # --- Treeview de Resultados ---
        resultados_frame = tk.Frame(main, bg=COLOR_FONDO_MAIN)
        resultados_frame.pack(fill='both', expand=True)
        
        columnas = ("Seleccion", "Año", "Tipo", "Nombre")
        
        # Scrollbar
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
        
        # Configurar columnas
        self.resultados.heading("Seleccion", text="☑")
        self.resultados.column("Seleccion", anchor="center", width=50, minwidth=50, stretch=False)
        
        self.resultados.heading("Año", text="Año")
        self.resultados.column("Año", anchor="center", width=80, minwidth=80)
        
        self.resultados.heading("Tipo", text="Tipo")
        self.resultados.column("Tipo", anchor="center", width=180, minwidth=120)
        
        self.resultados.heading("Nombre", text="Nombre del Oficio")
        self.resultados.column("Nombre", anchor="center", width=400, minwidth=200)
        
        # Zebra stripes
        self.resultados.tag_configure('odd', background=COLOR_ZEBRA_ODD)
        self.resultados.tag_configure('even', background=COLOR_ZEBRA_EVEN)
        
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
        self.resultados.bind('<Button-1>', self.on_tree_click)
        self.resultados.bind("<<TreeviewSelect>>", self.on_select_result)
        self.resultados.bind("<Double-1>", self.on_double_click)
        
        self.ventana.bind('<Control-f>', lambda e: self.entrada_busqueda.focus_set())
        self.ventana.bind('<Return>', lambda e: self.abrir_pdf_handler())
        
        # Bindings para filtros
        self.combo_anio.bind("<<ComboboxSelected>>", lambda e: self.buscar())
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self.buscar())
        
        # Inicializar filtros
        self._inicializar_filtros()
        
        # Cargar datos
        if not settings.ruta_oficios:
            self.status_bar.config(text="No se encontró la ruta de oficios.")
        else:
            self._cargar_datos()
            if settings.oficios_cargados:
                self.ventana.after(200, self.buscar)
    
    def _inicializar_filtros(self):
        """Inicializa los filtros cargando las opciones"""
        try:
            from ui.components.filters import actualizar_anios_oficios, actualizar_tipo_oficios
            
            # Solo actualizar si ya se cargó la estructura
            if settings.estructura_oficios:
                actualizar_anios_oficios(self.combo_anio, self.combo_tipo)
            else:
                # Valores por defecto si no hay datos cargados
                opciones_default = ['(Todos)']
                self.combo_anio['values'] = opciones_default
                self.combo_anio.set('(Todos)')
                self.combo_tipo['values'] = opciones_default
                self.combo_tipo.set('(Todos)')
            
            self.combo_anio.bind("<<ComboboxSelected>>", 
                              lambda e: actualizar_tipo_oficios(self.combo_anio, self.combo_tipo))
        except Exception as e:
            print(f"[ERROR] Error al inicializar filtros: {e}")
            # Fallback seguro
            opciones_default = ['(Todos)']
            self.combo_anio['values'] = opciones_default
            self.combo_anio.set('(Todos)')
            self.combo_tipo['values'] = opciones_default
            self.combo_tipo.set('(Todos)')
    
    def _sync_search_text(self, event):
        """Sincroniza el texto del Entry con el StringVar"""
        texto = self.entrada_busqueda.get()
        if texto == "🔍 Buscar por nombre o número...":
            self.search_text.set("")
        else:
            self.search_text.set(texto)
        self.ejecutar_busqueda()
    
    def on_search_change(self, *args):
        """Callback cuando cambia el texto de búsqueda"""
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(300, self.ejecutar_busqueda)
    
    def ejecutar_busqueda(self):
        """Ejecuta la búsqueda"""
        filtro_anio = self.combo_anio.get()
        filtro_tipo = self.combo_tipo.get()
        filtro_nombre = self.search_text.get().strip().lower()
        
        encontrados = buscar_oficios(filtro_anio, filtro_tipo, filtro_nombre)
        self._poblar_resultados(encontrados)
    
    def buscar(self):
        """Ejecuta la búsqueda de oficios"""
        filtro_anio = self.combo_anio.get()
        filtro_tipo = self.combo_tipo.get()
        filtro_nombre = self.search_text.get().strip().lower()
        
        encontrados = buscar_oficios(filtro_anio, filtro_tipo, filtro_nombre)
        self._poblar_resultados(encontrados)
    
    def _poblar_resultados(self, documentos_encontrados):
        """Puebla el treeview con resultados"""
        try:
            self.resultados.delete(*self.resultados.get_children())
            settings.ruta_por_iid_oficios.clear()
            
            if not documentos_encontrados:
                self.status_bar.config(text="Sin resultados")
                return
            
            for i, doc in enumerate(documentos_encontrados):
                tag = 'even' if i % 2 == 0 else 'odd'
                
                iid = self.resultados.insert("", "end", values=(
                    "☐",
                    doc.get('anio', ''),
                    doc.get('tipo', ''),
                    doc.get('nombre', '')[:60] + '...' if len(doc.get('nombre', '')) > 60 else doc.get('nombre', '')
                ), tags=(tag,))
                
                settings.ruta_por_iid_oficios[iid] = doc['ruta']
            
            self.status_bar.config(text=f"Mostrando {len(documentos_encontrados)} resultado(s)")
        
        except Exception as e:
            print(f"[ERROR] Error al poblar resultados: {e}")
            self.status_bar.config(text=f"Error: {e}")
    
    def on_tree_click(self, event):
        """Maneja clic en el Treeview"""
        column = self.resultados.identify_column(event.x)
        if column == '#1' or column == '#0':
            region = self.resultados.identify_region(event.x, event.y)
            if region in ('cell', 'tree'):
                item = self.resultados.identify_row(event.y)
                if item:
                    valores = list(self.resultados.item(item)['values'])
                    if valores:
                        checkbox_actual = valores[0]
                        valores[0] = '☐' if checkbox_actual == '☑' else '☑'
                        self.resultados.item(item, values=valores)
    
    def on_select_result(self, event):
        """Maneja la selección de un resultado"""
        pass
    
    def on_double_click(self, event):
        """Maneja el doble click"""
        self.abrir_pdf_handler()
    
    def abrir_pdf_handler(self):
        """Abre el PDF seleccionado"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid_oficios:
            ruta = settings.ruta_por_iid_oficios[item]
            abrir_pdf(ruta)
        else:
            messagebox.showwarning("Selecciona algo", "Debes seleccionar un resultado.")
    
    def descargar_pdf_handler(self):
        """Descarga el PDF seleccionado - soporta descarga múltiple"""
        # PRIORIDAD 1: Archivos marcados (con ☑)
        marcados = []
        for item in self.resultados.get_children():
            valores = self.resultados.item(item)['values']
            if valores and valores[0] == '☑':
                iid = item
                if iid in settings.ruta_por_iid_oficios:
                    ruta = settings.ruta_por_iid_oficios[iid]
                    if ruta:
                        marcados.append(ruta)
        
        if len(marcados) > 1:
            # Descarga masiva con ZIP
            self._descarga_masiva(marcados)
            return
        elif len(marcados) == 1:
            # Un solo archivo marcado
            descargar_pdf(marcados[0])
            return
        
        # PRIORIDAD 2: Archivo con foco (sin marcar)
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid_oficios:
            ruta = settings.ruta_por_iid_oficios[item]
            descargar_pdf(ruta)
        else:
            messagebox.showwarning("Selecciona algo", "Debes seleccionar un resultado.")
    
    def _descarga_masiva(self, rutas):
        """Descarga múltiples archivos en ZIP"""
        if messagebox.askyesno("Descargar", f"¿Descargar {len(rutas)} archivos en un ZIP?"):
            # Usar threading para no bloquear UI
            def descarga_background():
                from services.file_service import descargar_expediente_multiple
                try:
                    descargar_expediente_multiple(rutas)
                except Exception as e:
                    self.ventana.after(0, lambda: messagebox.showerror("Error", f"Error al descargar:\n{e}"))
            
            thread = threading.Thread(target=descarga_background, daemon=True)
            thread.start()
            messagebox.showinfo("Éxito", f"Descarga iniciada para {len(rutas)} archivos.")
    
    def _actualizar_filtros_despues_carga(self):
        """Actualiza los filtros después de cargar los datos"""
        try:
            from ui.components.filters import actualizar_anios_oficios, actualizar_tipo_oficios
            
            if settings.estructura_oficios:
                actualizar_anios_oficios(self.combo_anio, self.combo_tipo)
            else:
                # Extraer años únicos de los documentos
                anios = sorted(set(doc.get('anio', '') for doc in settings.documentos_oficios if doc.get('anio')))
                opciones = ['(Todos)'] + anios
                self.combo_anio['values'] = opciones
                self.combo_anio.set('(Todos)')
                
                # Extraer tipos únicos
                tipos = sorted(set(doc.get('tipo', '') for doc in settings.documentos_oficios if doc.get('tipo')))
                opciones_tipos = ['(Todos)'] + tipos
                self.combo_tipo['values'] = opciones_tipos
                self.combo_tipo.set('(Todos)')
        except Exception as e:
            print(f"[ERROR] Error al actualizar filtros: {e}")
    
    def _cargar_datos(self):
        """Carga los datos de oficios"""
        if not settings.ruta_oficios:
            retry = messagebox.askretrycancel(
                "Rutas no encontradas",
                "Las rutas de Google Drive no están disponibles.\n"
                "¿Deseas reintentar?"
            )
            if retry:
                settings.ruta_doctorados, settings.ruta_oficios, settings.ruta_doctorados2 = \
                    encontrar_rutas_drive()
                if not settings.ruta_oficios:
                    messagebox.showwarning("Rutas no encontradas", "No se pudieron encontrar.")
                    return
            else:
                return
        
        if settings.oficios_cargados:
            total_docs = len(settings.documentos_oficios)
            self.status_bar.config(text=f"✓ {total_docs} documentos cargados (en caché)")
            # Actualizar filtros aunque esté en caché
            self._actualizar_filtros_despues_carga()
            return
        
        self.status_bar.config(text="Cargando documentos...")
        
        # Simple threading
        def worker():
            try:
                self.ventana.after(0, lambda: self.status_bar.config(text="Escaneando..."))
                from utils.file_utils import obtener_estructura_oficios
                from services.file_service import cargar_documentos_oficios
                
                settings.estructura_oficios = obtener_estructura_oficios(settings.ruta_oficios)
                settings.documentos_oficios = cargar_documentos_oficios(settings.ruta_oficios, None)
                docs_cargados = len(settings.documentos_oficios)
                settings.oficios_cargados = True
                
                self.ventana.after(0, lambda: self.status_bar.config(
                    text=f"✓ {docs_cargados} documentos cargados"))
                # Actualizar filtros con datos cargados
                self.ventana.after(0, lambda: self._actualizar_filtros_despues_carga())
                self.ventana.after(0, lambda: self.buscar())
                self.ventana.after(0, lambda: messagebox.showinfo(
                    "Sincronización", f"¡Documentos cargados!\n\nTotal: {docs_cargados}"))
            except Exception as e:
                self.ventana.after(0, lambda: self.status_bar.config(text=f"Error: {e}"))
                self.ventana.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def refrescar_vista(self):
        """Recrea la interfaz"""
        self.crear_interfaz()


def mostrar_oficios(ventana, on_volver, on_cerrar_sesion):
    """Función helper para mostrar la vista de oficios"""
    OficiosView(ventana, on_volver, on_cerrar_sesion)