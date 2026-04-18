"""
Servicio de operaciones con archivos y documentos
"""
import os
import shutil
import zipfile
import threading
from tkinter import messagebox, filedialog
import config.settings as settings


def cargar_documentos(ruta, progress_callback=None):
    """
    Carga todos los documentos PDF de una ruta dada
    Args:
        ruta: Ruta del directorio a escanear
        progress_callback: Función opcional para reportar progreso (carpeta_actual, num_documentos)
    Returns:
        list: Lista de diccionarios con información de documentos
    """
    if not ruta:
        return []
    
    documentos = []
    for carpeta, _, archivos in os.walk(ruta):
        # Reportar progreso si se proporcionó callback
        if progress_callback:
            carpeta_relativa = os.path.relpath(carpeta, ruta)
            progress_callback(carpeta_relativa, len(documentos))
        
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                ruta_completa = os.path.join(carpeta, archivo)
                nombre_archivo = archivo.replace('.pdf', '').replace('_', ' ').lower()

                partes_ruta = os.path.relpath(ruta_completa, ruta).split(os.sep)
                universidad = partes_ruta[0] if len(partes_ruta) > 0 else ''
                programa = partes_ruta[1] if len(partes_ruta) > 1 else ''
                estudiante = partes_ruta[2] if len(partes_ruta) > 2 else ''

                documentos.append({
                    'universidad': universidad,
                    'programa': programa,
                    'estudiante': estudiante,
                    'nombre': nombre_archivo,
                    'ruta': ruta_completa
                })
    
    return documentos


def cargar_documentos_oficios(ruta, progress_callback=None):
    """
    Carga todos los oficios PDF de una ruta dada
    Args:
        ruta: Ruta del directorio de oficios
        progress_callback: Función opcional para reportar progreso (carpeta_actual, num_documentos)
    Returns:
        list: Lista de diccionarios con información de oficios
    """
    if not ruta:
        return []
    
    documentos = []
    for carpeta, _, archivos in os.walk(ruta):
        # Reportar progreso si se proporcionó callback
        if progress_callback:
            carpeta_relativa = os.path.relpath(carpeta, ruta)
            progress_callback(carpeta_relativa, len(documentos))
        
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                ruta_completa = os.path.join(carpeta, archivo)
                partes_ruta = os.path.relpath(ruta_completa, ruta).split(os.sep)
                
                if len(partes_ruta) >= 4:
                    anio = partes_ruta[0]
                    periodo = partes_ruta[1]
                    tipo = partes_ruta[2]
                else:
                    anio = periodo = tipo = ''
                
                nombre_archivo = archivo.replace('.pdf', '').replace('_', ' ').lower()
                documentos.append({
                    'anio': anio,
                    'periodo': periodo,
                    'tipo': tipo,
                    'nombre': nombre_archivo,
                    'ruta': ruta_completa
                })
    
    return documentos


