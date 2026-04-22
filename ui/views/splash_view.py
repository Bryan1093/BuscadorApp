"""
Splash Screen PRO - Pantalla de carga profesional
"""
import tkinter as tk
from tkinter import ttk
import math

from utils.file_utils import resource_path
from PIL import Image, ImageTk


class CircularSpinner(tk.Canvas):
    """Spinner circular animado"""
    def __init__(self, parent, size, color):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        self.size = size
        self.color = color
        self.angle = 0
    
    def start(self):
        self._animate()
    
    def stop(self):
        if hasattr(self, '_job'):
            self.after_cancel(self._job)
    
    def _animate(self):
        self.angle = (self.angle + 15) % 360
        self.delete('all')
        
        cx = self.size / 2
        cy = self.size / 2
        r = self.size / 2 - 8
        
        for i in range(8):
            a = (self.angle - i * 45) % 360
            rad = math.radians(a)
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            
            alpha = (8 - i) / 8
            c = self._hex_rgb(self.color)
            rc = int(c[0] * 0.3 + 255 * 0.7 * alpha)
            gc = int(c[1] * 0.3 + 255 * 0.7 * alpha)
            bc = int(c[2] * 0.3 + 255 * 0.7 * alpha)
            fill = f'#{rc:02x}{gc:02x}{bc:02x}'
            
            s = 7 if i == 0 else 5
            self.create_oval(x-s, y-s, x+s, y+s, fill=fill, outline='')
        
        self._job = self.after(40, self._animate)
    
    def _hex_rgb(self, c):
        c = c.lstrip('#')
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))


class SplashScreenPro:
    """Splash Screen profesional"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BuscadorApp")
        
        # Sin bordes
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Tamaño
        w, h = 500, 450
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        
        # Colores
        BG = '#0f172a'
        BLUE = '#0ea5e9'
        WHITE = '#f8fafc'
        GRAY = '#94a3b8'
        
        # Fondo
        self.root.configure(bg=BG)
        
        # Logo
        self.logo_img = None
        try:
            path = resource_path('imagenes/logouce3.png')
            img = Image.open(path).resize((120, 120), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
        except:
            pass
        
        # Logo label
        tk.Label(root, image=self.logo_img, bg=BG).place(x=w//2-60, y=60)
        
        # Título
        tk.Label(root, text='BuscadorApp', font=('Segoe UI', 26, 'bold'), 
              fg=WHITE, bg=BG).place(x=w//2, y=200, anchor='center')
        
        tk.Label(root, text='Sistema de Gestion Documental', font=('Segoe UI', 11), 
              fg=GRAY, bg=BG).place(x=w//2, y=235, anchor='center')
        
        # Línea azul
        tk.Frame(root, bg=BLUE, height=3, width=100).place(x=w//2-50, y=265)
        
        # Spinner circular
        self.spinner = CircularSpinner(root, 45, BLUE)
        self.spinner.place(x=w//2-22, y=300)
        self.spinner.start()
        
        # Mensaje
        self.msg = tk.Label(root, text='Cargando...', font=('Segoe UI', 10), fg=GRAY, bg=BG)
        self.msg.place(x=w//2, y=360, anchor='center')
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('splash.Horizontal.TProgressbar', background=BLUE, troughcolor='#334155')
        
        self.progress = ttk.Progressbar(root, mode='indeterminate', length=250, 
                                 style='splash.Horizontal.TProgressbar')
        self.progress.place(x=w//2-125, y=390)
        self.progress.start(10)
        
        # Info
        tk.Label(root, text='v1.0 | 2026 | UCE', font=('Segoe UI', 8), 
              fg='#64748b', bg=BG).place(x=w//2, y=425, anchor='center')
    
    def actualizar_mensaje(self, texto):
        self.msg.config(text=texto)
    
    def stop(self):
        self.spinner.stop()
        self.progress.stop()


def mostrar_splash(root):
    return SplashScreenPro(root)