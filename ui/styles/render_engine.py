"""
RenderEngine - Motor de rendering avanzado para fondos técnicos.
Proporciona gradiente radial, grid y glow points.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QLinearGradient, QRadialGradient, 
    QBrush, QPainterPath
)


class CyberGridBackground(QWidget):
    """
    Fondo técnico avanzado con:
    - Gradiente radial oscuro
    - Grid de líneas cian
    - Glow points en intersecciones
    """
    
    def __init__(self, parent=None, is_dark=True, grid_spacing=40):
        super().__init__(parent)
        self._is_dark = is_dark
        self._grid_spacing = grid_spacing
        self._set_colors()
    
    def _set_colors(self):
        if self._is_dark:
            # Colores para modo oscuro
            self._center_color = QColor("#0f2240")    # Más claro en centro
            self._edge_color = QColor("#050a14")     # Más oscuro en bordes
            self._line_color = QColor(0, 255, 255, 13)  # Cian 5%
            self._glow_color = QColor(0, 255, 255, 40)  # Glow point 15%
            self._bg_base = QColor("#0a1929")
        else:
            # Modo claro
            self._center_color = QColor("#fafbfc")
            self._edge_color = QColor("#d0d5db")
            self._line_color = QColor(0, 0, 0, 8)
            self._glow_color = QColor(52, 152, 219, 20)
            self._bg_base = QColor("#f5f7fa")
    
    def set_theme(self, is_dark):
        self._is_dark = is_dark
        self._set_colors()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Gradiente radial desde el centro
        center = self.rect().center()
        radius = max(self.width(), self.height())
        
        radial = QRadialGradient(center, radius)
        radial.setColorAt(0, self._center_color)
        radial.setColorAt(0.5, self._bg_base)
        radial.setColorAt(1, self._edge_color)
        
        painter.fillRect(self.rect(), QBrush(radial))
        
        # 2. Grid de líneas
        painter.setPen(QPen(self._line_color, 1))
        
        for x in range(0, self.width(), self._grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        for y in range(0, self.height(), self._grid_spacing):
            painter.drawLine(0, y, self.width(), y)
        
        # 3. Glow points en intersecciones (solo en oscuro)
        if self._is_dark:
            painter.setPen(QPen(self._glow_color, 3))
            painter.setRenderHint(QPainter.Antialiasing, False)
            
            for x in range(0, self.width(), self._grid_spacing):
                for y in range(0, self.height(), self._grid_spacing):
                    if x > 0 and y > 0:  # Evitar esquinas
                        painter.drawPoint(x, y)