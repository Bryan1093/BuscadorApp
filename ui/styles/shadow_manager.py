"""
ShadowManager - Administrador de sombras nativas.
Asigna efectos de sombra a widgets sin usar QSS.
"""
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


class ShadowManager:
    """
    Singleton para gestionar sombras en toda la aplicación.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        # Parámetros de sombras estándar
        self._neumorphic_params = {
            'blur': 20,
            'offset': (5, 5),
            'color': QColor(0, 0, 0, 80)
        }
        
        self._glow_params = {
            'blur': 15,
            'offset': (0, 0),
            'color': QColor(0, 255, 255, 100)  # Cian neón
        }
        
        self._sidebar_shadow = {
            'blur': 25,
            'offset': (4, 0),  # Sombra hacia la derecha
            'color': QColor(0, 0, 0, 60)
        }
    
    def apply_card_shadow(self, widget):
        """Aplica sombra neumórfica a tarjetas."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self._neumorphic_params['blur'])
        shadow.setOffset(*self._neumorphic_params['offset'])
        shadow.setColor(self._neumorphic_params['color'])
        widget.setGraphicsEffect(shadow)
        return shadow
    
    def apply_glow(self, widget, color=None):
        """Aplica efecto glow a un widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self._glow_params['blur'])
        shadow.setOffset(*self._glow_params['offset'])
        
        if color:
            shadow.setColor(QColor(color))
        else:
            shadow.setColor(self._glow_params['color'])
        
        widget.setGraphicsEffect(shadow)
        return shadow
    
    def apply_sidebar_shadow(self, widget):
        """Aplica sombra específica para sidebar."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self._sidebar_shadow['blur'])
        shadow.setOffset(*self._sidebar_shadow['offset'])
        shadow.setColor(self._sidebar_shadow['color'])
        widget.setGraphicsEffect(shadow)
        return shadow
    
    def apply_neon_line(self, widget, color="#00ffff"):
        """Aplica efecto neón lineal (para líneas de tensión)."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(color))
        widget.setGraphicsEffect(shadow)
        return shadow