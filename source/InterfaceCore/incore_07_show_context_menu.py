from PySide6.QtWidgets import (QMenu, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QDateEdit,
                               QTimeEdit, QCheckBox, QDialogButtonBox, QCalendarWidget, QApplication, QFileDialog, QLineEdit)
from PySide6.QtGui import QAction, QColor, QPalette, QFont, QDesktopServices
from PySide6.QtCore import QCoreApplication, Qt, QDate, QTime, QLocale, QUrl
from PySide6.QtGui import QFont
from source.InterfaceCore.incore_01_initUI import FileDropLineEdit
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
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

def _is_completed_list(app, lst) -> bool:
    return lst in (
        app.quadrant1_completed_list,
        app.quadrant2_completed_list,
        app.quadrant3_completed_list,
        app.quadrant4_completed_list,
    )

def _quadrant_options(app):
    return [
        app.quadrant1_label.text(),
        app.quadrant2_label.text(),
        app.quadrant3_label.text(),
        app.quadrant4_label.text(),
    ]

def _target_list_for_quadrant(app, quadrant_index: int, keep_completed: bool):
    pending = [app.quadrant1_list, app.quadrant2_list, app.quadrant3_list, app.quadrant4_list]
    done = [app.quadrant1_completed_list, app.quadrant2_completed_list, app.quadrant3_completed_list, app.quadrant4_completed_list]
    if 0 <= quadrant_index < 4:
        return done[quadrant_index] if keep_completed else pending[quadrant_index]

    return None

def _find_source_item_for_calendar(app, task_dict):
    try:
        if not isinstance(task_dict, dict):
            return None, None

        cat = task_dict.get("category")
        if not cat:
            return None, None

        completed = bool(task_dict.get("completed"))
        labels = [
            getattr(app, "quadrant1_label", None).text() if getattr(app, "quadrant1_label", None) is not None else None,
            getattr(app, "quadrant2_label", None).text() if getattr(app, "quadrant2_label", None) is not None else None,
            getattr(app, "quadrant3_label", None).text() if getattr(app, "quadrant3_label", None) is not None else None,
            getattr(app, "quadrant4_label", None).text() if getattr(app, "quadrant4_label", None) is not None else None,
        ]
        pending = [getattr(app, "quadrant1_list", None), getattr(app, "quadrant2_list", None), getattr(app, "quadrant3_list", None), getattr(app, "quadrant4_list", None)]
        done = [getattr(app, "quadrant1_completed_list", None), getattr(app, "quadrant2_completed_list", None), getattr(app, "quadrant3_completed_list", None), getattr(app, "quadrant4_completed_list", None)]

        for idx, label in enumerate(labels):
            try:
                if not label:
                    continue

                if not str(cat).startswith(label):
                    continue

                src_list = done[idx] if completed else pending[idx]
                if src_list is None:
                    continue

                for i in range(src_list.count()):
                    it = src_list.item(i)
                    if not it:
                        continue

                    if not (it.flags() & Qt.ItemIsSelectable):
                        continue

                    d = it.data(Qt.UserRole) or {}
                    if (str(d.get("text") or "").strip() == str(task_dict.get("text") or "").strip()) and (d.get("date") or "") == (task_dict.get("date") or "") and (d.get("time") or "") == (task_dict.get("time") or ""):
                        return src_list, it

            except Exception:
                continue

    except Exception:
        pass

    return None, None

def _base_text_from_item(item) -> str:
    data = item.data(Qt.UserRole) or {}
    base = (data.get("text") or "").strip()
    if base:
        return base

    txt = (item.text() or "").strip()
    if " — " in txt:
        return txt.split(" — ", 1)[0].strip()

    return txt

