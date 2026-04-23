"""
Punto de entrada principal de la aplicación AppBuscador
Aplicación modularizada para búsqueda de documentos de doctorados y oficios
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time
from ui.views.login_view import mostrar_login, cerrar_sesion
from ui.views.selection_view import mostrar_seleccion
from ui.views.docentes_view import mostrar_docentes, DocentesView
from ui.views.oficios_view import mostrar_oficios, OficiosView
from ui.views.acerca_de_view import mostrar_acerca_de, AcercaDeView
from ui.views.splash_view import mostrar_splash
from utils.path_utils import encontrar_rutas_drive
import config.settings as settings


class AppBuscador:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        """Inicializa la aplicación"""
        self.root = tk.Tk()
        self.root.title("BuscadorApp")
        
        # Instancias de vistas (para mantener estado)
        self.docentes_view = None
        self.oficios_view = None
        self.acerca_de_view = None
        
        # MOSTRAR SPLASH SCREEN EN LA MISMA VENTANA
        self._mostrar_splash()
    
    def _mostrar_splash(self):
        """Muestra el splash screen en la misma ventana"""
        from ui.views.splash_view import mostrar_splash
        self.splash = mostrar_splash(self.root)
        self.splash.actualizar_mensaje("Inicializando...")
        
        # Luego de mostrar splash, hacer carga en background
        self._iniciar_carga()
    
    def _iniciar_carga(self):
        """Inicia la carga en background"""
        self.splash.actualizar_mensaje("Cargando...")
        
        def cargar():
            self._inicializar_rutas()
            time.sleep(2)
            self.root.after(0, self._cerrar_splash_y_login)
        
        threading.Thread(target=cargar, daemon=True).start()
    
    def _cerrar_splash_y_login(self):
        """Cierra splash y muestra login"""
        from ui.views.login_view import mostrar_login
        
        self.root.overrideredirect(False)
        self.root.attributes('-topmost', False)
        
        mostrar_login(self.root, self.on_login_success)
    
    def _inicializar_rutas(self):
        """Inicializa las rutas de Google Drive"""
        self._reintentar_rutas()
        print("\n" + "="*60)
        print("INICIALIZACIÓN DE RUTAS")
        print("="*60)
        print(f"ruta_doctorados:  {settings.ruta_doctorados if settings.ruta_doctorados else 'NO ENCONTRADA'}")
        print(f"ruta_oficios:     {settings.ruta_oficios if settings.ruta_oficios else 'NO ENCONTRADA'}")
        print(f"ruta_doctorados2: {settings.ruta_doctorados2 if settings.ruta_doctorados2 else 'NO ENCONTRADA'}")
        print("="*60 + "\n")
    
    def _reintentar_rutas(self):
        settings.ruta_doctorados, settings.ruta_oficios, settings.ruta_doctorados2 = \
            encontrar_rutas_drive()
    
    def on_login_success(self, ventana, nombre_usuario):
        mostrar_seleccion(ventana, nombre_usuario, 
                         lambda: self.mostrar_modulo_docentes(ventana),
                         lambda: self.mostrar_modulo_oficios(ventana),
                         lambda: self.mostrar_acerca_de(ventana))
    
    def mostrar_modulo_docentes(self, ventana):
        if self.docentes_view is not None:
            try:
                self.docentes_view.cerrar()
            except:
                pass
        self.docentes_view = None
        
        self.docentes_view = DocentesView(
            ventana,
            lambda: self.volver_a_seleccion(ventana),
            lambda: self.cerrar_sesion_handler(ventana)
        )
    
    def mostrar_modulo_oficios(self, ventana):
        """Muestra el módulo de oficios"""
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
                         lambda: self.mostrar_modulo_oficios(ventana),
                         lambda: self.mostrar_acerca_de(ventana))
    
    def mostrar_acerca_de(self, ventana):
        """
        Muestra la pantalla de Acerca de
        Args:
            ventana: Ventana principal
        """
        if self.acerca_de_view is None:
            self.acerca_de_view = AcercaDeView(
                ventana,
                lambda: self.volver_a_seleccion(ventana)
            )
        else:
            self.acerca_de_view.refrescar_vista()
    
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
