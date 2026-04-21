"""
Vista principal del módulo de Oficios
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ui.styles import configurar_estilos
from ui.components.header import crear_encabezado, crear_resumen
from ui.components.filters import (crear_filtros_oficios, crear_entrada_busqueda,
                                   crear_entrada_busqueda_con_autocompletado,
                                   actualizar_anios_oficios, actualizar_tipo_oficios)
from ui.components.results import (crear_resultados_oficios, poblar_resultados_oficios,
                                   crear_botones_oficios)
from ui.components.details import (crear_texto_detalles, mostrar_detalles_oficio, 
                                   limpiar_detalles)
from ui.components.loading_dialog import LoadingDialog
from services.search_service import buscar_oficios
from services.file_service import abrir_pdf, descargar_pdf, cargar_documentos_oficios
from utils.file_utils import obtener_estructura_oficios
from utils.path_utils import encontrar_rutas_drive
from utils.text_utils import normalizar_texto
from ui.views.login_view import limpiar_ventana
import config.settings as settings
from utils.file_utils import resource_path
from PIL import Image, ImageTk


def obtener_sugerencias_oficio(texto):
    """
    Retorna sugerencias de nombres de oficios que contienen el texto.
    Utiliza normalización para ser tolerant a tildes.
    """
    if not texto:
        return []
    if not settings.documentos_oficios:
        return []
    
    texto_norm = normalizar_texto(texto)
    nombres = set()
    
    for doc in settings.documentos_oficios:
        nombre = doc.get('nombre', '')
        if nombre and texto_norm in normalizar_texto(nombre):
            # Limitar longitud para visualización
            nombre_corto = nombre[:50] + '...' if len(nombre) > 50 else nombre
            nombres.add(nombre_corto)
    
    return sorted(nombres)[:5]


class OficiosView:
    """Vista del módulo de Oficios"""
    
    def __init__(self, ventana, on_volver, on_cerrar_sesion):
        """
        Inicializa la vista de oficios
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
        self.combo_anio = None
        self.combo_tipo = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea toda la interfaz de la vista de oficios"""
        limpiar_ventana(self.ventana)
        
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
            command=self._cargar_datos,
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
        
        # Configurar ventana
        self.ventana.title("Buscador de Oficios")
        self.ventana.state('zoomed')
        self.ventana.configure(bg="#f5f7fa")
        
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
            text="BUSCADOR DE OFICIOS",
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
        self.combo_anio, self.combo_tipo = crear_filtros_oficios(filtros_frame)
        
        # Entrada de búsqueda con autocompletado
        self.entrada_nombre = crear_entrada_busqueda_con_autocompletado(
            filtros_frame, 
            "Buscar por nombre o número de oficio:",
            ancho=50,
            callback_buscar=self.buscar,
            callback_sugerencias=obtener_sugerencias_oficio
        )
        
        # Botones de acción
        botones_frame = tk.Frame(main_content, bg="#ffffff")
        botones_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        crear_botones_oficios(botones_frame, self.buscar, self.abrir_pdf_handler,
                             self.descargar_pdf_handler)
        
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
        self.resultados, self.frame_resultados = crear_resultados_oficios(
            resultados_container, 
            self.on_select_result,
            self.on_double_click
        )
        
        # Inicializar filtros
        actualizar_anios_oficios(self.combo_anio, self.combo_tipo)
        self.combo_anio.bind("<<ComboboxSelected>>", 
                            lambda e: actualizar_tipo_oficios(self.combo_anio, self.combo_tipo))
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: None)
        
        # Cargar datos (usará caché si ya está cargado)
        self._cargar_datos()
    
    def refrescar_vista(self):
        """
        Recrea la interfaz cuando se vuelve a entrar a la vista.
        Usa el caché si ya está cargado para evitar re-escaneo.
        """
        self.crear_interfaz()
    
    def _cargar_datos(self):
        """Carga los datos de oficios usando threading"""
        # Verificar si las rutas están disponibles
        if not settings.ruta_oficios:
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
                if not settings.ruta_oficios:
                    messagebox.showwarning(
                        "Rutas no encontradas",
                        "No se pudieron encontrar las rutas de Google Drive.\n"
                        "Asegúrate de que Google Drive Sync esté ejecutándose."
                    )
                    return
            else:
                return
        
        # Si ya está en caché, solo actualizar el label
        if settings.oficios_cargados:
            total_docs = len(settings.documentos_oficios)
            self.etiqueta_resumen.config(text=f"✓ {total_docs} documentos cargados (en caché)")
            return
        
        # Crear y mostrar diálogo de carga
        loading_dialog = LoadingDialog(self.ventana, "Cargando Oficios")
        
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
                print("\n[CARGA OFICIOS] Iniciando carga de documentos...")
                
                # Actualizar estado
                self.ventana.after(0, lambda: loading_dialog.update_status(
                    "Cargando estructura de oficios...", 0
                ))
                
                # Cargar estructura y documentos
                settings.estructura_oficios = obtener_estructura_oficios(settings.ruta_oficios)
                settings.documentos_oficios = cargar_documentos_oficios(
                    settings.ruta_oficios, 
                    progress_callback
                )
                
                # Contar documentos cargados
                docs_cargados = len(settings.documentos_oficios)
                print(f"[CARGA OFICIOS] Total documentos cargados: {docs_cargados}\n")
                
                resultado['docs_cargados'] = docs_cargados
                
            except Exception as e:
                print(f"[ERROR] Error al cargar oficios: {e}")
                resultado['error'] = str(e)
        
        def on_complete():
            """Callback cuando termina la carga"""
            # Cerrar diálogo de carga
            loading_dialog.close()
            
            # Verificar si hubo error
            if resultado['error']:
                messagebox.showerror("Error", 
                                   f"Error al cargar oficios:\n{resultado['error']}")
                return
            
            docs_cargados = resultado['docs_cargados']
            
            # Marcar como cargados para evitar re-escaneo
            settings.oficios_cargados = True
            
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
        """Ejecuta la búsqueda de oficios"""
        filtro_anio = self.combo_anio.get()
        filtro_tipo = self.combo_tipo.get()
        filtro_nombre = self.entrada_nombre.get().strip().lower()
        
        encontrados = buscar_oficios(filtro_anio, filtro_tipo, filtro_nombre)
        poblar_resultados_oficios(self.resultados, self.etiqueta_resumen, encontrados)
        limpiar_detalles(self.texto_detalles)
    
    def on_select_result(self, event):
        """Maneja la selección de un resultado"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid_oficios:
            # Buscar el documento completo
            ruta = settings.ruta_por_iid_oficios[item]
            doc = next((d for d in settings.documentos_oficios if d['ruta'] == ruta), None)
            if doc:
                mostrar_detalles_oficio(self.texto_detalles, doc)
        else:
            limpiar_detalles(self.texto_detalles)
    
    def on_double_click(self, event):
        """Maneja el doble click en un resultado"""
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
        """Descarga el PDF seleccionado"""
        item = self.resultados.focus()
        if item and item in settings.ruta_por_iid_oficios:
            ruta = settings.ruta_por_iid_oficios[item]
            descargar_pdf(ruta)
        else:
            messagebox.showwarning("Selecciona algo", "Debes seleccionar un resultado.")


def mostrar_oficios(ventana, on_volver, on_cerrar_sesion):
    """
    Función helper para mostrar la vista de oficios
    Args:
        ventana: Ventana principal
        on_volver: Callback para volver
        on_cerrar_sesion: Callback para cerrar sesión
    """
    OficiosView(ventana, on_volver, on_cerrar_sesion)