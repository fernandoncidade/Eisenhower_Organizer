from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QDateEdit, QTimeEdit, QCheckBox,
                               QFileDialog, QLineEdit, QComboBox, QCalendarWidget, QApplication)
from PySide6.QtGui import QDesktopServices, QColor, QPalette
from PySide6.QtCore import QCoreApplication, Qt, QDate, QTime, QUrl, QLocale
from source.InterfaceCore.incore_01_initUI import FileDropLineEdit
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _compute_widget_height(app, widget, name: str | None = None) -> int:
    try:
        if hasattr(app, "widget_heights") and isinstance(app.widget_heights, dict) and name in app.widget_heights:
            v = int(app.widget_heights.get(name) or 0)
            if v > 0:
                return v

        if hasattr(app, "widget_height_override") and isinstance(app.widget_height_override, int) and app.widget_height_override > 0:
            return int(app.widget_height_override)

        fm = widget.fontMetrics()
        return max(26, int(fm.height() * 1.2))

    except Exception:
        return 28

def _apply_widget_min_height(app, widget, name: str | None = None):
    try:
        h = _compute_widget_height(app, widget, name)
        widget.setMinimumHeight(h)

    except Exception:
        pass

def _effective_locale(app) -> QLocale:
    try:
        if hasattr(app, "date_input") and app.date_input is not None:
            return app.date_input.locale()

    except Exception:
        pass

    try:
        if hasattr(app, "gerenciador_traducao"):
            idioma = app.gerenciador_traducao.obter_idioma_atual()
            if idioma and idioma.startswith("pt"):
                return QLocale(QLocale.Portuguese, QLocale.Brazil)

            if idioma and idioma.startswith("en"):
                return QLocale(QLocale.English, QLocale.UnitedStates)

    except Exception:
        pass

    return QLocale.system()

def _apply_locale_to_dateedit(app, de: QDateEdit):
    try:
        loc = _effective_locale(app)
        de.setLocale(loc)
        cw = de.calendarWidget()

        if cw is None:
            cw = QCalendarWidget(de)
            de.setCalendarWidget(cw)

        cw.setLocale(loc)

        try:
            qt_app = QApplication.instance()
            if qt_app is not None:
                window_color = qt_app.palette().color(QPalette.Window)

                def _is_light_color(col: QColor) -> bool:
                    try:
                        r, g, b = col.red(), col.green(), col.blue()
                        lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
                        return lum >= 0.85

                    except Exception:
                        return True

                if True:
                    fill_color = QColor(window_color)

                pal = de.palette()
                pal.setColor(QPalette.Base, fill_color)
                pal.setColor(QPalette.AlternateBase, fill_color)
                de.setPalette(pal)

                try:
                    cw_pal = cw.palette()
                    cw_pal.setColor(QPalette.Base, fill_color)
                    cw_pal.setColor(QPalette.AlternateBase, fill_color)
                    cw.setPalette(cw_pal)

                except Exception:
                    pass

        except Exception:
            pass

        cw.update()
        de.update()

    except Exception as e:
        logger.debug(f"Falha ao aplicar locale no calendário do QDateEdit: {e}", exc_info=True)


