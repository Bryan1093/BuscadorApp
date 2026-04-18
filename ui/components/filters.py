"""
Componentes de filtros para búsqueda
"""
import tkinter as tk
from tkinter import ttk
from services.search_service import (obtener_programas_filtrados, 
                                     obtener_estudiantes_filtrados,
                                     obtener_tipos_oficios_filtrados)
from utils.path_utils import obtener_todas_universidades_combinadas
from utils.text_utils import normalizar_texto
import config.settings as settings


def configurar_autocompletado(combobox, todas_opciones):
    """
    Configura el autocompletado para un combobox con popup personalizado
    Args:
        combobox: El combobox a configurar
        todas_opciones: Lista de todas las opciones disponibles
    """
    # Variable para el popup
    popup = None
    listbox = None
    
    def cerrar_popup():
        nonlocal popup, listbox
        if popup:
            try:
                popup.destroy()
            except:
                pass
            popup = None
            listbox = None
    
    def mostrar_popup(opciones_filtradas):
        nonlocal popup, listbox
        
        # Cerrar popup anterior si existe
        cerrar_popup()
        
        if not opciones_filtradas:
            return
        
        # Crear popup
        popup = tk.Toplevel(combobox)
        popup.wm_overrideredirect(True)
        popup.wm_attributes('-topmost', True)
        
        # Posicionar debajo del combobox
        x = combobox.winfo_rootx()
        y = combobox.winfo_rooty() + combobox.winfo_height()
        width = combobox.winfo_width()
        popup.wm_geometry(f"{width}x150+{x}+{y}")
        
        # Crear listbox con scrollbar
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, 
                            font=('Segoe UI', 10), height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Agregar opciones
        for opcion in opciones_filtradas[:20]:  # Limitar a 20 opciones
            listbox.insert(tk.END, opcion)
        
        # Evento de selección
        def on_select(event):
            if listbox.curselection():
                seleccion = listbox.get(listbox.curselection())
                combobox.set(seleccion)
                cerrar_popup()
                # Disparar evento de selección para actualizar filtros dependientes
                combobox.event_generate('<<ComboboxSelected>>')
                combobox.focus_set()
        
        listbox.bind('<<ListboxSelect>>', on_select)
        listbox.bind('<Double-Button-1>', on_select)
    
    def on_keyrelease(event):
        # Ignorar teclas especiales
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Escape'):
            if event.keysym == 'Escape':
                cerrar_popup()
            return
        
        # Obtener texto actual
        texto = combobox.get()
        
        # Limpiar "(Todos)"
        if texto == "(Todos)":
            combobox.set("")
            return
        
        # Normalizar para búsqueda tolerante a tildes
        texto_norm = normalizar_texto(texto)
        
        # Filtrar opciones
        if not texto:
            combobox['values'] = todas_opciones
            cerrar_popup()
        else:
            opciones_filtradas = [
                opcion for opcion in todas_opciones 
                if texto_norm in normalizar_texto(opcion)
            ]
            combobox['values'] = opciones_filtradas
            
            # Mostrar popup con resultados
            if opciones_filtradas:
                mostrar_popup(opciones_filtradas)
            else:
                cerrar_popup()
    
    def on_click(event):
        if combobox.get() == "(Todos)":
            combobox.set("")
    
    def on_focusout(event):
        # Cerrar popup cuando pierde el foco (con delay mínimo para permitir clicks en listbox)
        combobox.after(100, cerrar_popup)
    
    # Vincular eventos
    combobox.bind('<KeyRelease>', on_keyrelease)
    combobox.bind('<Button-1>', on_click)
    combobox.bind('<FocusOut>', on_focusout)


