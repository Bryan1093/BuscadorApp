"""
Componente de resultados de búsqueda
"""
import tkinter as tk
from tkinter import ttk, messagebox
from services.search_service import buscar_documentos, buscar_oficios
import config.settings as settings


def convertir_nombre_a_glosario(nombre_archivo):
    """
    Convierte el nombre del archivo a su nombre completo del glosario
    Args:
        nombre_archivo: Nombre del archivo (ej: "c.beca-ariasbalarezcoana")
    Returns:
        str: Nombre completo del glosario o el nombre original si no se encuentra
    """
    nombre_lower = nombre_archivo.lower()
    
    # Buscar en el glosario si el nombre contiene algún alias
    for nombre_completo, aliases in settings.items_clave.items():
        for alias in aliases:
            if alias.lower() in nombre_lower:
                # Extraer el sufijo después del alias (ej: "-ariasbalarezcoana")
                # y agregarlo al nombre completo
                partes = nombre_lower.split(alias.lower())
                if len(partes) > 1:
                    sufijo = partes[1]
                    # Limpiar el nombre completo (quitar el número al inicio)
                    nombre_limpio = nombre_completo.split('. ', 1)[-1]
                    return f"{nombre_limpio}{sufijo}".title()
                else:
                    # Si no hay sufijo, solo retornar el nombre completo
                    nombre_limpio = nombre_completo.split('. ', 1)[-1]
                    return nombre_limpio
    
    # Si no se encuentra en el glosario, retornar el nombre original
    return nombre_archivo.title()



def crear_resultados_docentes(ventana, on_select, on_double_click, on_toggle_select=None, on_seleccionar_todo=None):
    """
    Crea el treeview de resultados para docentes
    Args:
        ventana: Ventana o frame padre
        on_select: Callback al seleccionar un item
        on_double_click: Callback al hacer doble click
        on_toggle_select: Callback al togglear selección (optional)
        on_seleccionar_todo: Callback al hacer click en header para seleccionar todos (optional)
    Returns:
        tuple: (treeview, frame_contenedor) para acceso externo
    """
    columnas = ("Seleccion", "Universidad", "Programa", "Estudiante", "Nombre")
    
    # Frame contenedor
    frame_contenedor = tk.Frame(ventana, bg="#ecf0f1", relief='flat')
    frame_contenedor.pack(padx=30, pady=10, fill="both", expand=True)
    
    # Frame interno para resultados
    frame_resultados = tk.Frame(frame_contenedor, bg="#ffffff", relief="solid", bd=1)
    frame_resultados.pack(fill="both", expand=True, padx=2, pady=2)
    
# Scrollbar moderna - ESTILO SEGURO
    try:
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", style="Vertical.TScrollbar")
    except:
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    
    # Treeview
    resultados = ttk.Treeview(frame_resultados, columns=columnas, show="headings", 
                             yscrollcommand=scrollbar.set)
    scrollbar.config(command=resultados.yview)
    resultados.pack(side="left", fill="both", expand=True)

    # Configurar columnas - checkbox más grande (60px)
    resultados.heading("Seleccion", text="☑")
    resultados.column("Seleccion", anchor="center", width=60, minwidth=60)
    
    # Binding unificado para clicks en header y celdas de selección
    # Tkinter solo procesa un binding por evento, por eso combinamos ambos handlers
    def _handle_selection_click(event):
        region = resultados.identify_region(event.x, event.y)
        
        # 1. Click en heading (columna #1) → seleccionar todo
        if region == "heading":
            column = resultados.identify_column(event.x)
            if column == "#1" and on_seleccionar_todo:
                on_seleccionar_todo()
                return "break"  # Prevenir manejo default
        
        # 2. Click en celda (columna #1) → toggle checkbox
        if region == "cell":
            column = resultados.identify_column(event.x)
            if column == "#1" and on_toggle_select:
                on_toggle_select(resultados, event)
                return "break"
        
        return None  # Allow default handling para otros clicks
    
    if on_seleccionar_todo or on_toggle_select:
        resultados.bind("<Button-1>", _handle_selection_click)
    
    for col in columnas[1:]:
        resultados.heading(col, text=col)
        resultados.column(col, anchor="center", width=200, minwidth=150)
    
    # Retornar tupla con treeview y frame_contenedor
    return resultados, frame_contenedor


