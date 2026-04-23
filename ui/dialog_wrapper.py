"""
Wrapper de diálogos para compatibilidad entre Tkinter y PySide6.

Este módulo proporciona una interfaz unificada para messagebox y filedialog
que funciona tanto con Tkinter como con PySide6, permitiendo que el backend
permanezca independiente de la UI.

Uso:
    # En PySide6, importar antes de usar cualquier servicio:
    from ui.dialog_wrapper import setup_qt_dialogs
    setup_qt_dialogs()
    
    # Luego importar los servicios normalmente
    from services import file_service
"""
from typing import Optional, Callable, Any
import sys

# ==============================================================================
# INTERFAZ PÚBLICA - Funciones que el backend espera
# ==============================================================================

def showinfo(title: str, message: str) -> None:
    """Muestra un diálogo de información."""
    _get_dialog_impl().showinfo(title, message)


def showwarning(title: str, message: str) -> None:
    """Muestra un diálogo de advertencia."""
    _get_dialog_impl().showwarning(title, message)


def showerror(title: str, message: str) -> None:
    """Muestra un diálogo de error."""
    _get_dialog_impl().showerror(title, message)


def askyesno(title: str, message: str) -> bool:
    """Muestra un diálogo de sí/no. Returns True if 'yes'."""
    return _get_dialog_impl().askyesno(title, message)


def askretrycancel(title: str, message: str) -> bool:
    """Muestra un diálogo de reintentar/cancelar. Returns True if 'retry'."""
    return _get_dialog_impl().askretrycancel(title, message)


def asksaveasfilename(title: str = "Guardar", 
                      initialfile: str = "", 
                      defaultextension: str = "",
                      filetypes: list = None) -> Optional[str]:
    """Muestra diálogo para guardar archivo. Returns path or None."""
    return _get_dialog_impl().asksaveasfilename(title, initialfile, defaultextension, filetypes)


def askdirectory(title: str = "Seleccionar carpeta") -> Optional[str]:
    """Muestra diálogo para seleccionar carpeta. Returns path or None."""
    return _get_dialog_impl().askdirectory(title)


# ==============================================================================
# IMPLEMENTACIONES
# ==============================================================================

class _TkinterDialogs:
    """Implementación usando Tkinter (original)"""
    
    def __init__(self):
        import tkinter as tk
        from tkinter import messagebox, filedialog
        
        self._root = tk.Tk()
        self._root.withdraw()  # Ocultar ventana raíz
        self._messagebox = messagebox
        self._filedialog = filedialog
    
    def showinfo(self, title: str, message: str):
        self._messagebox.showinfo(title, message)
    
    def showwarning(self, title: str, message: str):
        self._messagebox.showwarning(title, message)
    
    def showerror(self, title: str, message: str):
        self._messagebox.showerror(title, message)
    
    def askyesno(self, title: str, message: str) -> bool:
        return self._messagebox.askyesno(title, message)
    
    def askretrycancel(self, title: str, message: str) -> bool:
        return self._messagebox.askretrycancel(title, message)
    
    def asksaveasfilename(self, title: str, initialfile: str, 
                         defaultextension: str, filetypes: list) -> Optional[str]:
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        return self._filedialog.asksaveasfilename(
            title=title,
            initialfile=initialfile,
            defaultextension=defaultextension,
            filetypes=filetypes
        )
    
    def askdirectory(self, title: str) -> Optional[str]:
        return self._filedialog.askdirectory(title=title)


