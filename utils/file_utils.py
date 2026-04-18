"""
Utilidades para manejo de archivos
"""
import os
import sys


def resource_path(relative_path):
    """
    Obtiene la ruta absoluta de un recurso, compatible con PyInstaller
    Args:
        relative_path: Ruta relativa del recurso
    Returns:
        str: Ruta absoluta del recurso
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Subir un nivel desde utils/ hasta la raíz del proyecto
    base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)


def obtener_estructura_oficios(ruta):
    """
    Devuelve la estructura de carpetas de oficios:
    {
        '2016': {
            'Octubre-Diciembre': ['Recibidos', 'Enviados'],
            ...
        },
        ...
    }
    Args:
        ruta: Ruta del directorio de oficios
    Returns:
        dict: Estructura jerárquica de oficios
    """
    estructura = {}
    if not ruta or not os.path.exists(ruta):
        return estructura
    
    for anio in os.listdir(ruta):
        ruta_anio = os.path.join(ruta, anio)
        if os.path.isdir(ruta_anio):
            estructura[anio] = {}
            for periodo in os.listdir(ruta_anio):
                ruta_periodo = os.path.join(ruta_anio, periodo)
                if os.path.isdir(ruta_periodo):
                    tipos = []
                    for tipo in os.listdir(ruta_periodo):
                        ruta_tipo = os.path.join(ruta_periodo, tipo)
                        if os.path.isdir(ruta_tipo):
                            tipos.append(tipo)
                    estructura[anio][periodo] = tipos
    
    return estructura