def crear_filtros_docentes(ventana):
    """
    Crea los filtros para búsqueda de docentes
    Layout en 2 filas de 2 filtros cada una para mejor visibilidad:
    - Fila 1: Universidad (50%) | Programa (50%)
    - Fila 2: Estudiante (50%) | Ítem Clave (50%)
    
    Args:
        ventana: Ventana o frame padre
    Returns:
        tuple: (combo_universidad, combo_programa, combo_estudiante, combo_item_clave)
    """
    frame = tk.Frame(ventana, bg="#ecf0f1", relief='flat')
    frame.pack(pady=15, padx=30, fill='x')
    
    # Configurar columnas con pesos proporcionales (50% cada filtro)
    # Columnas: 0(etq) 1(combo) 2(espacio) 3(etq) 4(combo)
    frame.columnconfigure(0, weight=15)   # Label
    frame.columnconfigure(1, weight=35)  # Combo
    frame.columnconfigure(2, weight=5)   # Espacio
    frame.columnconfigure(3, weight=15)  # Label
    frame.columnconfigure(4, weight=35)  # Combo
    
    def crear_fila(fila, texto_label, texto_label2):
        """Crea una fila con dos grupos de label + combo"""
        # Primer filtro
        lbl1 = tk.Label(frame, text=texto_label, font=('Segoe UI', 10, 'bold'), 
                       bg="#ecf0f1", fg="#2c3e50", anchor='e')
        lbl1.grid(row=fila, column=0, padx=(15, 5), pady=6, sticky='ew')
        
        combo1 = ttk.Combobox(frame, state="normal", font=('Segoe UI', 10))
        combo1.grid(row=fila, column=1, padx=(0, 10), pady=6, sticky='ew')
        
        # Segundo filtro
        lbl2 = tk.Label(frame, text=texto_label2, font=('Segoe UI', 10, 'bold'), 
                       bg="#ecf0f1", fg="#2c3e50", anchor='e')
        lbl2.grid(row=fila, column=3, padx=(5, 5), pady=6, sticky='ew')
        
        combo2 = ttk.Combobox(frame, state="normal", font=('Segoe UI', 10))
        combo2.grid(row=fila, column=4, padx=(0, 15), pady=6, sticky='ew')
        
        return combo1, combo2

    # Fila 0: Universidad y Programa
    combo_universidad, combo_programa = crear_fila(0, "Universidad:", "Programa:")
    
    # Fila 1: Estudiante e Ítem Clave
    combo_estudiante, combo_item_clave = crear_fila(1, "Estudiante:", "Ítem Clave:")

    return combo_universidad, combo_programa, combo_estudiante, combo_item_clave


def crear_filtros_oficios(ventana):
    """
    Crea los filtros para búsqueda de oficios
    Args:
        ventana: Ventana o frame padre
    Returns:
        tuple: (combo_anio_oficio, combo_tipo_oficio)
    """
    frame = tk.Frame(ventana, bg="#ecf0f1", relief='flat')
    frame.pack(pady=15, padx=30)
    
    def crear_etiqueta(texto, fila, columna):
        tk.Label(frame, text=texto, font=('Segoe UI', 10, 'bold'), 
                bg="#ecf0f1", fg="#2c3e50").grid(row=fila, column=columna, 
                                                 padx=8, pady=5, sticky='e')
    
    # Año - más ancho y permite escribir
    crear_etiqueta("Año:", 0, 0)
    combo_anio_oficio = ttk.Combobox(frame, width=25, state="normal", font=('Segoe UI', 10))
    combo_anio_oficio.grid(row=0, column=1, padx=8, pady=5)
    
    # Tipo - más ancho y permite escribir
    crear_etiqueta("Tipo:", 0, 2)
    combo_tipo_oficio = ttk.Combobox(frame, width=30, state="normal", font=('Segoe UI', 10))
    combo_tipo_oficio.grid(row=0, column=3, padx=8, pady=5)
    
    return combo_anio_oficio, combo_tipo_oficio


def actualizar_universidades(combo_universidad, combo_programa, combo_estudiante):
    """
    Actualiza el combo de universidades
    Args:
        combo_universidad: Combobox de universidad
        combo_programa: Combobox de programa
        combo_estudiante: Combobox de estudiante
    """
    universidades = obtener_todas_universidades_combinadas(
        settings.ruta_doctorados, settings.ruta_doctorados2)
    settings.universidades_lista = universidades
    opciones = ['(Todos)'] + universidades
    combo_universidad['values'] = opciones
    combo_universidad.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_universidad, opciones)
    
    actualizar_programas(combo_universidad, combo_programa, combo_estudiante)


