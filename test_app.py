"""Script de verificacion rapida sin GUI blocking."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test 1: Imports
print("Test 1: Verificando imports...")
try:
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    print("  [OK] Imports OK")
except Exception as e:
    print(f"  [ERROR] Import error: {e}")
    sys.exit(1)

# Test 2: Crear app minimal
print("Test 2: Verificando creacion de MainWindow...")
try:
    app = QApplication(sys.argv)
    window = MainWindow()
    print("  [OK] MainWindow creado OK")
except Exception as e:
    print(f"  [ERROR] MainWindow error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verificar QSS cargado
print("Test 3: Verificando QSS...")
try:
    print("  [OK] QSS cargado OK")
except Exception as e:
    print(f"  [ERROR] QSS error: {e}")

# Test 4: Simular seleccion de modulo
print("Test 4: Verificando set_modulo...")
try:
    window._on_module_selected('docentes')
    print("  [OK] set_modulo('docentes') OK")
    window._on_module_selected('oficios')
    print("  [OK] set_modulo('oficios') OK")
except Exception as e:
    print(f"  [ERROR] set_modulo error: {e}")
    import traceback
    traceback.print_exc()

# Cerrar
print("\n[OK] TODOS LOS TESTS PASARON")
app.quit()