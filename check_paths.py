import os
import string
from utils.path_utils import encontrar_rutas_drive

print("="*60)
print("DIAGNOSTICO DE RUTAS")
print("="*60)

# Verificar que unidades existen
print("\n1. Unidades disponibles:")
for letra in ["C", "D", "E", "F", "G", "H"]:
    if os.path.exists(f"{letra}:\\"):
        print(f"   [{letra}:] Disponible")

# Buscar Mi unidad
print("\n2. Buscando 'Mi unidad':")
for letra in string.ascii_uppercase:
    ruta = f"{letra}:\\"
    if os.path.exists(ruta):
        try:
            if "Mi unidad" in os.listdir(ruta):
                print(f"   ENCONTRADA en {letra}:\\Mi unidad")
                mi_unidad_path = f"{letra}:\\Mi unidad"
                contenido = os.listdir(mi_unidad_path)
                print(f"   Carpetas dentro: {contenido}")
        except:
            pass

# Verificar rutas especificas
print("\n3. Verificando rutas especificas:")
rutas = {
    "DB_General": "Mi unidad\\Doctorados\\DB_General\\Universidad",
    "DB_General2": "Mi unidad\\Doctorados\\DB_General2\\Universidad",
    "Oficios": "Mi unidad\\Oficios\\DB_GeneralOficios"
}

for nombre, ruta_rel in rutas.items():
    encontrada = False
    for letra in string.ascii_uppercase:
        ruta_completa = f"{letra}:\\{ruta_rel}"
        if os.path.exists(ruta_completa):
            print(f"   [{nombre}] SI existe en: {ruta_completa}")
            encontrada = True
            break
    if not encontrada:
        print(f"   [{nombre}] NO existe")

# Ejecutar funcion de la app
print("\n4. Resultado de encontrar_rutas_drive():")
r1, r2, r3 = encontrar_rutas_drive()
print(f"   ruta_doctorados:  {r1 if r1 else 'None'}")
print(f"   ruta_oficios:     {r2 if r2 else 'None'}")
print(f"   ruta_doctorados2: {r3 if r3 else 'None'}")

print("\n" + "="*60)
