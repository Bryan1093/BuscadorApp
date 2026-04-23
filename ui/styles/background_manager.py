"""
BackgroundManager - Sistema de fondo con patrón de cuadrícula.
Proporciona un widget base que dibuja líneas de grid.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient


class GridBackground(QWidget):
    """
    Widget de fondo con patrón de cuadrícula (grid).
    
    Debe usarse como widget base o integrarse en las vistas.
    """
    
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self._is_dark = is_dark
        self._grid_spacing = 40  # pixels entre líneas
        self._set_colors()
    
    def _set_colors(self):
        """Configura los colores según el tema."""
        if self._is_dark:
            self._bg_color = QColor("#0a1929")  # azul noche
            self._line_color = QColor(0, 255, 255, 25)  # cian con opacidad 10%
        else:
            self._bg_color = QColor("#f5f7fa")  # gris nube
            self._line_color = QColor(0, 0, 0, 13)  # gris con opacidad 5%
    
    def set_theme(self, is_dark):
        """Cambia el tema del fondo."""
        self._is_dark = is_dark
        self._set_colors()
        self.update()  # Repintar
    
    def paintEvent(self, event):
        """Dibuja el fondo con cuadrícula."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo sólido
        painter.fillRect(self.rect(), self._bg_color)
        
        # Dibujar cuadrícula
        painter.setPen(QPen(self._line_color, 1))
        
        # Líneas verticales
        x = 0
        while x < self.width():
            painter.drawLine(x, 0, x, self.height())
            x += self._grid_spacing
        
        # Líneas horizontales
        y = 0
        while y < self.height():
            painter.drawLine(0, y, self.width(), y)
            y += self._grid_spacing


class GradientBackground(QWidget):
    """
    Fondo con degradado vertical (opcional, más elaborado).
    """
    
    def __init__(self, parent=None, is_dark=True):
        super().__init__(parent)
        self._is_dark = is_dark
        self._grid_spacing = 50
        self._set_colors()
    
    def _set_colors(self):
        if self._is_dark:
            self._gradient = QLinearGradient(0, 0, 0, self.height())
            self._gradient.setColorAt(0, QColor("#0a1929"))
            self._gradient.setColorAt(1, QColor("#0f2240"))
            self._line_color = QColor(0, 255, 255, 20)
        else:
            self._gradient = QLinearGradient(0, 0, 0, self.height())
            self._gradient.setColorAt(0, QColor("#f5f7fa"))
            self._gradient.setColorAt(1, QColor("#ecf0f1"))
            self._line_color = QColor(0, 0, 0, 10)
    
    def set_theme(self, is_dark):
        self._is_dark = is_dark
        self._set_colors()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Degradado
        painter.fillRect(self.rect(), self._gradient)
        
        # Grid
        painter.setPen(QPen(self._line_color, 1))
        
        for x in range(0, self.width(), self._grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        for y in range(0, self.height(), self._grid_spacing):
            painter.drawLine(0, y, self.width(), y)