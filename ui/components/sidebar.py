"""
Sidebar de filtros para BuscadorApp.

Proporciona una interfaz de filtrado dual:
- Modo "docentes": filtros en cascada (Universidad → Programa → Estudiante)
- Modo "oficios": filtros simples (Año, Tipo de Oficio)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel
from PySide6.QtCore import Signal

from core.proxy_model import DocumentProxyModel
from core.controller import DriveController


class FiltersSidebar(QWidget):
    """
    Widget de sidebar para filtrado de documentos.

    Soporta dos modos de funcionamiento:
    - "docentes": filtros en cascada por Universidad → Programa → Estudiante
    - "oficios": filtros simples por Año → Tipo de Oficio
    
    Los cambios en un nivel superior limpian los niveles inferiores.
    """

    filter_changed = Signal(dict)

    def __init__(self, proxy_model: DocumentProxyModel, controller: DriveController, parent=None):
        super().__init__(parent)

        # Guardar referencias
        self._proxy_model = proxy_model
        self._controller = controller
        self._modo = "docentes"  # Modo por defecto

        # Crear UI
        self._setup_ui()

        # Conectar señales
        self._connect_signals()

        # Poblar combos iniciales según el modo
        if self._modo == "docentes":
            self._populate_universidades()
        else:
            self._populate_oficios()

        # Actualizar estado de combos según carga
        self._update_combos_enabled(self._controller.is_loaded)

    def _setup_ui(self):
        """Configura el layout y widgets de la interfaz."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Título principal
        self._label_titulo = QLabel("Filtros")
        font_titulo = self._label_titulo.font()
        font_titulo.setBold(True)
        font_titulo.setPointSize(12)
        self._label_titulo.setFont(font_titulo)
        layout.addWidget(self._label_titulo)

        # ==== WIDGETS MODO DOCENTES ====
        # Combo Universidad
        self._label_universidad = QLabel("Universidad:")
        font_label = self._label_universidad.font()
        font_label.setPointSize(11)
        self._label_universidad.setFont(font_label)
        layout.addWidget(self._label_universidad)

        self._combo_universidad = QComboBox()
        self._combo_universidad.setEditable(True)
        self._combo_universidad.setCurrentIndex(-1)
        layout.addWidget(self._combo_universidad)

        # Combo Programa
        self._label_programa = QLabel("Programa:")
        self._label_programa.setFont(font_label)
        layout.addWidget(self._label_programa)

        self._combo_programa = QComboBox()
        self._combo_programa.setEditable(True)
        self._combo_programa.setCurrentIndex(-1)
        layout.addWidget(self._combo_programa)

        # Combo Estudiante
        self._label_estudiante = QLabel("Estudiante:")
        self._label_estudiante.setFont(font_label)
        layout.addWidget(self._label_estudiante)

        self._combo_estudiante = QComboBox()
        self._combo_estudiante.setEditable(True)
        self._combo_estudiante.setCurrentIndex(-1)
        layout.addWidget(self._combo_estudiante)

        # ==== WIDGETS MODO OFICIOS ====
        # Combo Año (para oficios)
        self._label_ano = QLabel("Año:")
        self._label_ano.setFont(font_label)
        self._label_ano.setVisible(False)
        layout.addWidget(self._label_ano)

        self._combo_ano = QComboBox()
        self._combo_ano.setEditable(True)
        self._combo_ano.setCurrentIndex(-1)
        self._combo_ano.setVisible(False)
        layout.addWidget(self._combo_ano)

        # Combo Tipo de Oficio (para oficios)
        self._label_tipo_oficio = QLabel("Tipo de Oficio:")
        self._label_tipo_oficio.setFont(font_label)
        self._label_tipo_oficio.setVisible(False)
        layout.addWidget(self._label_tipo_oficio)

        self._combo_tipo_oficio = QComboBox()
        self._combo_tipo_oficio.setEditable(True)
        self._combo_tipo_oficio.setCurrentIndex(-1)
        self._combo_tipo_oficio.setVisible(False)
        layout.addWidget(self._combo_tipo_oficio)

        # Espaciador vertical
        layout.addStretch()

        # Botón limpiar filtros
        self._btn_limpiar = QPushButton("Limpiar Filtros")
        layout.addWidget(self._btn_limpiar)

    def _connect_signals(self):
        """Conecta las señales del controller y los combos."""
        # Señales del controller
        self._controller.signals.load_completed.connect(self._on_load_completed)

        # Señales de los combos (modo docentes)
        self._combo_universidad.currentTextChanged.connect(self._on_universidad_changed)
        self._combo_programa.currentTextChanged.connect(self._on_programa_changed)
        self._combo_estudiante.currentTextChanged.connect(self._on_estudiante_changed)

        # Señales de los combos (modo oficios)
        self._combo_ano.currentTextChanged.connect(self._on_ano_changed)
        self._combo_tipo_oficio.currentTextChanged.connect(self._on_tipo_oficio_changed)

        # Botón limpiar
        self._btn_limpiar.clicked.connect(self._on_limpiar_clicked)

    # ============ MÉTODOS DE POPULATE (DOCENTES) ============

    def _populate_universidades(self):
        """Pobla el combo de universidades."""
        universidades = self._controller.get_universidades()
        universidades.insert(0, "(Todos)")

        self._combo_universidad.blockSignals(True)
        self._combo_universidad.clear()
        self._combo_universidad.addItems(universidades)
        self._combo_universidad.setCurrentIndex(0)
        self._combo_universidad.blockSignals(False)

    def _populate_programas(self, universidad: str):
        """
        Puebla el combo de programas según la universidad seleccionada.

        Args:
            universidad: Nombre de la universidad (o "(Todos)")
        """
        # Traducir "(Todos)" para el controller
        filtro_u = "" if universidad == "(Todos)" else universidad
        programas = self._controller.get_programas(filtro_u)
        programas.insert(0, "(Todos)")

        self._combo_programa.blockSignals(True)
        self._combo_programa.clear()
        self._combo_programa.addItems(programas)
        self._combo_programa.setCurrentIndex(0)
        self._combo_programa.blockSignals(False)

    def _populate_estudiantes(self):
        """
        Puebla el combo de estudiantes según universidad y programa seleccionados.
        """
        universidad = self._combo_universidad.currentText()
        programa = self._combo_programa.currentText()

        # Traducir "(Todos)" para el controller
        filtro_u = "" if universidad == "(Todos)" else universidad
        filtro_p = "" if programa == "(Todos)" else programa

        estudiantes = self._controller.get_estudiantes(filtro_u, filtro_p)
        estudiantes.insert(0, "(Todos)")

        self._combo_estudiante.blockSignals(True)
        self._combo_estudiante.clear()
        self._combo_estudiante.addItems(estudiantes)
        self._combo_estudiante.setCurrentIndex(0)
        self._combo_estudiante.blockSignals(False)

    def _on_load_completed(self, documentos):
        """
        Handler cuando se completan de cargar los documentos.
        Puebla los combos y habilita la interfaz según el modo.
        """
        if self._modo == "docentes":
            self._populate_universidades()
        else:
            self._populate_oficios()
        self._update_combos_enabled(True)

    def _update_combos_enabled(self, enabled: bool):
        """
        Habilita o deshabilita los combos según el estado de carga.

        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        if self._modo == "docentes":
            self._combo_universidad.setEnabled(enabled)
            self._combo_programa.setEnabled(enabled)
            self._combo_estudiante.setEnabled(enabled)
        else:
            self._combo_ano.setEnabled(enabled)
            self._combo_tipo_oficio.setEnabled(enabled)

    def _on_universidad_changed(self, texto: str):
        """
        Handler cuando cambia la universidad seleccionada.
        Limpia programa y estudiante, y actualiza el proxy.
        """
        # Limpiar programas y estudiantes (con blockSignals para evitar loops)
        self._combo_programa.blockSignals(True)
        self._combo_programa.clear()
        self._combo_programa.addItem("(Todos)")
        self._combo_programa.setCurrentIndex(0)
        self._combo_programa.blockSignals(False)

        self._combo_estudiante.blockSignals(True)
        self._combo_estudiante.clear()
        self._combo_estudiante.addItem("(Todos)")
        self._combo_estudiante.setCurrentIndex(0)
        self._combo_estudiante.blockSignals(False)

        # Poblar programas
        self._populate_programas(texto)

        # Traducir y asignar al proxy
        valor = "" if texto == "(Todos)" else texto
        self._proxy_model.filter_universidad = valor

        # Emitir señal
        self._emit_filter_changed()

    def _on_programa_changed(self, texto: str):
        """
        Handler cuando cambia el programa seleccionado.
        Limpia estudiantes y actualiza el proxy.
        """
        # Limpiar estudiantes
        self._combo_estudiante.blockSignals(True)
        self._combo_estudiante.clear()
        self._combo_estudiante.addItem("(Todos)")
        self._combo_estudiante.setCurrentIndex(0)
        self._combo_estudiante.blockSignals(False)

        # Poblar estudiantes
        self._populate_estudiantes()

        # Traducir y asignar al proxy
        valor = "" if texto == "(Todos)" else texto
        self._proxy_model.filter_programa = valor

        # Emitir señal
        self._emit_filter_changed()

    def _on_estudiante_changed(self, texto: str):
        """
        Handler cuando cambia el estudiante seleccionado.
        Actualiza el proxy.
        """
        # Traducir y asignar al proxy
        valor = "" if texto == "(Todos)" else texto
        self._proxy_model.filter_estudiante = valor

        # Emitir señal
        self._emit_filter_changed()

    # ============ HANDLERS (OFICIOS) ============

    def _populate_oficios(self):
        """Pobla los combos de oficios (año y tipo)."""
        # Obtener años únicos de los documentos de oficios
        anos = self._controller.get_anios_oficios()
        anos.insert(0, "(Todos)")

        self._combo_ano.blockSignals(True)
        self._combo_ano.clear()
        self._combo_ano.addItems(anos)
        self._combo_ano.setCurrentIndex(0)
        self._combo_ano.blockSignals(False)

        # Obtener tipos de oficio único
        tipos = self._controller.get_tipos_oficio()
        tipos.insert(0, "(Todos)")

        self._combo_tipo_oficio.blockSignals(True)
        self._combo_tipo_oficio.clear()
        self._combo_tipo_oficio.addItems(tipos)
        self._combo_tipo_oficio.setCurrentIndex(0)
        self._combo_tipo_oficio.blockSignals(False)

    def _on_ano_changed(self, texto: str):
        """
        Handler cuando cambia el año seleccionado.
        Actualiza el proxy.
        """
        # Traducir y asignar al proxy
        valor = "" if texto == "(Todos)" else texto
        self._proxy_model.filter_ano = valor

        # Emitir señal
        self._emit_filter_changed()

    def _on_tipo_oficio_changed(self, texto: str):
        """
        Handler cuando cambia el tipo de oficio seleccionado.
        Actualiza el proxy.
        """
        # Traducir y asignar al proxy
        valor = "" if texto == "(Todos)" else texto
        self._proxy_model.filter_tipo_oficio = valor

        # Emitir señal
        self._emit_filter_changed()

    def _on_limpiar_clicked(self):
        """Handler cuando se presiona el botón de limpiar filtros."""
        # Limpiar filtros del proxy
        self._proxy_model.clear_filters()

        # Resetear combos según el modo
        if self._modo == "docentes":
            self._combo_universidad.blockSignals(True)
            self._combo_universidad.setCurrentIndex(0)
            self._combo_universidad.blockSignals(False)

            self._combo_programa.blockSignals(True)
            self._combo_programa.clear()
            self._combo_programa.addItem("(Todos)")
            self._combo_programa.setCurrentIndex(0)
            self._combo_programa.blockSignals(False)

            self._combo_estudiante.blockSignals(True)
            self._combo_estudiante.clear()
            self._combo_estudiante.addItem("(Todos)")
            self._combo_estudiante.setCurrentIndex(0)
            self._combo_estudiante.blockSignals(False)
        else:
            self._combo_ano.blockSignals(True)
            self._combo_ano.setCurrentIndex(0)
            self._combo_ano.blockSignals(False)

            self._combo_tipo_oficio.blockSignals(True)
            self._combo_tipo_oficio.setCurrentIndex(0)
            self._combo_tipo_oficio.blockSignals(False)

        # Emitir señal con filtros vacíos
        self._emit_filter_changed()

    def _emit_filter_changed(self):
        """Emite la señal filter_changed con los valores actuales."""
        filters = {
            "filter_universidad": self._proxy_model.filter_universidad,
            "filter_programa": self._proxy_model.filter_programa,
            "filter_estudiante": self._proxy_model.filter_estudiante,
            "filter_tipo": self._proxy_model.filter_tipo,
            "filter_ano": self._proxy_model.filter_ano,
            "filter_tipo_oficio": self._proxy_model.filter_tipo_oficio,
        }
        self.filter_changed.emit(filters)

    # ==================== APIS PÚBLICAS ====================

    def set_modo(self, modo: str):
        """
        Cambia el modo de funcionamiento del sidebar.

        Args:
            modo: "docentes" o "oficios"
        """
        self._modo = modo
        self._update_widgets_visibility()

        # Poblar los combos según el modo si los datos ya están cargados
        if self._controller.is_loaded:
            if modo == "docentes":
                self._populate_universidades()
            else:
                self._populate_oficios()

    def _update_widgets_visibility(self):
        """Actualiza la visibilidad de los widgets según el modo."""
        if self._modo == "docentes":
            # Mostrar widgets de docentes
            self._label_universidad.setVisible(True)
            self._combo_universidad.setVisible(True)
            self._label_programa.setVisible(True)
            self._combo_programa.setVisible(True)
            self._label_estudiante.setVisible(True)
            self._combo_estudiante.setVisible(True)

            # Ocultar widgets de oficios
            self._label_ano.setVisible(False)
            self._combo_ano.setVisible(False)
            self._label_tipo_oficio.setVisible(False)
            self._combo_tipo_oficio.setVisible(False)
        else:
            # Ocultar widgets de docentes
            self._label_universidad.setVisible(False)
            self._combo_universidad.setVisible(False)
            self._label_programa.setVisible(False)
            self._combo_programa.setVisible(False)
            self._label_estudiante.setVisible(False)
            self._combo_estudiante.setVisible(False)

            # Mostrar widgets de oficios
            self._label_ano.setVisible(True)
            self._combo_ano.setVisible(True)
            self._label_tipo_oficio.setVisible(True)
            self._combo_tipo_oficio.setVisible(True)
