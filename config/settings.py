"""
Configuración global de la aplicación
Contiene constantes, rutas y variables de estado global
"""

# Variables globales de estado
documentos_drive = []
ruta_por_iid = {}
nombre_usuario_actual = ""

# Variables globales de UI
logo_img_global = None
login_logo_img_global = None

# Rutas de Drive (se inicializan al arrancar)
ruta_doctorados = None
ruta_oficios = None
ruta_doctorados2 = None

# Diccionario de items clave para clasificación de documentos
items_clave = {
    "1. Hoja de Vida": ["h.vida"],
    "2. Contrato de Beca": ["c.beca"],
    "3. Contrato de Licencia": ["c.licencia"],
    "4. Aval de Facultad": ["avalfacultad"],
    "5. Acción Personal": ["acciónpersonal"],
    "6. Datos del Garante": ["d.garante"],
    "7. Cédula y Papeleta de Votación": ["cédulaypapeleta"],
    "8. Pasaporte": ["pasaporte"],
    "9. Declaración Juramentada": ["declaraciónjuramentada"],
    "10. Solicitud de Pedido al Rectorado": ["solicitudpedidorectorado"],
    "11. Carta de Admisión de la Universidad": ["cartaadmisiónuniversidad"],
    "12. Certificado de Cuenta Bancaria": ["certificadobancario"],
    "13. Matrícula": ["matrícula"],
    "14. Certificado de Aprobación Tesis": ["certificadoaprobación"],
    "15. Reporte de Notas Semestrales": ["reportenotas"],
    "16. Línea de Investigación y Plan de Tesis": ["lineamientoinvestigacióntesis"],
    "17. Informe de Avance de Tesis Emitido por el Tutor": ["informeavance"],
    "18. Correspondencia": ["correspondencia"],
    "19. Registro de Títulos SENESCYT": ["registrosenescyt"],
    "20. Adenda": ["adenda"],
    "21. Oficios": ["oficio"],
    "22. Contrato IECE": ["c.iece"],
    "23. Contrato Senescyt": ["c.senescyt"],
    "24. Acta Finiquito": ["a.finiquito"],
    "25. Contrato apoyo financiero": ["c.apoyofinanciero"],
    "26. Contrato reducción carga horaria": ["c.reduccionhoraria"],
    "27. Documentos Precontractuales": ["DocumentosPrecontractuales"],
    "28. Extensión de Beca": ["extensionbeca"]
}

# Variables globales para oficios
estructura_oficios = None
documentos_oficios = []
ruta_por_iid_oficios = {}

# Flags para evitar recargas innecesarias de documentos
documentos_cargados = False
oficios_cargados = False

# Lista de universidades
universidades_lista = []
