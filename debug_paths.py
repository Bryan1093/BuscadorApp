import os
import string
def debug_rutas():
    print("Iniciando diagnóstico profundo...")
    
    drives = ['C:', 'D:', 'E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'S:', 'T:', 'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:']
    
    for drive in drives:
        path = f"{drive}\\"
        if os.path.exists(path):
            print(f"\n[DRIVE] Unidad detectada: {drive}")
            try:
                items = os.listdir(path)
                print(f"  Contenido raíz ({len(items)} items):")
                for item in items[:20]:  # Listar primeros 20
                    print(f"    - {item}")
                
                # Buscar específicamente "Mi unidad" o "My Drive"
                if "Mi unidad" in items:
                    print(f"  !!! ENCONTRADO 'Mi unidad' en {drive}")
                    subpath = os.path.join(path, "Mi unidad")
                    try:
                        subitems = os.listdir(subpath)
                        print(f"    Contenido de 'Mi unidad': {subitems}")
                    except Exception as e:
                        print(f"    Error leyendo 'Mi unidad': {e}")
                        
                if "My Drive" in items:
                    print(f"  !!! ENCONTRADO 'My Drive' en {drive}")
            except Exception as e:
                print(f"  Error listando raíz: {e}")
if __name__ == "__main__":
    debug_rutas()