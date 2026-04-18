"""
Vista principal del módulo de Docentes
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ui.styles import configurar_estilos
from ui.components.header import crear_encabezado, crear_resumen
from ui.components.filters import (crear_filtros_docentes, crear_entrada_busqueda,
                                   actualizar_universidades, actualizar_programas, 
                                   actualizar_estudiantes)
from ui.components.results import (crear_resultados_docentes, poblar_resultados_docentes,
                                   crear_botones_docentes, crear_barra_progreso,
                                   actualizar_progreso)
from ui.components.details import (crear_texto_detalles, mostrar_detalles_documento, 
                                   limpiar_detalles)
from ui.components.loading_dialog import LoadingDialog
from services.search_service import buscar_documentos
from services.file_service import (abrir_pdf, descargar_expediente,
                                    descargar_expediente_multiple, cargar_documentos)
from utils.path_utils import encontrar_rutas_drive
from ui.views.login_view import limpiar_ventana
import config.settings as settings
from utils.file_utils import resource_path
from PIL import Image, ImageTk



class DocentesView:
    """Vista del módulo de Docentes"""
    
    def __init__(self, ventana, on_volver, on_cerrar_sesion):
        """
        Inicializa la vista de docentes
        Args:
            ventana: Ventana principal
            on_volver: Callback para volver a selección
            on_cerrar_sesion: Callback para cerrar sesión
        """
        self.ventana = ventana
        self.on_volver = on_volver
        self.on_cerrar_sesion = on_cerrar_sesion
        
        # Widgets que necesitamos referenciar
        self.resultados = None
        self.texto_detalles = None
        self.etiqueta_resumen = None
        self.entrada_nombre = None
        self.combo_universidad = None
        self.combo_programa = None
        self.combo_estudiante = None
        self.combo_item_clave = None
        
        # State for selection checkboxes and progress bar
        self.selecciones = {}  # {iid: True/False}
        self.progress_frame = None
        self.progress_var = None
        self.progress_label = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea toda la interfaz de la vista de docentes"""
        limpiar_ventana(self.ventana)
        
        # Configurar ventana
        self.ventana.title("Buscador de Doctorados - Docentes")
        self.ventana.state('zoomed')
        self.ventana.configure(bg="#f5f7fa")
        
        # Frame fijo para navegación
        nav_frame = tk.Frame(self.ventana, bg="#f5f7fa")
        nav_frame.pack(fill='x', pady=(10, 0))
        
        # Panel superior con logo, botones y usuario
        top_panel = tk.Frame(nav_frame, bg="#f5f7fa")
        top_panel.pack(fill='x', padx=20, pady=5)
        
        # Logo
        try:
            ruta_imagen = resource_path("imagenes/logouce.png")
            imagen_logo = Image.open(ruta_imagen)
            imagen_logo = imagen_logo.resize((60, 60), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            logo_label = tk.Label(top_panel, image=self.logo_img, bg="#f5f7fa")
            logo_label.pack(side='left', padx=(0, 15))
        except Exception as e:
            print("No se pudo cargar el logo:", e)
        
        # Botón de volver
        btn_volver = tk.Button(
            top_panel,
            text="← Volver a selección",
            command=self.on_volver,
            font=("Segoe UI", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            activebackground="#2980b9",
            activeforeground="white"
        )
        btn_volver.pack(side='left', padx=(0, 10))
        
        # Botón de sincronización
        btn_sincro = tk.Button(
            top_panel,
            text="🔄 Sincronizar",
            command=self._cargar_documentos,
            font=("Segoe UI", 12, "bold"),
            bg="#f39c12",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            activebackground="#e67e22",
            activeforeground="white"
        )
        btn_sincro.pack(side='left', padx=(0, 10))
        
        # Espaciador
        tk.Label(top_panel, text="", bg="#f5f7fa").pack(side='left', expand=True)
        
        # Información de usuario
        user_info = tk.Frame(top_panel, bg="#f5f7fa")
        user_info.pack(side='right')
        
        tk.Label(
            user_info,
            text=f"Usuario: {settings.nombre_usuario_actual}",
            font=("Segoe UI", 12),
            bg="#f5f7fa",
            fg="#6c757d"
        ).pack(side='top', anchor='e')
        
        # Botón de cierre de sesión
        btn_cerrar = tk.Button(
            user_info,
            text="Cerrar sesión",
            command=self.on_cerrar_sesion,
            font=("Segoe UI", 11),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            activebackground="#c0392b",
            activeforeground="white"
        )
        btn_cerrar.pack(side='top', anchor='e', pady=(5, 0))
        
        # Canvas y Scrollbar para hacer toda la página scrollable
        canvas_frame = tk.Frame(self.ventana, bg="#f5f7fa")
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f5f7fa", highlightthickness=0)
        scrollbar_page = tk.Scrollbar(canvas_frame, orient="vertical", 
                                     command=self.canvas.yview, width=16)
        scrollbar_page.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar_page.set)
        
        # Binding para MouseWheel - scroll de la página cuando mouse NO está sobre la tabla
        def _on_page_scroll(event):
            self.canvas.yview_scroll(int(-event.delta/120), "units")
            return "break"
        
        self.canvas.bind("<MouseWheel>", _on_page_scroll)
        
        # Frame interno scrollable
        scrollable_frame = tk.Frame(self.canvas, bg="#f5f7fa")
        canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configurar scroll region
        def configurar_scroll_region(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configurar_scroll_region)
        
        # Ajustar ancho
        def ajustar_ancho(event):
            self.canvas.itemconfig(canvas_window, width=event.width)
        
        self.canvas.bind("<Configure>", ajustar_ancho)
        
        # Crear componentes en el frame scrollable
        configurar_estilos()
        
        # Contenedor principal para el contenido
        main_content = tk.Frame(scrollable_frame, bg="#ffffff", relief='raised', bd=2)
        main_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Encabezado profesional
        header_frame = tk.Frame(main_content, bg="#ffffff")
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(
            header_frame,
            text="BUSCADOR DE DOCTORADOS",
            font=("Segoe UI Bold", 28),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor='w')
        
        # Resumen
        self.etiqueta_resumen = tk.Label(
            main_content,
            text="",
            font=("Segoe UI", 12),
            bg="#f8f9fa",
            fg="#6c757d",
            relief='solid',
            bd=1,
            padx=10,
            pady=8
        )
        self.etiqueta_resumen.pack(fill='x', padx=20, pady=(0, 15))
        
        # Panel de filtros
        filtros_frame = tk.Frame(main_content, bg="#ffffff")
        filtros_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Título de filtros
        tk.Label(
            filtros_frame,
            text="FILTROS DE BÚSQUEDA",
            font=("Segoe UI Bold", 16),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        # Filtros
        self.combo_universidad, self.combo_programa, self.combo_estudiante, self.combo_item_clave = \
            crear_filtros_docentes(filtros_frame)
        
        # Entrada de búsqueda
        self.entrada_nombre = crear_entrada_busqueda(filtros_frame, 
                                                     "Filtrar por nombre del docente:")
        
        # Botones de acción
        botones_frame = tk.Frame(main_content, bg="#ffffff")
        botones_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        crear_botones_docentes(botones_frame, self.buscar, self.abrir_pdf_handler,
                              self.descargar_seleccionados_handler)
        
        # Separador
        separador = tk.Frame(main_content, height=2, bg="#e9ecef", bd=0)
        separador.pack(fill='x', padx=20, pady=(15, 15))
        
        # Sección de Detalles - arriba en formato horizontal compacto
        detalles_container = tk.Frame(main_content, bg="#ffffff")
        detalles_container.pack(fill='x', padx=20, pady=(0, 15))
        
        # Título de detalles
        tk.Label(
            detalles_container,
            text="DETALLES",
            font=("Segoe UI Bold", 16),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        self.texto_detalles = crear_texto_detalles(detalles_container)
        
        # Separador entre detalles y resultados
        separador2 = tk.Frame(main_content, height=2, bg="#e9ecef", bd=0)
        separador2.pack(fill='x', padx=20, pady=(0, 15))
        
        # Sección de Resultados - abajo ocupando todo el ancho
        resultados_container = tk.Frame(main_content, bg="#ffffff")
        resultados_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Título de resultados
        tk.Label(
            resultados_container,
            text="RESULTADOS",
            font=("Segoe UI Bold", 16),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        # Crear resultados
        self.resultados, self.frame_resultados = crear_resultados_docentes(
            resultados_container, 
            self.on_select_result,
            self.on_double_click,
            self.on_toggle_select,
            self.on_seleccionar_todo
        )
        
        # Inicializar filtros
        actualizar_universidades(self.combo_universidad, self.combo_programa, 
                                self.combo_estudiante)
        
        # Binding para actualizar programas cuando cambia la universidad
        self.combo_universidad.bind("<<ComboboxSelected>>", 
                                   lambda e: actualizar_programas(self.combo_universidad,
                                                                 self.combo_programa,
                                                                 self.combo_estudiante))
        
        # Binding para actualizar estudiantes cuando cambia el programa
        self.combo_programa.bind("<<ComboboxSelected>>", 
                                lambda e: actualizar_estudiantes(self.combo_universidad,
                                                                self.combo_programa,
                                                                self.combo_estudiante))
        
        # Binding para actualizar ítems clave cuando cambia el estudiante
        from ui.components.filters import actualizar_items_clave
        self.combo_estudiante.bind("<<ComboboxSelected>>", 
                                  lambda e: actualizar_items_clave(self.combo_universidad,
                                                                  self.combo_programa,
                                                                  self.combo_estudiante,
                                                                  self.combo_item_clave))
        
        # Items clave - inicializar con todos los items
        opciones_items = ['(Todos)'] + list(settings.items_clave.keys())
        self.combo_item_clave['values'] = opciones_items
        self.combo_item_clave.set('(Todos)')
        
        # Configurar autocompletado para item clave
        from ui.components.filters import configurar_autocompletado
        configurar_autocompletado(self.combo_item_clave, opciones_items)
        
        # Mensaje si no hay rutas
        if not settings.ruta_doctorados and not settings.ruta_doctorados2:
            self.etiqueta_resumen.config(
                text="No se encontró ninguna ruta de doctorados. No hay documentos cargados.")
        
        # Cargar documentos (usará caché si ya está cargado)
        self._cargar_documentos()
    
    def refrescar_vista(self):
        """
        Recrea la interfaz cuando se vuelve a entrar a la vista.
        Usa el caché si ya está cargado para evitar re-escaneo.
        """
        self.crear_interfaz()
    
    def _cargar_documentos(self):
        """Carga los documentos desde las rutas configuradas usando threading"""
        # Verificar si las rutas están disponibles
        if not settings.ruta_doctorados and not settings.ruta_doctorados2:
            # Intentar reintentar encontrar las rutas
            retry = messagebox.askretrycancel(
                "Rutas no encontradas",
                "Las rutas de Google Drive no están disponibles.\n"
                "El sincronizador de Google Drive puede que no haya terminado.\n\n"
                "¿Deseas reintentar?"
            )
            if retry:
                # Reintentar encontrar las rutas
                settings.ruta_doctorados, settings.ruta_oficios, settings.ruta_doctorados2 = \
                    encontrar_rutas_drive()
                
                # Verificar si ahora se encontraron las rutas
                if not settings.ruta_doctorados and not settings.ruta_doctorados2:
                    messagebox.showwarning(
                        "Rutas no encontradas",
                        "No se pudieron encontrar las rutas de Google Drive.\n"
                        "Asegúrate de que Google Drive Sync esté ejecutándose."
                    )
                    return
            else:
                return
        
        # Si ya está en caché, solo actualizar el label
        if settings.documentos_cargados:
            total_docs = len(settings.documentos_drive)
            self.etiqueta_resumen.config(text=f"✓ {total_docs} documentos cargados (en caché)")
            return
        
        # Crear y mostrar diálogo de carga
        loading_dialog = LoadingDialog(self.ventana, "Cargando Documentos")
        
        # Variables para compartir entre threads
        resultado = {'docs_cargados': 0, 'error': None}
        
        def progress_callback(carpeta, count):
            """Callback para actualizar el progreso desde el thread"""
            # Usar after() para actualizar UI de forma segura desde otro thread
            self.ventana.after(0, lambda: loading_dialog.update_status(
                f"Escaneando: {carpeta[:50]}...",
                count
            ))
        
        def cargar_en_background():
            """Función que se ejecuta en el thread de fondo"""
            try:
                settings.documentos_drive = []
                docs_cargados = 0
                
                print("\n[CARGA] Iniciando carga de documentos...")
                
                # Cargar desde ruta_doctorados
                if settings.ruta_doctorados:
                    self.ventana.after(0, lambda: loading_dialog.update_status(
                        "Escaneando ruta principal de doctorados...", 0
                    ))
                    docs1 = cargar_documentos(settings.ruta_doctorados, progress_callback)
                    settings.documentos_drive.extend(docs1)
                    docs_cargados += len(docs1)
                    print(f"[CARGA] Documentos desde ruta_doctorados: {len(docs1)}")
                
                # Cargar desde ruta_doctorados2
                if settings.ruta_doctorados2:
                    self.ventana.after(0, lambda: loading_dialog.update_status(
                        "Escaneando ruta secundaria de doctorados...", docs_cargados
                    ))
                    docs2 = cargar_documentos(settings.ruta_doctorados2, progress_callback)
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
            # Cerrar diálogo de carga
            loading_dialog.close()
            
            # Verificar si hubo error
            if resultado['error']:
                messagebox.showerror("Error", 
                                   f"Error al cargar documentos:\n{resultado['error']}")
                return
            
            docs_cargados = resultado['docs_cargados']
            
            # Marcar como cargados para evitar re-escaneo
            settings.documentos_cargados = True
            
            # Actualizar resumen con información de carga
            if hasattr(self, 'etiqueta_resumen') and self.etiqueta_resumen:
                mensaje = f"✓ {docs_cargados} documentos cargados desde Google Drive"
                self.etiqueta_resumen.config(text=mensaje)
            
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
                # Revisar de nuevo en 100ms
                self.ventana.after(100, check_thread)
            else:
                # Thread terminó, ejecutar callback
                on_complete()
        
        # Iniciar monitoreo
        self.ventana.after(100, check_thread)

    
    def buscar(self):
        """Ejecuta la búsqueda de documentos"""
        filtro_u = self.combo_universidad.get()
        filtro_p = self.combo_programa.get()
        filtro_e = self.combo_estudiante.get()
        filtro_nombre = self.entrada_nombre.get().strip().lower()
        filtro_item = self.combo_item_clave.get()
        
        encontrados = buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item)
        poblar_resultados_docentes(self.resultados, self.etiqueta_resumen, encontrados)
        limpiar_detalles(self.texto_detalles)
    
    def on_select_result(self, event):
        """Maneja la selección de un resultado"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid:
            ruta = settings.ruta_por_iid[item]
            mostrar_detalles_documento(self.texto_detalles, ruta)
        else:
            limpiar_detalles(self.texto_detalles)
    
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
    
    def descargar_todos_handler(self):
        """Descarga todos los documentos filtrados como un expediente ZIP"""
        # Obtener los filtros actuales
        filtro_u = self.combo_universidad.get()
        filtro_p = self.combo_programa.get()
        filtro_e = self.combo_estudiante.get()
        filtro_nombre = self.entrada_nombre.get().strip().lower()
        filtro_item = self.combo_item_clave.get()
        
        # Ejecutar búsqueda con los filtros actuales
        encontrados = buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item)
        
        if not encontrados:
            messagebox.showinfo("Sin resultados", 
                              "No hay documentos con los filtros actuales para descargar.")
            return
        
        # Extraer las rutas de todos los documentos encontrados
        rutas = [doc['ruta'] for doc in encontrados]
        
        # Crear y mostrar la barra de progreso
        if self.progress_frame:
            self.progress_frame.destroy()
        
        # Crear barra de progreso
        # Find main_content frame
        main_content = None
        for child in self.ventana.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Canvas):
                        # Get scrollable frame
                        pass
        
        # Buscar el main_content en los frames
        for widget in self.ventana.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for gc in child.winfo_children():
                            if isinstance(gc, tk.Frame):
                                main_content = gc
                                break
        
        if main_content is None:
            # Fallback: crear en el último lugar conocido
            main_content = self.ventana
        
        self.progress_frame, self.progress_var, _, self.progress_label = \
            crear_barra_progreso(main_content)
        
        # Definir el callback de progreso
        def progress_callback(percentage, message):
            actualizar_progreso(self.progress_var, self.progress_label, percentage, message)
        
        # Descargar todos los documentos como un expediente ZIP con progreso
        descargar_expediente_multiple(rutas, progress_callback, self.ventana)
    
    def seleccionar_todo_handler(self):
        """Selecciona o deselecciona todos los documentos en los resultados"""
        # Obtener todos los items del treeview
        items = self.resultados.get_children()
        
        if not items:
            return
        
        # Determinar estado: si alguno está seleccionado, deseleccionar todo
        # Revisar el primer item para determinar el estado actual
        primer_item = items[0]
        valores = self.resultados.item(primer_item, 'values')
        estado_actual = valores[0] if valores else "☐"
        
        nuevo_estado = "☐" if estado_actual == "☑" else "☑"
        
        # Actualizar todos los items
        for item in items:
            valores_actuales = list(self.resultados.item(item, 'values'))
            valores_actuales[0] = nuevo_estado
            self.resultados.item(item, values=tuple(valores_actuales))
            # Guardar el estado de selección
            self.selecciones[item] = (nuevo_estado == "☑")
    
    def on_toggle_select(self, tree, event):
        """Maneja el click en la columna de selección"""
        # Obtener el item clicked
        item = tree.identify_row(event.y)
        if not item:
            return
        
        # Obtener la columna clicked
        column = tree.identify_column(event.x)
        
        # Solo responder al click en la columna de selección (columna #1)
        if column != '#1':
            return
        
        # Toggle el estado
        valores_actuales = list(tree.item(item, 'values'))
        estado_actual = valores_actuales[0]
        nuevo_estado = "☐" if estado_actual == "☑" else "☑"
        valores_actuales[0] = nuevo_estado
        tree.item(item, values=tuple(valores_actuales))
        
        # Guardar el estado de selección
        self.selecciones[item] = (nuevo_estado == "☑")
    
    def on_seleccionar_todo(self):
        """Selecciona o deselecciona todos los documentos"""
        items = self.resultados.get_children()
        
        if not items:
            return
        
        # Verificar si TODOS los items ya están seleccionados
        todos_seleccionados = all(
            self.resultados.item(item, 'values')[0] == "☑"
            for item in items
        )
        
        # Si todos están seleccionados → deseleccionar todos
        # Si no todos están seleccionados → seleccionar todos
        nuevo_estado = "☐" if todos_seleccionados else "☑"
        
        for item in items:
            valores = list(self.resultados.item(item, 'values'))
            valores[0] = nuevo_estado
            self.resultados.item(item, values=tuple(valores))
            self.selecciones[item] = (nuevo_estado == "☑")
    
    def descargar_seleccionados_handler(self):
        """Descarga solo los documentos seleccionados"""
        # Obtener items seleccionados
        items = self.resultados.get_children()
        
        if not items:
            messagebox.showinfo("Sin resultados", "No hay documentos para descargar.")
            return
        
        # Recolectar rutas de documentos marcados con ☑
        rutas = []
        for item in items:
            valores = self.resultados.item(item, 'values')
            if valores and valores[0] == "☑":
                # Obtener la ruta del documento
                if item in settings.ruta_por_iid:
                    rutas.append(settings.ruta_por_iid[item])
        
        if not rutas:
            messagebox.showinfo("Sin selección", "No has seleccionado ningún documento.\nHaz click en la columna ☑ para seleccionar.")
            return
        
        # Crear y mostrar la barra de progreso
        if self.progress_frame:
            self.progress_frame.destroy()
        
        # Buscar main_content
        main_content = None
        for widget in self.ventana.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for gc in child.winfo_children():
                            if isinstance(gc, tk.Frame):
                                main_content = gc
                                break
        
        if main_content is None:
            main_content = self.ventana
        
        self.progress_frame, self.progress_var, _, self.progress_label = \
            crear_barra_progreso(main_content)
        
        # Definir el callback de progreso
        def progress_callback(percentage, message):
            actualizar_progreso(self.progress_var, self.progress_label, percentage, message)
        
        # Descargar los documentos seleccionados como un expediente ZIP con progreso
        descargar_expediente_multiple(rutas, progress_callback, self.ventana)


def mostrar_docentes(ventana, on_volver, on_cerrar_sesion):
    """
    Función helper para mostrar la vista de docentes
    Args:
        ventana: Ventana principal
        on_volver: Callback para volver
        on_cerrar_sesion: Callback para cerrar sesión
    """
    DocentesView(ventana, on_volver, on_cerrar_sesion)