def actualizar_programas(combo_universidad, combo_programa, combo_estudiante):
    """
    Actualiza el combo de programas según la universidad seleccionada
    Args:
        combo_universidad: Combobox de universidad
        combo_programa: Combobox de programa
        combo_estudiante: Combobox de estudiante
    """
    u = combo_universidad.get()
    programas = obtener_programas_filtrados(u)
    opciones = ['(Todos)'] + programas
    combo_programa['values'] = opciones
    combo_programa.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_programa, opciones)
    
    actualizar_estudiantes(combo_universidad, combo_programa, combo_estudiante)


def actualizar_estudiantes(combo_universidad, combo_programa, combo_estudiante):
    """
    Actualiza el combo de estudiantes según universidad y programa
    Args:
        combo_universidad: Combobox de universidad
        combo_programa: Combobox de programa
        combo_estudiante: Combobox de estudiante
    """
    u = combo_universidad.get()
    p = combo_programa.get()
    estudiantes = obtener_estudiantes_filtrados(u, p)
    opciones = ['(Todos)'] + estudiantes
    combo_estudiante['values'] = opciones
    combo_estudiante.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_estudiante, opciones)


def actualizar_items_clave(combo_universidad, combo_programa, combo_estudiante, combo_item_clave):
    """
    Actualiza el combo de ítems clave según universidad, programa y estudiante
    Args:
        combo_universidad: Combobox de universidad
        combo_programa: Combobox de programa
        combo_estudiante: Combobox de estudiante
        combo_item_clave: Combobox de ítem clave
    """
    from services.search_service import obtener_items_clave_filtrados
    
    u = combo_universidad.get()
    p = combo_programa.get()
    e = combo_estudiante.get()
    
    items_clave = obtener_items_clave_filtrados(u, p, e)
    opciones = ['(Todos)'] + items_clave
    combo_item_clave['values'] = opciones
    combo_item_clave.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_item_clave, opciones)


def actualizar_anios_oficios(combo_anio, combo_tipo):
    """
    Actualiza el combo de años de oficios
    Args:
        combo_anio: Combobox de año
        combo_tipo: Combobox de tipo
    """
    if settings.estructura_oficios:
        anios = sorted(settings.estructura_oficios.keys())
    else:
        anios = []
    opciones = ['(Todos)'] + anios
    combo_anio['values'] = opciones
    combo_anio.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_anio, opciones)
    
    actualizar_tipo_oficios(combo_anio, combo_tipo)


def actualizar_tipo_oficios(combo_anio, combo_tipo):
    """
    Actualiza el combo de tipos de oficios según el año
    Args:
        combo_anio: Combobox de año
        combo_tipo: Combobox de tipo
    """
    anio = combo_anio.get()
    tipos = obtener_tipos_oficios_filtrados(anio, settings.estructura_oficios)
    opciones = ['(Todos)'] + tipos
    combo_tipo['values'] = opciones
    combo_tipo.set('(Todos)')
    
    # Configurar autocompletado
    configurar_autocompletado(combo_tipo, opciones)


def crear_entrada_busqueda(ventana, texto_placeholder, ancho=80):
    """
    Crea un campo de entrada para búsqueda
    Args:
        ventana: Ventana o frame padre
        texto_placeholder: Texto del placeholder
        ancho: Ancho del campo de entrada
    Returns:
        Entry: Campo de entrada
    """
    frame_entrada = tk.Frame(ventana, bg="#ecf0f1")
    frame_entrada.pack(pady=(5, 10), padx=30)
    
    tk.Label(frame_entrada, text=f"🔍 {texto_placeholder}", 
            font=("Segoe UI", 10, 'bold'), bg="#ecf0f1", fg="#2c3e50").pack(pady=(0, 5))
    
    entrada = tk.Entry(frame_entrada, width=ancho, font=("Segoe UI", 11), 
                      relief="solid", bd=1, bg="white", fg="#2c3e50")
    entrada.pack(pady=5)
    entrada.insert(0, "")
    
    return entrada
