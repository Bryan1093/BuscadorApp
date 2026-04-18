"""
Script de diagnóstico para verificar las rutas de Google Drive
"""
import os
import string
from utils.path_utils import encontrar_rutas_drive

def diagnostico_completo():
    print("=" * 80)
    print("DIAGNÓSTICO DE RUTAS - AppBuscador")
    print("=" * 80)
    
    # 1. Verificar qué unidades están disponibles
    print("\n[1] UNIDADES DISPONIBLES:")
    print("-" * 80)
    unidades_disponibles = []
    for letra in string.ascii_uppercase:
        ruta = f"{letra}:\\"
        if os.path.exists(ruta):
            unidades_disponibles.append(letra)
            print(f"  ✓ Unidad {letra}: encontrada")
    
    if not unidades_disponibles:
        print("  ✗ No se encontraron unidades")
        return
    
    # 2. Buscar "Mi unidad" en cada unidad disponible
    print("\n[2] BUSCANDO 'Mi unidad' EN CADA UNIDAD:")
    print("-" * 80)
    rutas_mi_unidad = []
    for letra in unidades_disponibles:
        ruta = f"{letra}:\\"
        try:
            contenido = os.listdir(ruta)
            if "Mi unidad" in contenido:
                ruta_mi_unidad = os.path.join(ruta, "Mi unidad")
                rutas_mi_unidad.append((letra, ruta_mi_unidad))
                print(f"  ✓ Unidad {letra}: 'Mi unidad' ENCONTRADA en {ruta_mi_unidad}")
                
                # Listar contenido de "Mi unidad"
                try:
                    contenido_mi_unidad = os.listdir(ruta_mi_unidad)
                    print(f"    Contenido de 'Mi unidad': {contenido_mi_unidad[:10]}")
                except Exception as e:
                    print(f"    Error al listar contenido: {e}")
            else:
                print(f"  ✗ Unidad {letra}: 'Mi unidad' NO encontrada")
        except Exception as e:
            print(f"  ✗ Unidad {letra}: Error al acceder - {e}")
    
    # 3. Verificar rutas específicas que busca la app
    print("\n[3] VERIFICANDO RUTAS ESPECÍFICAS:")
    print("-" * 80)
    
    rutas_a_verificar = [
        ("Doctorados DB_General", "Mi unidad\\Doctorados\\DB_General\\Universidad"),
        ("Doctorados DB_General2", "Mi unidad\\Doctorados\\DB_General2\\Universidad"),
        ("Oficios", "Mi unidad\\Oficios\\DB_GeneralOficios")
    ]
    
    for nombre, ruta_relativa in rutas_a_verificar:
        print(f"\n  Buscando: {nombre}")
        encontrada = False
        for letra in unidades_disponibles:
            ruta_completa = f"{letra}:\\{ruta_relativa}"
            if os.path.exists(ruta_completa):
                print(f"    ✓ ENCONTRADA en {ruta_completa}")
                encontrada = True
                # Listar contenido
                try:
                    contenido = os.listdir(ruta_completa)
                    print(f"      Contiene {len(contenido)} elementos")
                    if contenido:
                        print(f"      Primeros elementos: {contenido[:5]}")
                except Exception as e:
                    print(f"      Error al listar: {e}")
                break
        
        if not encontrada:
            print(f"    ✗ NO ENCONTRADA en ninguna unidad")
    
    # 4. Ejecutar la función de la app
    print("\n[4] RESULTADO DE encontrar_rutas_drive():")
    print("-" * 80)
    ruta_doctorados, ruta_oficios, ruta_doctorados2 = encontrar_rutas_drive()
    
    print(f"  ruta_doctorados:  {ruta_doctorados if ruta_doctorados else '❌ None (NO ENCONTRADA)'}")
    print(f"  ruta_oficios:     {ruta_oficios if ruta_oficios else '❌ None (NO ENCONTRADA)'}")
    print(f"  ruta_doctorados2: {ruta_doctorados2 if ruta_doctorados2 else '❌ None (NO ENCONTRADA)'}")
    
    # 5. Verificar si hay archivos PDF
    print("\n[5] VERIFICANDO ARCHIVOS PDF:")
    print("-" * 80)
    
    rutas_validas = [
        ("Doctorados", ruta_doctorados),
        ("Doctorados2", ruta_doctorados2),
        ("Oficios", ruta_oficios)
    ]
    
    for nombre, ruta in rutas_validas:
        if ruta and os.path.exists(ruta):
            print(f"\n  {nombre} ({ruta}):")
            contador_pdf = 0
            try:
                for root, dirs, files in os.walk(ruta):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            contador_pdf += 1
                            if contador_pdf <= 3:  # Mostrar solo los primeros 3
                                print(f"    - {os.path.join(root, file)}")
                
                print(f"    Total PDFs encontrados: {contador_pdf}")
            except Exception as e:
                print(f"    Error al buscar PDFs: {e}")
        else:
            print(f"\n  {nombre}: Ruta no disponible")
    
    # 6. Recomendaciones
    print("\n" + "=" * 80)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 80)
    
    if not ruta_doctorados and not ruta_doctorados2 and not ruta_oficios:
        print("\n⚠️  PROBLEMA DETECTADO:")
        print("   No se encontraron ninguna de las rutas esperadas.")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica que Google Drive esté sincronizado")
        print("   2. Verifica que las carpetas existan en Google Drive")
        print("   3. Verifica que la estructura de carpetas sea correcta")
        if rutas_mi_unidad:
            print(f"\n   'Mi unidad' se encontró en: {[r[1] for r in rutas_mi_unidad]}")
            print("   Verifica que dentro de 'Mi unidad' existan las carpetas:")
            print("   - Doctorados\\DB_General\\Universidad")
            print("   - Doctorados\\DB_General2\\Universidad")
            print("   - Oficios\\DB_GeneralOficios")
    else:
        print("\n✓ Al menos una ruta fue encontrada correctamente")

if __name__ == "__main__":
    diagnostico_completo()
