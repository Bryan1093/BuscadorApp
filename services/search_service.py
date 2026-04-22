"""
Servicio de búsqueda de documentos y oficios
"""
from tkinter import messagebox
import config.settings as settings
from utils.text_utils import normalizar_texto, texto_contiene


def buscar_documentos(filtro_u, filtro_p, filtro_e, filtro_nombre, filtro_item):
    """
    Busca documentos según los filtros aplicados.
    Las búsquedas son tolerantes a tildes, mayúsculas/minúsculas y eñes.
    
    IMPORTANTE: Retorna solo estudiantes únicos (un documento por estudiante)
    para mostrar en la tabla.

    Args:
        filtro_u: Filtro de universidad
        filtro_p: Filtro de programa
        filtro_e: Filtro de estudiante
        filtro_nombre: Filtro de nombre de documento
        filtro_item: Filtro de item clave
    Returns:
        list: Lista de documentos encontrados (uno por estudiante único)
    """
    encontrados = []

    # Verificar que haya documentos cargados
    if not settings.documentos_drive:
        print("[WARN] buscar_documentos: documentos_drive está vacío")
        return []

    # Normalizar filtros de texto
    filtro_nombre_norm = normalizar_texto(filtro_nombre) if filtro_nombre else ""

    try:
        for d in settings.documentos_drive:
            # Comparaciones normalizadas (tolerantes a tildes y mayúsculas) (y strings vacíos como 'Todos')
            match_u = not filtro_u or filtro_u == '(Todos)' or normalizar_texto(d['universidad']) == normalizar_texto(filtro_u)
            match_p = not filtro_p or filtro_p == '(Todos)' or normalizar_texto(d['programa']) == normalizar_texto(filtro_p)
            match_e = not filtro_e or filtro_e == '(Todos)' or normalizar_texto(d['estudiante']) == normalizar_texto(filtro_e)
            match_nombre = not filtro_nombre_norm or filtro_nombre_norm in normalizar_texto(d['nombre'])

            if match_u and match_p and match_e and match_nombre:

                if not filtro_item or filtro_item == '(Todos)':
                    encontrados.append(d)
                else:
                    alias_list = settings.items_clave.get(filtro_item, [])
                    nombre_doc_norm = normalizar_texto(d['nombre'])
                    if any(normalizar_texto(alias) in nombre_doc_norm for alias in alias_list):
                        encontrados.append(d)
    except Exception as e:
        print(f"[ERROR] buscar_documentos: {e}")

    # Sin deduplicación — mostrar todos los documentos encontrados
    return encontrados


def buscar_oficios(filtro_anio, filtro_tipo, filtro_nombre):
    """
    Busca oficios según los filtros aplicados.
    Las búsquedas son tolerantes a tildes, mayúsculas/minúsculas y eñes.
    
    Args:
        filtro_anio: Filtro de año
        filtro_tipo: Filtro de tipo de oficio
        filtro_nombre: Filtro de nombre de oficio
    Returns:
        list: Lista de oficios encontrados
    """
    docs = settings.documentos_oficios
    
    if filtro_anio != '(Todos)':
        docs = [doc for doc in docs if doc['anio'] == filtro_anio]
    
    if filtro_tipo != '(Todos)':
        docs = [doc for doc in docs if normalizar_texto(doc['tipo']) == normalizar_texto(filtro_tipo)]
    
    if filtro_nombre:
        docs = [doc for doc in docs if texto_contiene(doc['nombre'], filtro_nombre)]
    
    return docs


def obtener_programas_filtrados(universidad):
    """
    Obtiene programas filtrados por universidad
    Args:
        universidad: Nombre de la universidad o '(Todos)'
    Returns:
        list: Lista ordenada de programas
    """
    if not settings.documentos_drive:
        return []

    if universidad == '(Todos)':
        programas = sorted(set(doc['programa'] for doc in settings.documentos_drive))
    else:
        programas = sorted(set(doc['programa'] for doc in settings.documentos_drive
                             if doc['universidad'] == universidad))
    return programas


def obtener_estudiantes_filtrados(universidad, programa):
    """
    Obtiene estudiantes filtrados por universidad y programa
    Args:
        universidad: Nombre de la universidad o '(Todos)'
        programa: Nombre del programa o '(Todos)'
    Returns:
        list: Lista ordenada de estudiantes
    """
    if not settings.documentos_drive:
        return []

    estudiantes = set()
    for doc in settings.documentos_drive:
        if (universidad == '(Todos)' or doc['universidad'] == universidad) and \
           (programa == '(Todos)' or doc['programa'] == programa):
            estudiantes.add(doc['estudiante'])
    return sorted(estudiantes)


def obtener_items_clave_filtrados(universidad, programa, estudiante):
    """
    Obtiene ítems clave filtrados por universidad, programa y estudiante
    Retorna solo los ítems clave que el estudiante tiene documentos
    Args:
        universidad: Nombre de la universidad o '(Todos)'
        programa: Nombre del programa o '(Todos)'
        estudiante: Nombre del estudiante o '(Todos)'
    Returns:
        list: Lista ordenada de ítems clave que el estudiante tiene
    """
    # Si no hay estudiante seleccionado, retornar todos los items
    if estudiante == '(Todos)':
        return sorted(settings.items_clave.keys())
    
    # Filtrar documentos del estudiante
    documentos_estudiante = []
    for doc in settings.documentos_drive:
        if (universidad == '(Todos)' or doc['universidad'] == universidad) and \
           (programa == '(Todos)' or doc['programa'] == programa) and \
           doc['estudiante'] == estudiante:
            documentos_estudiante.append(doc)
    
    # Encontrar qué ítems clave tiene el estudiante
    items_encontrados = set()
    for doc in documentos_estudiante:
        nombre_doc = doc['nombre'].lower()
        # Revisar cada ítem clave
        for item_clave, alias_list in settings.items_clave.items():
            # Si algún alias del ítem clave está en el nombre del documento
            if any(alias.lower() in nombre_doc for alias in alias_list):
                items_encontrados.add(item_clave)
    
    return sorted(items_encontrados)


def obtener_tipos_oficios_filtrados(anio, estructura_oficios):
    """
    Obtiene tipos de oficios filtrados por año
    Args:
        anio: Año seleccionado o '(Todos)'
        estructura_oficios: Estructura de oficios
    Returns:
        list: Lista ordenada de tipos de oficios
    """
    tipos = set()
    if estructura_oficios:
        if anio != '(Todos)':
            for tipos_periodo in estructura_oficios.get(anio, {}).values():
                tipos.update(tipos_periodo)
        else:
            for anio_val in estructura_oficios.values():
                for tipos_periodo in anio_val.values():
                    tipos.update(tipos_periodo)
    return sorted(tipos)