def crear_resultados_oficios(ventana, on_select, on_double_click):
    """
    Crea el treeview de resultados para oficios
    Args:
        ventana: Ventana o frame padre
        on_select: Callback al seleccionar un item
        on_double_click: Callback al hacer doble click
    Returns:
        tuple: (treeview, frame_contenedor) para acceso externo
    """
    columnas = ("Año", "Tipo", "Nombre")
    
    # Frame contenedor
    frame_contenedor = tk.Frame(ventana, bg="#ecf0f1", relief='flat')
    frame_contenedor.pack(padx=30, pady=10, fill="both", expand=True)
    
    # Frame interno para resultados
    frame_resultados = tk.Frame(frame_contenedor, bg="#ffffff", relief='solid', bd=1)
    frame_resultados.pack(fill="both", expand=True, padx=2, pady=2)
    
    # Scrollbar moderna - ESTILO SEGURO
    try:
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", style="Vertical.TScrollbar")
    except:
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    
    # Treeview
    resultados = ttk.Treeview(frame_resultados, columns=columnas, show="headings", 
                             yscrollcommand=scrollbar.set)
    scrollbar.config(command=resultados.yview)
    resultados.pack(side="left", fill="both", expand=True)
    
    # Configurar columnas
    for col in columnas:
        resultados.heading(col, text=col)
        resultados.column(col, anchor="center", width=250)
    
    # Colores alternados
    resultados.tag_configure('oddrow', background="#f8f9fa")
    resultados.tag_configure('evenrow', background="#ffffff")
    
    # Eventos
    resultados.bind("<<TreeviewSelect>>", on_select)
    resultados.bind("<Double-1>", on_double_click)
    
    # Retornar tupla
    return resultados, frame_contenedor


def poblar_resultados_docentes(resultados, etiqueta_resumen, documentos_encontrados):
    """
    Puebla el treeview con resultados de búsqueda de docentes
    Args:
        resultados: Widget Treeview
        etiqueta_resumen: Label de resumen
        documentos_encontrados: Lista de documentos encontrados
    """
    # Limpiar resultados anteriores
    resultados.delete(*resultados.get_children())
    settings.ruta_por_iid.clear()
    
    if not documentos_encontrados:
        messagebox.showinfo("No encontrado", 
                          "No se encontró ningún documento con los filtros aplicados.")
        etiqueta_resumen.config(text="Mostrando 0 documentos.")
        return
    
    # Insertar resultados con checkbox
    for i, doc in enumerate(documentos_encontrados):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        # Convertir el nombre del archivo al nombre del glosario
        nombre_mostrar = convertir_nombre_a_glosario(doc['nombre'])
        iid = resultados.insert("", "end", values=(
            "☑",  # Selection checkbox - checked by default
            doc['universidad'].title(),
            doc['programa'].title(),
            doc['estudiante'].title(),
            nombre_mostrar
        ), tags=(tag,))
        settings.ruta_por_iid[iid] = doc['ruta']
    
    etiqueta_resumen.config(text=f"Mostrando {len(documentos_encontrados)} documento(s).")


def poblar_resultados_oficios(resultados, etiqueta_resumen, oficios_encontrados):
    """
    Puebla el treeview con resultados de búsqueda de oficios
    Args:
        resultados: Widget Treeview
        etiqueta_resumen: Label de resumen
        oficios_encontrados: Lista de oficios encontrados
    """
    # Limpiar resultados anteriores
    resultados.delete(*resultados.get_children())
    settings.ruta_por_iid_oficios.clear()
    
    if not oficios_encontrados:
        messagebox.showinfo("No encontrado", 
                          "No se encontró ningún oficio con los filtros aplicados.")
        etiqueta_resumen.config(text="Mostrando 0 oficios.")
        return
    
    # Insertar resultados
    for i, doc in enumerate(oficios_encontrados):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        iid = resultados.insert("", "end", values=(
            doc['anio'],
            doc['tipo'],
            doc['nombre'].title()
        ), tags=(tag,))
        settings.ruta_por_iid_oficios[iid] = doc['ruta']
    
    etiqueta_resumen.config(text=f"Mostrando {len(oficios_encontrados)} oficio(s).")


