"""
Servicio de autenticación de usuarios
"""
import json
import hashlib
from tkinter import messagebox
from utils.file_utils import resource_path


def verificar_credenciales(usuario, contrasena):
    """
    Verifica las credenciales de un usuario
    Args:
        usuario: Nombre de usuario
        contrasena: Contraseña del usuario
    Returns:
        tuple: (valido: bool, nombre_real: str or None)
    """
    ruta_json = resource_path("data/usuarios.json")
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            lista_usuarios = json.load(f)
            usuario_hash = hashlib.sha256(usuario.encode('utf-8')).hexdigest()
            contrasena_hash = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

            usuario_encontrado = None
            for u in lista_usuarios:
                if u['usuario'] == usuario_hash:
                    usuario_encontrado = u
                    break

            if usuario_encontrado:
                if usuario_encontrado['contrasena'] == contrasena_hash:
                    return True, usuario_encontrado.get('nombre', usuario)
                else:
                    messagebox.showwarning("Credenciales incorrectas", 
                                         "Vuelve a intentarlo: usuario o contraseña incorrectos.")
                    return False, None
            else:
                messagebox.showerror("Usuario no autorizado", 
                                   "Este usuario no está registrado en el sistema.")
                return False, None

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar credenciales:\n{e}")
        return False, None
