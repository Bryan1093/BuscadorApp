"""
Punto de entrada principal de la aplicación AppBuscador
Aplicación modularizada para búsqueda de documentos de doctorados y oficios
"""
import tkinter as tk
from ui.views.login_view import mostrar_login, cerrar_sesion
from ui.views.selection_view import mostrar_seleccion
from ui.views.docentes_view import mostrar_docentes, DocentesView
from ui.views.oficios_view import mostrar_oficios, OficiosView
from utils.path_utils import encontrar_rutas_drive
import config.settings as settings


class AppBuscador:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        """Inicializa la aplicación"""
        self.root = tk.Tk()
        self.root.title("AppBuscador - Sistema de Gestión de Doctorados")
        
        # Instancias de vistas (para mantener estado)
        self.docentes_view = None
        self.oficios_view = None
        
        # Inicializar rutas de Drive
        self._inicializar_rutas()
        
        # Mostrar login
        mostrar_login(self.root, self.on_login_success)
    
    def _inicializar_rutas(self):
        """Inicializa las rutas de Google Drive"""
        self._reintentar_rutas()
        
        # Debug: Verificar rutas encontradas
        print("\n" + "="*60)
        print("INICIALIZACIÓN DE RUTAS")
        print("="*60)
        print(f"ruta_doctorados:  {settings.ruta_doctorados if settings.ruta_doctorados else 'NO ENCONTRADA'}")
        print(f"ruta_oficios:     {settings.ruta_oficios if settings.ruta_oficios else 'NO ENCONTRADA'}")
        print(f"ruta_doctorados2: {settings.ruta_doctorados2 if settings.ruta_doctorados2 else 'NO ENCONTRADA'}")
        print("="*60 + "\n")
    
    def _reintentar_rutas(self):
        """Reintenta encontrar las rutas de Google Drive"""
        settings.ruta_doctorados, settings.ruta_oficios, settings.ruta_doctorados2 = \
            encontrar_rutas_drive()
    
    def on_login_success(self, ventana, nombre_usuario):
        """
        Callback ejecutado al iniciar sesión exitosamente
        Args:
            ventana: Ventana principal
            nombre_usuario: Nombre del usuario que inició sesión
        """
        mostrar_seleccion(ventana, nombre_usuario, 
                         lambda: self.mostrar_modulo_docentes(ventana),
                         lambda: self.mostrar_modulo_oficios(ventana))
    
    def mostrar_modulo_docentes(self, ventana):
        """
        Muestra el módulo de docentes (reutiliza instancia si ya existe)
        Args:
            ventana: Ventana principal
        """
        if self.docentes_view is None:
            self.docentes_view = DocentesView(
                ventana,
                lambda: self.volver_a_seleccion(ventana),
                lambda: self.cerrar_sesion_handler(ventana)
            )
        else:
            self.docentes_view.refrescar_vista()
    
    def mostrar_modulo_oficios(self, ventana):
        """
        Muestra el módulo de oficios (reutiliza instancia si ya existe)
        Args:
            ventana: Ventana principal
        """
        if self.oficios_view is None:
            self.oficios_view = OficiosView(
                ventana,
                lambda: self.volver_a_seleccion(ventana),
                lambda: self.cerrar_sesion_handler(ventana)
            )
        else:
            self.oficios_view.refrescar_vista()
    
    def volver_a_seleccion(self, ventana):
        """
        Vuelve a la pantalla de selección de módulo
        Args:
            ventana: Ventana principal
        """
        mostrar_seleccion(ventana, settings.nombre_usuario_actual,
                         lambda: self.mostrar_modulo_docentes(ventana),
                         lambda: self.mostrar_modulo_oficios(ventana))
    
    def cerrar_sesion_handler(self, ventana):
        """
        Maneja el cierre de sesión
        Args:
            ventana: Ventana principal
        """
        cerrar_sesion(ventana, lambda v: mostrar_login(v, self.on_login_success))
    
    def run(self):
        """Inicia el loop principal de la aplicación"""
        self.root.mainloop()


def main():
    """Función principal"""
    app = AppBuscador()
    app.run()


if __name__ == "__main__":
    main()