def abrir_pdf(ruta):
    """
    Abre un archivo PDF con la aplicación predeterminada
    Args:
        ruta: Ruta del archivo PDF
    """
    try:
        os.startfile(ruta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")


def abrir_carpeta(ruta_archivo):
    """
    Abre la carpeta que contiene un archivo
    Args:
        ruta_archivo: Ruta del archivo
    """
    import subprocess
    import sys
    
    carpeta = os.path.dirname(ruta_archivo)
    try:
        if os.name == 'nt':
            os.startfile(carpeta)
        elif os.name == 'posix':
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', carpeta])
        else:
            messagebox.showwarning("No soportado", 
                                 "No se puede abrir la carpeta en este sistema.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")


def descargar_pdf(ruta_origen):
    """
    Descarga una copia del PDF permitiendo al usuario elegir la ubicación
    Args:
        ruta_origen: Ruta del archivo PDF original
    """
    # Obtener nombre del archivo para el diálogo
    nombre_archivo = os.path.basename(ruta_origen)
    
    # Abrir diálogo para elegir ubicación
    ruta_destino = filedialog.asksaveasfilename(
        title="Guardar archivo como",
        initialfile=nombre_archivo,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if not ruta_destino:
        return  # Usuario canceló
    
    try:
        # Copiar archivo
        shutil.copy2(ruta_origen, ruta_destino)
        messagebox.showinfo("Éxito", f"Archivo descargado en:\n{ruta_destino}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el archivo:\n{e}")


def descargar_expediente(ruta_pdf):
    """
    Descarga toda la carpeta del estudiante como un archivo .zip permitiendo elegir ubicación
    Args:
        ruta_pdf: Ruta de un PDF del estudiante
    """
    # La carpeta del estudiante es el directorio padre del PDF
    carpeta_estudiante = os.path.dirname(ruta_pdf)
    nombre_estudiante = os.path.basename(carpeta_estudiante)
    
    # Abrir diálogo para elegir carpeta de destino
    carpeta_destino = filedialog.askdirectory(
        title="Seleccionar carpeta para guardar el expediente"
    )
    
    if not carpeta_destino:
        return  # Usuario canceló
    
    try:
        # Crear nombre del archivo zip
        nombre_zip = f"Expediente_{nombre_estudiante}.zip"
        ruta_zip = os.path.join(carpeta_destino, nombre_zip)
        
        # Si ya existe, agregar número
        contador = 1
        while os.path.exists(ruta_zip):
            nombre_zip = f"Expediente_{nombre_estudiante}_{contador}.zip"
            ruta_zip = os.path.join(carpeta_destino, nombre_zip)
            contador += 1
        
        # Crear el archivo zip con todas las subcarpetas
        with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            archivos_agregados = 0
            
            # Recorrer recursivamente toda la carpeta del estudiante
            for carpeta_actual, subcarpetas, archivos in os.walk(carpeta_estudiante):
                for archivo in archivos:
                    ruta_completa = os.path.join(carpeta_actual, archivo)
                    # Calcular la ruta relativa para mantener la estructura de carpetas
                    ruta_relativa = os.path.relpath(ruta_completa, carpeta_estudiante)
                    # Agregar archivo al zip manteniendo la estructura de carpetas
                    zipf.write(ruta_completa, ruta_relativa)
                    archivos_agregados += 1
        
        if archivos_agregados > 0:
            messagebox.showinfo("Éxito", 
                f"Expediente descargado exitosamente:\n{ruta_zip}\n\n"
                f"Archivos incluidos: {archivos_agregados}")
        else:
            messagebox.showwarning("Carpeta vacía", 
                "La carpeta del estudiante no contiene archivos.")
            # Eliminar el zip vacío
            if os.path.exists(ruta_zip):
                os.remove(ruta_zip)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el expediente:\n{e}")


def descargar_expediente_multiple(rutas_documentos, progress_callback=None, root=None):
    """
    Descarga todos los documentos filtrados como un archivo .zip permitiendo elegir ubicación
    Args:
        rutas_documentos: Lista de rutas de documentos PDF
        progress_callback: Función opcional para reportar progreso (percentage, message)
        root: Ventana raíz de tkinter para actualizar UI desde el thread
    """
    if not rutas_documentos:
        if root:
            root.after(0, lambda: messagebox.showwarning("Sin documentos", "No hay documentos para descargar."))
        else:
            messagebox.showwarning("Sin documentos", "No hay documentos para descargar.")
        return
    
    # Abrir diálogo para elegir carpeta de destino
    carpeta_destino = filedialog.askdirectory(
        title="Seleccionar carpeta para guardar los documentos"
    )
    
    if not carpeta_destino:
        return  # Usuario canceló
    
    def worker():
        """Función que ejecuta el trabajo en un thread separado"""
        try:
            # Crear nombre del archivo zip
            nombre_zip = "Documentos_Filtrados.zip"
            ruta_zip = os.path.join(carpeta_destino, nombre_zip)
            
            # Si ya existe, agregar número
            contador = 1
            while os.path.exists(ruta_zip):
                nombre_zip = f"Documentos_Filtrados_{contador}.zip"
                ruta_zip = os.path.join(carpeta_destino, nombre_zip)
                contador += 1
            
            total_docs = len(rutas_documentos)
            
            # Crear el archivo zip con todos los documentos
            with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                archivos_agregados = 0
                
                # Agregar cada documento al ZIP
                for idx, ruta_doc in enumerate(rutas_documentos):
                    if os.path.exists(ruta_doc) and os.path.isfile(ruta_doc):
                        # Obtener nombre del archivo
                        nombre_archivo = os.path.basename(ruta_doc)
                        
                        # Si hay duplicados, agregar el nombre de la carpeta padre
                        carpeta_padre = os.path.basename(os.path.dirname(ruta_doc))
                        nombre_en_zip = f"{carpeta_padre}/{nombre_archivo}"
                        
                        # Agregar archivo al zip
                        zipf.write(ruta_doc, nombre_en_zip)
                        archivos_agregados += 1
                    
                    # Reportar progreso
                    if progress_callback:
                        percentage = int((idx + 1) / total_docs * 100)
                        message = f"Procesando {idx + 1} de {total_docs}..."
                        if root:
                            root.after(0, lambda p=percentage, m=message: progress_callback(p, m))
                        else:
                            progress_callback(percentage, message)
            
            # Mostrar resultado
            if archivos_agregados > 0:
                final_message = f"Documentos descargados exitosamente:\n{ruta_zip}\n\nArchivos incluidos: {archivos_agregados}"
                if root:
                    root.after(0, lambda: messagebox.showinfo("Éxito", final_message))
                else:
                    messagebox.showinfo("Éxito", final_message)
            else:
                final_message = "No se pudieron agregar archivos al ZIP."
                if root:
                    root.after(0, lambda: messagebox.showwarning("Sin archivos", final_message))
                else:
                    messagebox.showwarning("Sin archivos", final_message)
                # Eliminar el zip vacío
                if os.path.exists(ruta_zip):
                    os.remove(ruta_zip)
        
        except Exception as e:
            error_message = f"No se pudo crear el archivo ZIP:\n{e}"
            if root:
                root.after(0, lambda: messagebox.showerror("Error", error_message))
            else:
                messagebox.showerror("Error", error_message)
    
    # Iniciar el thread y retornar inmediatamente
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def sincronizar_drive(ruta_doctorados, ruta_doctorados2):
    """
    Sincroniza los documentos desde Google Drive
    Args:
        ruta_doctorados: Primera ruta de doctorados
        ruta_doctorados2: Segunda ruta de doctorados
    Returns:
        list: Lista de documentos cargados
    """
    if not ruta_doctorados and not ruta_doctorados2:
        messagebox.showinfo("Sincronización", 
                          "No se encontró ninguna ruta de doctorados. No hay documentos cargados.")
        return []
    
    documentos = []
    if ruta_doctorados:
        documentos.extend(cargar_documentos(ruta_doctorados))
    if ruta_doctorados2:
        documentos.extend(cargar_documentos(ruta_doctorados2))
    
    messagebox.showinfo("Sincronización", 
                       "¡Sincronización completada! Los documentos han sido actualizados.")
    return documentos