class EditTaskDialog(QDialog):
    def __init__(self, app, parent=None, initial_text="", initial_file="", initial_description="", initial_date_iso=None, initial_time_str=None, initial_priority=None):
        super().__init__(parent or app)
        self._app = app
        self.setModal(True)
        self.setWindowTitle(_get_text("✏️ Editar Tarefa") or "✏️ Editar Tarefa")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(_get_text("Tarefa:")))
        self.title = QLineEdit(self)
        self.title.setText(initial_text or "")
        layout.addWidget(self.title)

        layout.addWidget(QLabel(_get_text("Arquivo vinculado (arraste ou escolha):")))
        hl = QHBoxLayout()
        self.file_field = FileDropLineEdit(self._app, self)
        self.file_field.setText(initial_file and (initial_file.split("\\")[-1] or initial_file) or "")
        self.file_field.setToolTip(initial_file or "")
        hl.addWidget(self.file_field)
        btn_choose = QPushButton(_get_text("Escolher..."))

        btn_open = QPushButton(_get_text("Abrir"))
        btn_open.setEnabled(bool(initial_file))

        def _open_linked():
            fp = self.file_field.toolTip() or ""

            if not fp:
                return

            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(fp))

            except Exception:
                try:
                    import os, subprocess, sys

                    if sys.platform.startswith("win"):
                        os.startfile(fp)

                    elif sys.platform.startswith("darwin"):
                        subprocess.Popen(["open", fp])

                    else:
                        subprocess.Popen(["xdg-open", fp])

                except Exception as e:
                    logger.error(f"Falha ao abrir arquivo vinculado: {e}", exc_info=True)

        def _choose():
            try:
                path, _ = QFileDialog.getOpenFileName(self, _get_text("Escolher arquivo"), "", "*")
                if path:
                    self.file_field.setText(path.split("\\")[-1])
                    self.file_field.setToolTip(path)
                    btn_open.setEnabled(True)

            except Exception:
                pass

        btn_choose.clicked.connect(_choose)
        btn_clear = QPushButton(_get_text("Remover"))

        def _clear():
            try:
                self.file_field.clear()
                self.file_field.setToolTip("")
                btn_open.setEnabled(False)

            except Exception:
                pass

        btn_open.clicked.connect(_open_linked)
        btn_clear.clicked.connect(_clear)
        hl.addWidget(btn_choose)
        hl.addWidget(btn_open)
        hl.addWidget(btn_clear)
        layout.addLayout(hl)

        layout.addWidget(QLabel(_get_text("Data e horário (opcional):")))
        row_date = QHBoxLayout()
        self.date_enabled = QCheckBox(_get_text("Vincular data"), self)
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat(self._app.date_input.displayFormat() if hasattr(self._app, "date_input") else "dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())
        _apply_widget_min_height(self._app, self.date_edit, "dialog_date_edit")
        _apply_locale_to_dateedit(self._app, self.date_edit)

        if initial_date_iso:
            qd = QDate.fromString(initial_date_iso, Qt.ISODate)
            if qd.isValid():
                self.date_enabled.setChecked(True)
                self.date_edit.setDate(qd)

            else:
                self.date_enabled.setChecked(False)

        else:
            self.date_enabled.setChecked(False)

        self.date_edit.setEnabled(self.date_enabled.isChecked())
        self.date_enabled.toggled.connect(self.date_edit.setEnabled)

        row_date.addWidget(self.date_enabled)
        row_date.addWidget(self.date_edit)
        layout.addLayout(row_date)

        row_time = QHBoxLayout()
        self.time_enabled = QCheckBox(_get_text("Vincular horário"), self)
        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        _apply_widget_min_height(self._app, self.time_edit, "dialog_time_edit")

        if initial_time_str:
            qt = QTime.fromString(initial_time_str, "HH:mm")
            if qt.isValid():
                self.time_enabled.setChecked(True)
                self.time_edit.setTime(qt)

            else:
                self.time_enabled.setChecked(False)

        else:
            self.time_enabled.setChecked(False)

        def _sync_time_enabled():
            self.time_edit.setEnabled(self.date_enabled.isChecked() and self.time_enabled.isChecked())

        self.time_enabled.toggled.connect(lambda _: _sync_time_enabled())
        self.date_enabled.toggled.connect(lambda _: _sync_time_enabled())
        _sync_time_enabled()

        row_time.addWidget(self.time_enabled)
        row_time.addWidget(self.time_edit)
        layout.addLayout(row_time)

        layout.addWidget(QLabel(_get_text("Prioridade:") or "Prioridade:"))
        self.priority_combo = QComboBox(self)
        self.priority_labels = [
            _get_text("🔴 Importante e Urgente"),
            _get_text("🟠 Importante, mas Não Urgente"),
            _get_text("🟡 Não Importante, mas Urgente"),
            _get_text("🟢 Não Importante e Não Urgente"),
        ]
        self.priority_combo.addItems(self.priority_labels)

        def _coerce_priority(val):
            try:
                return int(val)

            except Exception:
                return None

        prio = _coerce_priority(initial_priority)

        if prio is None and isinstance(initial_priority, str):
            try:
                normalized = prioridade_para_texto(initial_priority, self._app)
                if normalized in self.priority_labels:
                    prio = self.priority_labels.index(normalized) + 1

            except Exception:
                prio = None

        if prio is None:
            prio = 1

        self.priority_combo.setCurrentIndex(max(0, min(3, prio - 1)))
        layout.addWidget(self.priority_combo)

        layout.addWidget(QLabel(_get_text("Descrição (opcional):")))
        self.desc = QTextEdit(self)
        self.desc.setPlainText(initial_description or "")
        self.desc.setMinimumHeight(120)
        layout.addWidget(self.desc)

        btns = QHBoxLayout()
        btns.addStretch(1)
        btn_cancel = QPushButton(_get_text("Cancelar") or "Cancelar")
        btn_ok = QPushButton(_get_text("OK") or "OK")
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def get_values(self):
        fp = self.file_field.toolTip() or None
        date_iso = None
        time_str = None

        if self.date_enabled.isChecked():
            date_iso = self.date_edit.date().toString(Qt.ISODate)

            if self.time_enabled.isChecked():
                time_str = self.time_edit.time().toString("HH:mm")

        priority = self.priority_combo.currentIndex() + 1
        return self.title.text().strip(), fp, self.desc.toPlainText().strip(), date_iso, time_str, priority
