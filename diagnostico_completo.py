"""
Script de diagnóstico completo para AppBuscador
Verifica rutas, carga de documentos y configuración
"""
import os
import sys

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.path_utils import encontrar_rutas_drive, obtener_todas_universidades_combinadas
from services.file_service import cargar_documentos, cargar_documentos_oficios
import config.settings as settings

print("=" * 70)
print("DIAGNÓSTICO COMPLETO DE APPBUSCADOR")
print("=" * 70)

# 1. Verificar rutas
print("\n1. INICIALIZANDO RUTAS DE DRIVE...")
print("-" * 70)
ruta_doctorados, ruta_oficios, ruta_doctorados2 = encontrar_rutas_drive()

print(f"   ruta_doctorados:  {ruta_doctorados if ruta_doctorados else '❌ None'}")
print(f"   ruta_oficios:     {ruta_oficios if ruta_oficios else '❌ None'}")
print(f"   ruta_doctorados2: {ruta_doctorados2 if ruta_doctorados2 else '❌ None'}")

# 2. Verificar que las rutas existen físicamente
print("\n2. VERIFICANDO EXISTENCIA FÍSICA DE RUTAS...")
print("-" * 70)
if ruta_doctorados:
    existe = os.path.exists(ruta_doctorados)
    print(f"   {'✓' if existe else '❌'} ruta_doctorados existe: {existe}")
    if existe:
        try:
            contenido = os.listdir(ruta_doctorados)
            print(f"      Carpetas encontradas: {len(contenido)}")
            print(f"      Primeras 5: {contenido[:5]}")
        except Exception as e:
            print(f"      ❌ Error al listar: {e}")

if ruta_doctorados2:
    existe = os.path.exists(ruta_doctorados2)
    print(f"   {'✓' if existe else '❌'} ruta_doctorados2 existe: {existe}")
    if existe:
        try:
            contenido = os.listdir(ruta_doctorados2)
            print(f"      Carpetas encontradas: {len(contenido)}")
            print(f"      Primeras 5: {contenido[:5]}")
        except Exception as e:
            print(f"      ❌ Error al listar: {e}")

if ruta_oficios:
    existe = os.path.exists(ruta_oficios)
    print(f"   {'✓' if existe else '❌'} ruta_oficios existe: {existe}")
else:
    print(f"   ⚠ ruta_oficios no configurada")

# 3. Cargar documentos
print("\n3. CARGANDO DOCUMENTOS...")
print("-" * 70)
documentos = []

if ruta_doctorados:
    print(f"   Cargando desde ruta_doctorados...")
    docs1 = cargar_documentos(ruta_doctorados)
    print(f"   ✓ Documentos cargados: {len(docs1)}")
    documentos.extend(docs1)
    if docs1:
        print(f"      Ejemplo: {docs1[0]}")

if ruta_doctorados2:
    print(f"   Cargando desde ruta_doctorados2...")
    docs2 = cargar_documentos(ruta_doctorados2)
    print(f"   ✓ Documentos cargados: {len(docs2)}")
    documentos.extend(docs2)
    if docs2:
        print(f"      Ejemplo: {docs2[0]}")

print(f"\n   TOTAL DOCUMENTOS CARGADOS: {len(documentos)}")

# 4. Verificar universidades
print("\n4. OBTENIENDO UNIVERSIDADES...")
print("-" * 70)
universidades = obtener_todas_universidades_combinadas(ruta_doctorados, ruta_doctorados2)
print(f"   Total universidades: {len(universidades)}")
if universidades:
    print(f"   Primeras 5: {universidades[:5]}")

# 5. Simular inicialización de settings
print("\n5. SIMULANDO INICIALIZACIÓN DE SETTINGS...")
print("-" * 70)
settings.ruta_doctorados = ruta_doctorados
settings.ruta_oficios = ruta_oficios
settings.ruta_doctorados2 = ruta_doctorados2
settings.documentos_drive = documentos
settings.universidades_lista = universidades

print(f"   settings.ruta_doctorados: {settings.ruta_doctorados}")
print(f"   settings.ruta_doctorados2: {settings.ruta_doctorados2}")
print(f"   settings.documentos_drive: {len(settings.documentos_drive)} documentos")
print(f"   settings.universidades_lista: {len(settings.universidades_lista)} universidades")

# 6. Probar búsqueda
print("\n6. PROBANDO BÚSQUEDA...")
print("-" * 70)
if documentos:
    from services.search_service import buscar_documentos
    
    # Buscar todos
    resultados = buscar_documentos('(Todos)', '(Todos)', '(Todos)', '', '(Todos)')
    print(f"   Búsqueda '(Todos)': {len(resultados)} resultados")
    
    # Buscar por primera universidad
    if universidades:
        primera_uni = universidades[0]
        resultados = buscar_documentos(primera_uni, '(Todos)', '(Todos)', '', '(Todos)')
        print(f"   Búsqueda '{primera_uni}': {len(resultados)} resultados")
else:
    print("   ⚠ No hay documentos para probar búsqueda")

# 7. Resumen
print("\n" + "=" * 70)
print("RESUMEN DEL DIAGNÓSTICO")
print("=" * 70)
print(f"✓ Rutas encontradas: {sum([bool(ruta_doctorados), bool(ruta_doctorados2), bool(ruta_oficios)])}/3")
print(f"✓ Documentos cargados: {len(documentos)}")
print(f"✓ Universidades encontradas: {len(universidades)}")

if len(documentos) == 0:
    print("\n⚠ PROBLEMA DETECTADO: No se cargaron documentos")
    print("   Posibles causas:")
    print("   - Las rutas no contienen archivos PDF")
    print("   - Hay un error en la función cargar_documentos()")
    print("   - Los permisos de las carpetas no permiten lectura")
else:
    print("\n✓ TODO PARECE ESTAR FUNCIONANDO CORRECTAMENTE")

print("=" * 70)