def _build_display_and_tooltip(app, base_text: str, date_iso: str | None, time_str: str | None):
    display_text = base_text
    tooltip_lines = []

    if date_iso:
        qd = QDate.fromString(date_iso, Qt.ISODate)
        if qd.isValid():
            date_human = qd.toString(app.date_input.displayFormat())
            if time_str:
                display_text = f"{base_text} — {date_human} {time_str}"

            else:
                display_text = f"{base_text} — {date_human}"

            tooltip_lines.append(f"{get_text('Data') or 'Data'}: {date_human}")

    if time_str:
        tooltip_lines.append(f"{get_text('Horário') or 'Horário'}: {time_str}")

    return display_text, ("\n".join(tooltip_lines) if tooltip_lines else "")

def _edit_date_time_dialog(app, item):
    try:
        data = item.data(Qt.UserRole) or {}
        current_date_iso = data.get("date")
        current_time = data.get("time")

        dlg = QDialog(app)
        dlg.setWindowTitle(get_text("Editar data/horário..."))
        layout = QVBoxLayout(dlg)

        row_date = QHBoxLayout()
        cb_date = QCheckBox(get_text("Vincular data"), dlg)
        de = QDateEdit(dlg)
        de.setCalendarPopup(True)
        de.setDisplayFormat(app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy")
        de.setDate(QDate.currentDate())
        _apply_widget_min_height(app, de, "dialog_date_edit")
        _apply_locale_to_dateedit(app, de)

        if current_date_iso:
            qd = QDate.fromString(current_date_iso, Qt.ISODate)
            if qd.isValid():
                cb_date.setChecked(True)
                de.setDate(qd)

            else:
                cb_date.setChecked(False)

        else:
            cb_date.setChecked(False)

        de.setEnabled(cb_date.isChecked())
        cb_date.toggled.connect(de.setEnabled)

        row_date.addWidget(cb_date)
        row_date.addWidget(de)
        layout.addLayout(row_date)

        row_time = QHBoxLayout()
        cb_time = QCheckBox(get_text("Vincular horário"), dlg)
        te = QTimeEdit(dlg)
        te.setDisplayFormat("HH:mm")
        te.setTime(QTime.currentTime())
        _apply_widget_min_height(app, te, "dialog_time_edit")

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

                try:
                    fill_color = QColor(window_color)

                except Exception:
                    fill_color = window_color

                pal_te = te.palette()
                pal_te.setColor(QPalette.Base, fill_color)
                pal_te.setColor(QPalette.AlternateBase, fill_color)
                te.setPalette(pal_te)

        except Exception:
            pass

        if current_time:
            qt = QTime.fromString(current_time, "HH:mm")
            if qt.isValid():
                cb_time.setChecked(True)
                te.setTime(qt)

            else:
                cb_time.setChecked(False)

        else:
            cb_time.setChecked(False)

        def _sync_time_enabled():
            te.setEnabled(cb_date.isChecked() and cb_time.isChecked())

        cb_time.toggled.connect(lambda _: _sync_time_enabled())
        cb_date.toggled.connect(lambda _: _sync_time_enabled())
        _sync_time_enabled()

        row_time.addWidget(cb_time)
        row_time.addWidget(te)
        layout.addLayout(row_time)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dlg)

        try:
            ok_btn = buttons.button(QDialogButtonBox.Ok)
            cancel_btn = buttons.button(QDialogButtonBox.Cancel)
            if ok_btn:
                ok_btn.setText(get_text("OK"))

            if cancel_btn:
                cancel_btn.setText(get_text("Cancelar"))

        except Exception:
            pass

        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        try:
            if hasattr(app, "gerenciador_traducao"):
                def _on_idioma_alterado(_=None):
                    dlg.setWindowTitle(get_text("Editar data/horário..."))
                    cb_date.setText(get_text("Vincular data"))
                    cb_time.setText(get_text("Vincular horário"))
                    _apply_locale_to_dateedit(app, de)

                    try:
                        ok_btn = buttons.button(QDialogButtonBox.Ok)
                        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
                        if ok_btn:
                            ok_btn.setText(get_text("OK"))

                        if cancel_btn:
                            cancel_btn.setText(get_text("Cancelar"))

                    except Exception:
                        pass

                app.gerenciador_traducao.idioma_alterado.connect(_on_idioma_alterado)

        except Exception:
            pass

        if dlg.exec() != QDialog.Accepted:
            return

        new_date_iso = None
        new_time_str = None

        if cb_date.isChecked():
            new_date_iso = de.date().toString(Qt.ISODate)
            if cb_time.isChecked():
                new_time_str = te.time().toString("HH:mm")

        base_text = _base_text_from_item(item)
        display_text, tooltip = _build_display_and_tooltip(app, base_text, new_date_iso, new_time_str)

        new_data = dict(data) if isinstance(data, dict) else {}
        new_data["text"] = base_text
        new_data["date"] = new_date_iso
        new_data["time"] = new_time_str

        lst = item.listWidget()
        try:
            if isinstance(data, dict) and data.get("category"):
                src_lst, src_item = _find_source_item_for_calendar(app, data)
                if src_lst is not None and src_item is not None:
                    lst = src_lst
                    item = src_item

        except Exception:
            pass

        if lst is None:
            return

        row = lst.row(item)
        check_state = item.checkState()

        lst.takeItem(row)
        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(lst)

        except Exception:
            pass

        from PySide6.QtWidgets import QListWidgetItem
        new_item = QListWidgetItem(display_text)
        new_item.setFlags(new_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        new_item.setCheckState(check_state)
        new_item.setData(Qt.UserRole, new_data)

        try:
            tooltip_lines = []
            if tooltip:
                tooltip_lines.append(tooltip)

            try:
                fp = new_data.get("file_path")
                if fp:
                    tooltip_lines.append((get_text("Arquivo") or "Arquivo") + f": {fp}")

            except Exception:
                pass

            try:
                desc_full = new_data.get("description")
                if desc_full:
                    preview_lines = [ln for ln in desc_full.splitlines() if ln.strip()]
                    preview = "\n".join(preview_lines[:3])
                    if preview:
                        tooltip_lines.append((get_text("Descrição") or "Descrição") + ":")
                        tooltip_lines.append(preview)

            except Exception:
                pass

            try:
                prio = new_data.get("priority")
                if prio is not None and prio != "":
                    prio_text = prioridade_para_texto(prio, app)
                    tooltip_lines.append((get_text("Prioridade") or "Prioridade") + f": {prio_text}")

            except Exception:
                pass

            if tooltip_lines:
                new_item.setToolTip("\n".join(tooltip_lines))

        except Exception:
            try:
                if tooltip:
                    new_item.setToolTip(tooltip)

            except Exception:
                pass

        try:
            if new_data.get("file_path"):
                font = new_item.font() or QFont()
                font.setBold(True)
                new_item.setFont(font)

                try:
                    new_item.setForeground(Qt.blue)

                except Exception:
                    pass

        except Exception:
            pass

        if hasattr(app, "insert_task_into_quadrant_list"):
            app.insert_task_into_quadrant_list(lst, new_item)

        else:
            lst.addItem(new_item)

        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(lst)

        except Exception:
            pass

        app.save_tasks()
        if hasattr(app, "calendar_pane") and app.calendar_pane:
            app.calendar_pane.calendar_panel.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao editar data/horário via menu: {e}", exc_info=True)

def _move_to_quadrant(app, item, source_list):
    try:
        opts = _quadrant_options(app)
        chosen, ok = QInputDialog.getItem(
            app,
            get_text("Mover tarefa"),
            get_text("Selecione o quadrante:"),
            opts,
            0,
            False
        )
        if not ok or not chosen:
            return

        try:
            idx = opts.index(chosen)

        except ValueError:
            return

        keep_completed = _is_completed_list(app, source_list)
        target = _target_list_for_quadrant(app, idx, keep_completed=keep_completed)
        if target is None or target is source_list:
            return

        new_state = Qt.Checked if keep_completed else Qt.Unchecked

        source_list.blockSignals(True)
        target.blockSignals(True)

        try:
            app.move_item_between_lists(item, source_list, target, new_state)

        finally:
            source_list.blockSignals(False)
            target.blockSignals(False)

        app.save_tasks()
        if hasattr(app, "calendar_pane") and app.calendar_pane:
            app.calendar_pane.calendar_panel.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao mover tarefa de quadrante via menu: {e}", exc_info=True)

def mostrar_menu_contexto(app, point, list_widget):
    try:
        item = list_widget.itemAt(point)
        if not item:
            return

        if not bool(item.flags() & Qt.ItemIsSelectable):
            return

        menu = QMenu(list_widget)

        try:
            def _edit_description():
                try:
                    class DescriptionDialog(QDialog):
                        def __init__(self, parent=None, initial_text=""):
                            super().__init__(parent or app)
                            self.setModal(True)
                            self.setWindowTitle(get_text("Descrição da Tarefa") or "Descrição da Tarefa")
                            layout = QVBoxLayout(self)
                            layout.addWidget(QLabel(get_text("Adicione uma descrição para a tarefa:")))
                            self.text = QTextEdit(self)
                            self.text.setPlainText(initial_text or "")
                            self.text.setMinimumSize(400, 150)
                            layout.addWidget(self.text)
                            btns = QHBoxLayout()
                            btns.addStretch(1)
                            btn_cancel = QPushButton(get_text("Cancelar") or "Cancelar")
                            btn_ok = QPushButton(get_text("OK") or "OK")
                            btn_cancel.clicked.connect(self.reject)
                            btn_ok.clicked.connect(self.accept)
                            btns.addWidget(btn_cancel)
                            btns.addWidget(btn_ok)
                            layout.addLayout(btns)

                        def get_text(self):
                            return self.text.toPlainText()

                    current_data = item.data(Qt.UserRole) or {}
                    existing = current_data.get("description", "")

                    try:
                        src_list = None
                        src_item = None
                        if isinstance(current_data, dict) and current_data.get("category"):
                            src_list, src_item = _find_source_item_for_calendar(app, current_data)
                            if src_list is None:
                                src_list = list_widget
                                src_item = item

                        else:
                            src_list = list_widget
                            src_item = item

                    except Exception:
                        src_list = list_widget
                        src_item = item

                    dlg = DescriptionDialog(parent=app, initial_text=existing)
                    if dlg.exec() == QDialog.Accepted:
                        desc = dlg.get_text().strip()
                        data = dict(current_data) if isinstance(current_data, dict) else {}
                        if desc:
                            data["description"] = desc

                        else:
                            data.pop("description", None)

                        try:
                            src_list.blockSignals(True)

                        except Exception:
                            pass

                        try:
                            src_item.setData(Qt.UserRole, data)

                            tooltip_lines = []
                            try:
                                date_val = data.get("date")
                                time_val = data.get("time")
                                if date_val:
                                    qd = QDate.fromString(date_val, Qt.ISODate)
                                    if qd.isValid() and hasattr(app, "date_input"):
                                        date_human = qd.toString(app.date_input.displayFormat())
                                        tooltip_lines.append(f"{get_text('Data') or 'Data'}: {date_human}")
                                        if time_val:
                                            tooltip_lines.append(f"{get_text('Horário') or 'Horário'}: {time_val}")

                            except Exception:
                                pass

                            try:
                                fp = data.get("file_path")
                                if fp:
                                    tooltip_lines.append((get_text("Arquivo") or "Arquivo") + f": {fp}")

                            except Exception:
                                pass

                            try:
                                desc_full = data.get("description")
                                if desc_full:
                                    preview_lines = [ln for ln in desc_full.splitlines() if ln.strip()]
                                    preview = "\n".join(preview_lines[:3])
                                    if preview:
                                        tooltip_lines.append((get_text("Descrição") or "Descrição") + ":")
                                        tooltip_lines.append(preview)

                            except Exception:
                                pass

                            try:
                                prio = data.get("priority")
                                if prio is not None and prio != "":
                                    prio_text = prioridade_para_texto(prio, app)
                                    tooltip_lines.append((get_text("Prioridade") or "Prioridade") + f": {prio_text}")

                            except Exception:
                                pass

                            if tooltip_lines:
                                src_item.setToolTip("\n".join(tooltip_lines))

                        finally:
                            try:
                                src_list.blockSignals(False)

                            except Exception:
                                pass

                        try:
                            app.save_tasks()

                        except Exception:
                            pass

                        try:
                            if item is not None and item is not src_item:
                                try:
                                    item.setData(Qt.UserRole, data)
                                    if tooltip_lines:
                                        item.setToolTip("\n".join(tooltip_lines))

                                except Exception:
                                    pass

                        except Exception:
                            pass

                        try:
                            if hasattr(app, "calendar_pane") and app.calendar_pane:
                                app.calendar_pane.calendar_panel.update_task_list()

                        except Exception:
                            pass

                except Exception as e:
                    logger.error(f"Erro no diálogo de descrição: {e}", exc_info=True)

            descricao_acao = QAction(get_text("Adicionar/Editar Descrição...") or "Adicionar/Editar Descrição...", app)
            descricao_acao.triggered.connect(_edit_description)
            menu.addAction(descricao_acao)

        except Exception:
            pass

        try:
            current_data = item.data(Qt.UserRole) or {}
            fp = current_data.get("file_path")
            if fp:
                abrir_acao = QAction(get_text("Abrir Arquivo Vinculado...") or "Abrir Arquivo Vinculado...", app)
                def _abrir_arquivo():
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

                abrir_acao.triggered.connect(_abrir_arquivo)
                menu.addAction(abrir_acao)

        except Exception:
            pass

        def _edit_task():
            try:
                class EditTaskDialog(QDialog):
                    def __init__(self, parent=None, initial_text="", initial_file="", initial_description=""):
                        super().__init__(parent or app)
                        self.setModal(True)
                        self.setWindowTitle(get_text("Editar Tarefa") or "Editar Tarefa")
                        layout = QVBoxLayout(self)

                        layout.addWidget(QLabel(get_text("Tarefa:")))
                        self.title = QLineEdit(self)
                        self.title.setText(initial_text or "")
                        layout.addWidget(self.title)

                        layout.addWidget(QLabel(get_text("Arquivo vinculado (arraste ou escolha):")))
                        hl = QHBoxLayout()
                        self.file_field = FileDropLineEdit(app, self)
                        self.file_field.setText(initial_file and (initial_file.split("\\")[-1] or initial_file) or "")
                        self.file_field.setToolTip(initial_file or "")
                        hl.addWidget(self.file_field)
                        btn_choose = QPushButton(get_text("Escolher..."))

                        def _choose():
                            try:
                                path, _ = QFileDialog.getOpenFileName(self, get_text("Escolher arquivo"), "", "*")
                                if path:
                                    self.file_field.setText(path.split("\\")[-1])
                                    self.file_field.setToolTip(path)

                            except Exception:
                                pass

                        btn_choose.clicked.connect(_choose)
                        btn_clear = QPushButton(get_text("Remover"))

                        def _clear():
                            try:
                                self.file_field.clear()
                                self.file_field.setToolTip("")

                            except Exception:
                                pass

                        btn_clear.clicked.connect(_clear)
                        hl.addWidget(btn_choose)
                        hl.addWidget(btn_clear)
                        layout.addLayout(hl)

                        layout.addWidget(QLabel(get_text("Descrição (opcional):")))
                        self.desc = QTextEdit(self)
                        self.desc.setPlainText(initial_description or "")
                        self.desc.setMinimumHeight(120)
                        layout.addWidget(self.desc)

                        btns = QHBoxLayout()
                        btns.addStretch(1)
                        btn_cancel = QPushButton(get_text("Cancelar") or "Cancelar")
                        btn_ok = QPushButton(get_text("OK") or "OK")
                        btn_cancel.clicked.connect(self.reject)
                        btn_ok.clicked.connect(self.accept)
                        btns.addWidget(btn_cancel)
                        btns.addWidget(btn_ok)
                        layout.addLayout(btns)

                    def get_values(self):
                        fp = self.file_field.toolTip() or None
                        return self.title.text().strip(), fp, self.desc.toPlainText().strip()

                data = item.data(Qt.UserRole) or {}

                try:
                    src_list = None
                    src_item = None
                    if isinstance(data, dict) and data.get("category"):
                        src_list, src_item = _find_source_item_for_calendar(app, data)
                        if src_item is None:
                            src_list = item.listWidget()
                            src_item = item

                    else:
                        src_list = item.listWidget()
                        src_item = item

                except Exception:
                    src_list = item.listWidget()
                    src_item = item

                initial_text = data.get("text") or _base_text_from_item(item)
                initial_file = data.get("file_path") or ""
                initial_desc = data.get("description") or ""

                dlg = EditTaskDialog(parent=app, initial_text=initial_text, initial_file=initial_file, initial_description=initial_desc)
                if dlg.exec() != QDialog.Accepted:
                    return

                new_text, new_file_path, new_desc = dlg.get_values()
                if not new_text:
                    return

                new_data = dict(data) if isinstance(data, dict) else {}
                new_data["text"] = new_text
                if new_file_path:
                    new_data["file_path"] = new_file_path

                else:
                    new_data.pop("file_path", None)

                if new_desc:
                    new_data["description"] = new_desc

                else:
                    new_data.pop("description", None)

                date_iso = new_data.get("date")
                time_str = new_data.get("time")

                display_text, _dt_tooltip = _build_display_and_tooltip(app, new_text, date_iso, time_str)
                tooltip_lines = []
                if _dt_tooltip:
                    tooltip_lines.append(_dt_tooltip)

                try:
                    fp = new_data.get("file_path")
                    if fp:
                        tooltip_lines.append((get_text("Arquivo") or "Arquivo") + f": {fp}")

                except Exception:
                    pass

                try:
                    desc_full = new_data.get("description")
                    if desc_full:
                        preview_lines = [ln for ln in desc_full.splitlines() if ln.strip()]
                        preview = "\n".join(preview_lines[:3])
                        if preview:
                            tooltip_lines.append((get_text("Descrição") or "Descrição") + ":")
                            tooltip_lines.append(preview)

                except Exception:
                    pass

                tooltip = "\n".join(tooltip_lines) if tooltip_lines else ""
                if isinstance(new_data, dict):
                    try:
                        if new_data.get("file_path"):
                            font = item.font() or QFont()
                            font.setBold(True)

                    except Exception:
                        pass

                lst = src_list if src_list is not None else item.listWidget()
                if lst is None:
                    return

                row = lst.row(src_item if src_item is not None else item)
                check_state = (src_item if src_item is not None else item).checkState()
                lst.takeItem(row)

                from PySide6.QtWidgets import QListWidgetItem
                new_item = QListWidgetItem(display_text)
                new_item.setFlags(new_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                new_item.setCheckState(check_state)
                new_item.setData(Qt.UserRole, new_data)
                if tooltip:
                    new_item.setToolTip(tooltip)

                try:
                    if new_data.get("file_path"):
                        font = new_item.font() or QFont()
                        font.setBold(True)
                        new_item.setFont(font)
                        new_item.setForeground(Qt.blue)

                except Exception:
                    pass

                if hasattr(app, "insert_task_into_quadrant_list"):
                    app.insert_task_into_quadrant_list(lst, new_item)

                else:
                    lst.addItem(new_item)

                try:
                    if hasattr(app, "cleanup_time_groups"):
                        app.cleanup_time_groups(lst)

                except Exception:
                    pass

                try:
                    app.save_tasks()

                except Exception:
                    pass

                try:
                    if hasattr(app, "calendar_pane") and app.calendar_pane:
                        app.calendar_pane.calendar_panel.update_task_list()

                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Erro ao editar tarefa via menu: {e}", exc_info=True)

        editar_data_acao = QAction(get_text("Editar data/horário..."), app)
        editar_data_acao.triggered.connect(lambda: _edit_date_time_dialog(app, item))
        menu.addAction(editar_data_acao)

        editar_acao = QAction(get_text("Editar Tarefa...") or "Editar Tarefa...", app)
        editar_acao.triggered.connect(_edit_task)
        menu.addAction(editar_acao)

        try:
            opts = _quadrant_options(app)
            mover_menu = QMenu(get_text("Mover para outro quadrante"), app)

            try:
                data_for_resolution = item.data(Qt.UserRole) or {}
                src_list_for_move, src_item_for_move = (None, None)
                if isinstance(data_for_resolution, dict) and data_for_resolution.get("category"):
                    src_list_for_move, src_item_for_move = _find_source_item_for_calendar(app, data_for_resolution)

                if src_list_for_move is None:
                    src_list_for_move = list_widget
                    src_item_for_move = item

            except Exception:
                src_list_for_move = list_widget
                src_item_for_move = item

            for idx, label in enumerate(opts):
                a = QAction(label, app)
                def _make_handler(i, source_list=src_list_for_move, source_item=src_item_for_move):
                    def _handler():
                        try:
                            keep_completed = _is_completed_list(app, source_list)
                            target = _target_list_for_quadrant(app, i, keep_completed=keep_completed)
                            if target is None or target is source_list:
                                return

                            new_state = Qt.Checked if keep_completed else Qt.Unchecked

                            source_list.blockSignals(True)
                            target.blockSignals(True)

                            try:
                                app.move_item_between_lists(source_item, source_list, target, new_state)

                            finally:
                                source_list.blockSignals(False)
                                target.blockSignals(False)

                            try:
                                app.save_tasks()

                            except Exception:
                                pass

                            try:
                                if hasattr(app, "calendar_pane") and app.calendar_pane:
                                    app.calendar_pane.calendar_panel.update_task_list()

                            except Exception:
                                pass

                        except Exception as e:
                            logger.error(f"Erro ao mover tarefa de quadrante via submenu: {e}", exc_info=True)

                    return _handler

                a.triggered.connect(_make_handler(idx))
                mover_menu.addAction(a)

            menu.addMenu(mover_menu)

        except Exception:
            mover_acao = QAction(get_text("Mover para outro quadrante"), app)
            mover_acao.triggered.connect(lambda: _move_to_quadrant(app, item, list_widget))
            menu.addAction(mover_acao)

        menu.addSeparator()
        remover_acao = QAction(get_text("Remover Tarefa"), app)

        try:
            current_data_for_removal = item.data(Qt.UserRole) or {}
            if isinstance(current_data_for_removal, dict) and current_data_for_removal.get("category"):
                src_list_rem, src_item_rem = _find_source_item_for_calendar(app, current_data_for_removal)
                if src_list_rem is not None and src_item_rem is not None:
                    def _remove_both():
                        try:
                            removed = app.remove_task(src_item_rem, src_list_rem, True)
                            if not removed:
                                return

                            try:
                                if item is not None and list_widget is not None:
                                    try:
                                        list_widget.takeItem(list_widget.row(item))

                                    except Exception:
                                        pass

                            except Exception:
                                pass

                            try:
                                app.save_tasks()

                            except Exception:
                                pass

                            try:
                                if hasattr(app, "calendar_pane") and app.calendar_pane:
                                    app.calendar_pane.calendar_panel.update_task_list()

                            except Exception:
                                pass

                        except Exception:
                            pass

                    remover_acao.triggered.connect(_remove_both)

                else:
                    remover_acao.triggered.connect(lambda: app.remove_task(item, list_widget))

            else:
                remover_acao.triggered.connect(lambda: app.remove_task(item, list_widget))

        except Exception:
            remover_acao.triggered.connect(lambda: app.remove_task(item, list_widget))

        menu.addAction(remover_acao)
        menu.exec(list_widget.mapToGlobal(point))

    except Exception as e:
        logger.error(f"Erro ao exibir menu de contexto: {e}", exc_info=True)

def show_context_menu(app, point, list_widget):
    return mostrar_menu_contexto(app, point, list_widget)
