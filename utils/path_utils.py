"""
Utilidades para manejo de rutas
"""
import os
import string


def encontrar_rutas_drive():
    """
    Busca las rutas de Google Drive en todas las unidades disponibles
    Returns:
        tuple: (ruta_doctorados, ruta_oficios, ruta_doctorados2)
    """
    ruta_doctorados = None
    ruta_doctorados2 = None
    ruta_oficios = None
    
    for letra in string.ascii_uppercase:
        posible_doctorados = f"{letra}:\\Mi unidad\\Doctorados\\DB_General\\Universidad"
        if not ruta_doctorados and os.path.exists(posible_doctorados):
            ruta_doctorados = posible_doctorados
        
        posible_doctorados2 = f"{letra}:\\Mi unidad\\Doctorados\\DB_General2\\Universidad"
        if not ruta_doctorados2 and os.path.exists(posible_doctorados2):
            ruta_doctorados2 = posible_doctorados2
        
        posible_oficios = f"{letra}:\\Mi unidad\\Oficios\\DB_GeneralOficios"
        if not ruta_oficios and os.path.exists(posible_oficios):
            ruta_oficios = posible_oficios
    
    return ruta_doctorados, ruta_oficios, ruta_doctorados2


def obtener_todas_universidades(ruta):
    """
    Obtiene la lista de universidades en una ruta dada
    Args:
        ruta: Ruta del directorio de universidades
    Returns:
        list: Lista ordenada de nombres de universidades
    """
    if not ruta or not os.path.exists(ruta):
        return []
    return sorted([nombre for nombre in os.listdir(ruta) 
                   if os.path.isdir(os.path.join(ruta, nombre))])


def obtener_todas_universidades_combinadas(ruta_doctorados, ruta_doctorados2):
    """
    Obtiene universidades de ambas rutas de doctorados
    Args:
        ruta_doctorados: Primera ruta de doctorados
        ruta_doctorados2: Segunda ruta de doctorados
    Returns:
        list: Lista ordenada de universidades únicas
    """
    universidades = set()
    if ruta_doctorados:
        universidades.update(obtener_todas_universidades(ruta_doctorados))
    if ruta_doctorados2:
        universidades.update(obtener_todas_universidades(ruta_doctorados2))
    return sorted(universidades)