def crear_botones_docentes(ventana, on_buscar, on_abrir, on_descargar_seleccionados=None):
    """
    Crea los botones de acción para docentes
    Args:
        ventana: Ventana o frame padre
        on_buscar: Callback para buscar
        on_abrir: Callback para abrir PDF
        on_descargar_seleccionados: Callback para descargar seleccionados (opcional)
    """
    frame = tk.Frame(ventana, bg="#ecf0f1")
    frame.pack(pady=15, fill='x', padx=30)
    
    # Configurar columnas con pesos iguales para distribución proporcional
    frame.rowconfigure(0, weight=1)
    for i in range(3):
        frame.columnconfigure(i, weight=1)
    
    # Botones que se expanden proporcionalmente en una sola fila
    # Columna 0: Buscar
    ttk.Button(frame, text="🔍 Buscar", command=on_buscar).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    # Columna 1: Abrir PDF
    ttk.Button(frame, text="📄 Abrir PDF", command=on_abrir).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    
    # Columna 2: Descargar Seleccionados
    if on_descargar_seleccionados:
        ttk.Button(frame, text="⬇ Descargar Seleccionados", command=on_descargar_seleccionados).grid(row=0, column=2, padx=5, pady=5, sticky='ew')


def crear_botones_oficios(ventana, on_buscar, on_abrir, on_descargar):
    """
    Crea los botones de acción para oficios
    Args:
        ventana: Ventana o frame padre
        on_buscar: Callback para buscar
        on_abrir: Callback para abrir PDF
        on_descargar: Callback para descargar PDF
    """
    frame = tk.Frame(ventana, bg="#ecf0f1")
    frame.pack(pady=15, fill='x', padx=30)
    
    # Configurar columnas con pesos iguales para distribución proporcional
    for i in range(3):
        frame.columnconfigure(i, weight=1)
    
    # Botones que se expanden proporcionalmente
    ttk.Button(frame, text="🔍 Buscar", command=on_buscar).grid(row=0, column=0, padx=5, sticky='ew')
    ttk.Button(frame, text="📄 Abrir PDF", command=on_abrir).grid(row=0, column=1, padx=5, sticky='ew')
    ttk.Button(frame, text="⬇ Descargar PDF", command=on_descargar).grid(row=0, column=2, padx=5, sticky='ew')


def crear_barra_progreso(parent):
    """
    Crea una barra de progreso con etiqueta de estado
    Args:
        parent: Widget padre
    Returns:
        tuple: (frame, variable_double, progressbar, label)
    """
    frame = tk.Frame(parent, bg="#ecf0f1")
    frame.pack(fill='x', padx=30, pady=(0, 10))
    
    # Variable para el valor de progreso (0-100)
    var = tk.DoubleVar(value=0)
    
    # Barra de progreso
    progress = ttk.Progressbar(
        frame,
        variable=var,
        maximum=100,
        mode='determinate',
        length=300
    )
    progress.pack(fill='x', pady=(5, 2))
    
    # Etiqueta de estado
    label = tk.Label(
        frame,
        text="",
        bg="#ecf0f1",
        fg="#6c757d",
        font=("Segoe UI", 10)
    )
    label.pack(pady=(0, 5))
    
    return frame, var, progress, label


def actualizar_progreso(var, label, percentage, message):
    """
    Actualiza la barra de progreso
    Args:
        var: Variable DoubleVar de la barra
        label: Label de estado
        percentage: Porcentaje (0-100)
        message: Mensaje a mostrar
    """
    var.set(percentage)
    label.config(text=message)