class _QtDialogs:
    """Implementación usando PySide6"""
    
    def __init__(self):
        from PySide6.QtWidgets import QMessageBox, QFileDialog, QWidget
        from PySide6.QtCore import Qt
        
        self._msg_box = QMessageBox
        self._file_dialog = QFileDialog
        self._parent: QWidget = None
    
    def set_parent(self, parent):
        """Establecer widget padre para los diálogos"""
        self._parent = parent
    
    def showinfo(self, title: str, message: str):
        msg = self._msg_box(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(self._msg_box.Information)
        msg.exec()
    
    def showwarning(self, title: str, message: str):
        msg = self._msg_box(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(self._msg_box.Warning)
        msg.exec()
    
    def showerror(self, title: str, message: str):
        msg = self._msg_box(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(self._msg_box.Critical)
        msg.exec()
    
    def askyesno(self, title: str, message: str) -> bool:
        msg = self._msg_box(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(self._msg_box.Question)
        msg.setStandardButtons(self._msg_box.Yes | self._msg_box.No)
        msg.setDefaultButton(self._msg_box.No)
        result = msg.exec()
        return result == self._msg_box.Yes
    
    def askretrycancel(self, title: str, message: str) -> bool:
        msg = self._msg_box(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(self._msg_box.Warning)
        msg.setStandardButtons(self._msg_box.Retry | self._msg_box.Cancel)
        msg.setDefaultButton(self._msg_box.Cancel)
        result = msg.exec()
        return result == self._msg_box.Retry
    
    def asksaveasfilename(self, title: str, initialfile: str,
                         defaultextension: str, filetypes: list) -> Optional[str]:
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        
        # Convertir filetypes a formato Qt
        qt_filetypes = []
        for ft in filetypes:
            if isinstance(ft, tuple):
                qt_filetypes.append(ft)
            else:
                qt_filetypes.append((ft, "*.*"))
        
        result = self._file_dialog.getSaveFileName(
            self._parent,
            title,
            initialfile,
            ";;".join([f"{name} ({pattern})" for name, pattern in qt_filetypes])
        )
        
        if result and result[0]:
            return result[0]
        return None
    
    def askdirectory(self, title: str) -> Optional[str]:
        result = self._file_dialog.getExistingDirectory(
            self._parent,
            title,
            options=self._file_dialog.ShowDirsOnly
        )
        
        if result:
            return result
        return None


# ==============================================================================
# SISTEMA DE INYECCIÓN DE DEPENDENCIAS
# ==============================================================================

_dialog_impl: Optional[object] = None
_initialized = False


def _get_dialog_impl():
    """Retorna la implementación actual de diálogos"""
    global _dialog_impl
    if _dialog_impl is None:
        # Por defecto, usar Tkinter
        _dialog_impl = _TkinterDialogs()
    return _dialog_impl


def setup_tkinter_dialogs():
    """
    Configura el wrapper para usar diálogos de Tkinter.
    Útil para desarrollo o cuando se ejecuta sin Qt.
    """
    global _dialog_impl, _initialized
    _dialog_impl = _TkinterDialogs()
    _initialized = True


def setup_qt_dialogs(parent=None):
    """
    Configura el wrapper para usar diálogos de PySide6.
    Debe llamarse antes de importar los servicios.
    
    Args:
        parent: Widget padre para los diálogos (opcional)
    """
    global _dialog_impl, _initialized
    
    # Importar PySide6 aquí para evitar errores si no está instalado
    try:
        from PySide6.QtWidgets import QApplication
        _dialog_impl = _QtDialogs()
        if parent is not None:
            _dialog_impl.set_parent(parent)
        elif QApplication.instance():
            # Usar ventana principal si está disponible
            _dialog_impl.set_parent(QApplication.instance().activeWindow())
        _initialized = True
    except ImportError:
        print("[WARN] PySide6 no disponible, usando Tkinter")
        _dialog_impl = _TkinterDialogs()


def inject_into_services():
    """
    Inyecta el wrapper en los módulos de servicio.
    Reemplaza los imports de tkinter.messagebox y tkinter.filedialog.
    """
    global _initialized
    
    if not _initialized:
        setup_qt_dialogs()
    
    # Reemplazar en sys.modules para que los imports posteriores funcionen
    import types
    
    # Crear módulos fake con nuestras funciones
    messagebox_module = types.ModuleType('tkinter.messagebox')
    filedialog_module = types.ModuleType('tkinter.filedialog')
    
    # Copiar funciones al módulo
    messagebox_module.showinfo = showinfo
    messagebox_module.showwarning = showwarning
    messagebox_module.showerror = showerror
    messagebox_module.askyesno = askyesno
    messagebox_module.askretrycancel = askretrycancel
    
    filedialog_module.asksaveasfilename = asksaveasfilename
    filedialog_module.askdirectory = askdirectory
    
    # Registrar en sys.modules
    sys.modules['tkinter.messagebox'] = messagebox_module
    sys.modules['tkinter.filedialog'] = filedialog_module


def is_initialized() -> bool:
    """Verifica si el wrapper ha sido inicializado"""
    return _initialized