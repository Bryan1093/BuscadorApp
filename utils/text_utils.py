"""
Utilidades para procesamiento de texto
"""
import unicodedata


def normalizar_texto(texto):
    """
    Normaliza texto para búsquedas con tolerancia a caracteres especiales.
    - Convierte a minúsculas
    - Elimina tildes y diacríticos
    - Ejemplos: "María" -> "maria", "PeñA" -> "penA", "ñoño" -> "nono"
    
    Args:
        texto: Texto a normalizar
    Returns:
        str: Texto normalizado (sin tildes, en minúsculas)
    """
    if not texto:
        return ""
    
    # Normalizar a forma NFD (descompone caracteres con diacríticos)
    # Ej: "á" -> "a" + marca combinante
    normalized = unicodedata.normalize('NFD', texto.lower())
    
    # Filtrar caracteres diacríticos (marcas de combinación Unicode)
    # Estos son los caracteres que aparecen después de una letra normal
    return ''.join(c for c in normalized if not unicodedata.combining(c))


def texto_contiene(texto, busqueda):
    """
    Verifica si un texto contiene una búsqueda, ignorando tildes y mayúsculas.
    
    Args:
        texto: Texto donde buscar
        busqueda: Texto a buscar
    Returns:
        bool: True si contiene, False si no
    """
    texto_norm = normalizar_texto(texto)
    busqueda_norm = normalizar_texto(busqueda)
    return busqueda_norm in texto_norm


def texto_empieza_con(texto, prefijo):
    """
    Verifica si un texto empieza con un prefijo, ignorando tildes y mayúsculas.
    
    Args:
        texto: Texto a verificar
        prefijo: Prefijo a buscar
    Returns:
        bool: True si empieza con el prefijo, False si no
    """
    texto_norm = normalizar_texto(texto)
    prefijo_norm = normalizar_texto(prefijo)
    return texto_norm.startswith(prefijo_norm)
