from PySide6.QtWidgets import (QDialog, QVBoxLayout, QCalendarWidget, QComboBox, QListWidget,
                               QListWidgetItem, QCheckBox, QLabel, QHBoxLayout, QAbstractItemView,
                               QWidget, QSizePolicy, QStyle, QStyleOptionFrame, QToolTip, QMenu,
                               QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, QDate, QCoreApplication, QLocale, QSize, QEvent, QRect, QObject, QUrl
from PySide6.QtGui import QPainter, QFontMetrics, QTextCharFormat, QBrush, QColor, QFont, QPen, QPalette, QDesktopServices
from source.InterfaceCore.incore_07_show_context_menu import show_context_menu, _find_source_item_for_calendar, edit_task_dialog
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
from collections import defaultdict
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _emoji_from_priority(prio) -> str:
    try:
        label = prioridade_para_texto(prio, None)
        if label:
            emoji = str(label).strip()[:1]
            if emoji in {"🔴", "🟠", "🟡", "🟢"}:
                return emoji

    except Exception:
        pass

    return ""

def _task_label_for_day(task: dict, show_priority: bool) -> str:
    text = (task.get("text") or "").strip()
    time_str = task.get("time") or ""
    status_text = get_text("Concluída") if task.get("completed") else get_text("Pendente")
    emoji = _emoji_from_priority(task.get("priority")) if show_priority else ""
    if time_str:
        return f"{emoji} {time_str} — {text} [{status_text}]".strip()

    return f"{emoji} {text} [{status_text}]".strip()

def _tasks_for_date(owner, qdate: QDate) -> list[dict]:
    try:
        if qdate is None or not qdate.isValid():
            return []

        iso = qdate.toString(Qt.ISODate)
        tasks_all = owner._collect_tasks() if hasattr(owner, "_collect_tasks") else []
        return [t for t in tasks_all if t.get("date") == iso]

    except Exception:
        return []


class BadgeCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self._task_counts_by_date = {}  # {date_str: count}
            self._task_counts_by_week = {}  # {week_number: count}
            self._task_counts_by_month = {}  # {(year, month): count}
            self._tasks_by_date = {}  # {date_iso_str: [lines]}

        except Exception as e:
            logger.error(f"Erro ao inicializar BadgeCalendarWidget: {e}", exc_info=True)

        try:
            self.setMouseTracking(True)

        except Exception:
            pass

    def set_task_tooltip_map(self, tasks_by_date: dict):
        try:
            self._tasks_by_date = tasks_by_date or {}

        except Exception as e:
            logger.error(f"Erro ao definir mapa de tooltip do calendário: {e}", exc_info=True)

    def set_task_counts(self, task_dates_iso):
        try:
            self._task_counts_by_date.clear()
            self._task_counts_by_week.clear()
            self._task_counts_by_month.clear()

            for date_str in task_dates_iso:
                qdate = QDate.fromString(date_str, Qt.ISODate)
                if not qdate.isValid():
                    continue

                self._task_counts_by_date[date_str] = self._task_counts_by_date.get(date_str, 0) + 1

                week_num = qdate.weekNumber()[0]
                self._task_counts_by_week[week_num] = self._task_counts_by_week.get(week_num, 0) + 1

                month_key = (qdate.year(), qdate.month())
                self._task_counts_by_month[month_key] = self._task_counts_by_month.get(month_key, 0) + 1

            self.updateCells()

        except Exception as e:
            logger.error(f"Erro ao definir contadores de tarefas: {e}", exc_info=True)

    def paintCell(self, painter, rect, date):
        try:
            super().paintCell(painter, rect, date)

            date_str = date.toString(Qt.ISODate)
            count = self._task_counts_by_date.get(date_str, 0)

            if count > 0:
                self._draw_badge(painter, rect, count)

        except Exception as e:
            logger.error(f"Erro ao pintar célula do calendário: {e}", exc_info=True)

    def _draw_badge(self, painter, cell_rect, count):
        try:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)

            text = str(count)
            font = QFont(painter.font())
            font.setPointSize(max(7, font.pointSize() - 2))
            font.setBold(True)
            painter.setFont(font)

            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()

            badge_size = max(16, text_width + 8)
            badge_size = min(badge_size, cell_rect.width() // 2)

            badge_x = cell_rect.right() - badge_size - 2
            badge_y = cell_rect.top() + 2
            badge_rect = QRect(badge_x, badge_y, badge_size, badge_size)

            pal = self.palette()
            badge_color = pal.highlight().color()
            badge_color.setAlpha(200)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(badge_color))
            painter.drawEllipse(badge_rect)

            text_color = pal.highlightedText().color()
            painter.setPen(QPen(text_color))
            painter.drawText(badge_rect, Qt.AlignCenter, text)

            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao desenhar badge: {e}", exc_info=True)

    def _date_at_pos(self, pos):
        try:
            if hasattr(self, "dateAt"):
                try:
                    qd = self.dateAt(pos)
                    if isinstance(qd, QDate) and qd.isValid():
                        return qd

                except Exception:
                    pass

            view = self.findChild(QAbstractItemView)
            if view is not None:
                vpos = view.mapFrom(self, pos)
                idx = view.indexAt(vpos)
                if idx.isValid():
                    for role in (Qt.UserRole, Qt.UserRole + 1, Qt.UserRole + 2, Qt.DisplayRole):
                        try:
                            val = idx.data(role)
                            if isinstance(val, QDate) and val.isValid():
                                return val

                        except Exception:
                            pass

                    try:
                        day_val = idx.data(Qt.DisplayRole)
                        day = int(day_val)
                        if day > 0:
                            qd = QDate(self.yearShown(), self.monthShown(), day)
                            if qd.isValid():
                                return qd

                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Erro ao obter data pelo mouse no calendário: {e}", exc_info=True)

        return None

    def event(self, event):
        try:
            if event.type() == QEvent.ToolTip:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
                qd = self._date_at_pos(pos)
                if qd and qd.isValid():
                    ds = qd.toString(Qt.ISODate)
                    lines = self._tasks_by_date.get(ds) or []
                    if lines:
                        QToolTip.showText(event.globalPos(), "\n".join(lines), self)
                        return True

                QToolTip.hideText()
                event.ignore()
                return True

        except Exception as e:
            logger.error(f"Erro ao exibir tooltip no calendário: {e}", exc_info=True)

        return super().event(event)

    def get_week_count(self, week_number):
        return self._task_counts_by_week.get(week_number, 0)

    def get_month_count(self, year, month):
        return self._task_counts_by_month.get((year, month), 0)


class NativeLineEditFrame(QWidget):
    def __init__(self, child: QWidget, parent=None):
        super().__init__(parent)
        try:
            self._child = child
            self._layout = QVBoxLayout(self)
            self._layout.setSpacing(0)
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.addWidget(self._child)
            self._update_margins_from_style()

        except Exception as e:
            logger.error(f"Erro ao inicializar NativeLineEditFrame: {e}", exc_info=True)

    def _frame_width(self) -> int:
        try:
            return int(self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, None, self))

        except Exception:
            return 2

    def _update_margins_from_style(self):
        try:
            fw = self._frame_width()
            self._layout.setContentsMargins(fw, fw, fw, fw)
            self.updateGeometry()
            self.update()

        except Exception as e:
            logger.error(f"Erro ao atualizar margens do frame nativo: {e}", exc_info=True)

    def changeEvent(self, event):
        try:
            if event and event.type() in (QEvent.StyleChange, QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
                self._update_margins_from_style()

            super().changeEvent(event)

        except Exception as e:
            logger.error(f"Erro ao processar changeEvent no frame nativo: {e}", exc_info=True)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            opt = QStyleOptionFrame()
            opt.initFrom(self)
            opt.rect = self.rect()
            opt.lineWidth = self._frame_width()
            opt.midLineWidth = 0
            opt.state |= QStyle.State_Sunken
            self.style().drawPrimitive(QStyle.PE_FrameLineEdit, opt, painter, self)

        except Exception as e:
            logger.error(f"Erro ao pintar frame nativo: {e}", exc_info=True)


class CalendarDialog(QDialog):
    def __init__(self, app):
        super().__init__(app)
        try:
            self.app = app
            self.setModal(True)
            self.setWindowTitle(get_text("Calendário de Tarefas"))
            self._date_format = app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy"
            self._highlighted_dates = set() 

            main_layout = QVBoxLayout(self)

            self.calendar = BadgeCalendarWidget(self)
            initial_date = app.date_input.date() if hasattr(app, "date_input") else QDate.currentDate()
            self.calendar.setSelectedDate(initial_date)
            self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.calendar.customContextMenuRequested.connect(self._on_calendar_context_menu)

            hint = self.calendar.minimumSizeHint()
            fallback = QSize(300, 260)

            self.calendar_frame = NativeLineEditFrame(self.calendar, self)
            self.calendar_frame.setMinimumSize(hint.expandedTo(fallback))
            self.calendar_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self._apply_locale_to_calendar()

            main_layout.addWidget(self.calendar_frame)

            controls_layout = QHBoxLayout()
            self.filter_label = QLabel(get_text("Exibir por"), self)
            controls_layout.addWidget(self.filter_label)

            self.filter_combo = QComboBox(self)
            self.filter_combo.addItem(get_text("Dia"), "day")
            self.filter_combo.addItem(get_text("Semana"), "week")
            self.filter_combo.addItem(get_text("Mês"), "month")
            controls_layout.addWidget(self.filter_combo)
            controls_layout.addStretch()
            self.show_priority_checkbox = QCheckBox(get_text("Mostrar prioridade"), self)
            self.show_priority_checkbox.setChecked(True)
            self.show_priority_checkbox.stateChanged.connect(self.update_task_list)
            controls_layout.addWidget(self.show_priority_checkbox)
            main_layout.addLayout(controls_layout)

            self.tasks_label = QLabel(get_text("Lista Global de Tarefas:"), self)
            main_layout.addWidget(self.tasks_label)

            self.tasks_list = QListWidget(self)
            self.tasks_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.tasks_list.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.tasks_list.setSelectionRectVisible(True)
            self.tasks_list.setDragEnabled(False)
            self.tasks_list.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.tasks_list.setMouseTracking(True)
            self.tasks_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tasks_list.customContextMenuRequested.connect(lambda pt: show_context_menu(self.app, pt, self.tasks_list))

            try:
                self.tasks_list.itemDoubleClicked.connect(self._open_linked_file)

            except Exception:
                pass

            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarDialog: {e}", exc_info=True)

    def closeEvent(self, event):
        try:
            if hasattr(self.app, "gerenciador_traducao"):
                try:
                    self.app.gerenciador_traducao.idioma_alterado.disconnect(self._on_language_changed)

                except (RuntimeError, TypeError):
                    pass

            super().closeEvent(event)

        except Exception as e:
            logger.error(f"Erro ao fechar CalendarDialog: {e}", exc_info=True)

    def _open_linked_file(self, item):
        try:
            if item is None:
                return

            data = item.data(Qt.UserRole) or {}
            path = data.get("file_path")
            if not path:
                return

            import os, subprocess, sys

            try:
                if QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                    return

            except Exception:
                pass

            try:
                if os.path.exists(path):
                    if sys.platform.startswith("win"):
                        os.startfile(path)
                        return

                    elif sys.platform.startswith("darwin"):
                        subprocess.Popen(["open", path])
                        return

                    else:
                        subprocess.Popen(["xdg-open", path])
                        return

            except Exception as e:
                logger.error(f"Falha ao abrir arquivo vinculado via fallback: {e}", exc_info=True)

            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, get_text("Erro"), get_text("Arquivo não encontrado."))

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao abrir arquivo vinculado (Calendar): {e}", exc_info=True)

    def _collect_tasks(self):
        try:
            tasks = []
            mapping = [
                (self.app.quadrant1_list, self.app.quadrant1_label.text(), False),
                (self.app.quadrant1_completed_list, f"{self.app.quadrant1_label.text()} - {self.app.quadrant1_completed_label.text()}", True),
                (self.app.quadrant2_list, self.app.quadrant2_label.text(), False),
                (self.app.quadrant2_completed_list, f"{self.app.quadrant2_label.text()} - {self.app.quadrant2_completed_label.text()}", True),
                (self.app.quadrant3_list, self.app.quadrant3_label.text(), False),
                (self.app.quadrant3_completed_list, f"{self.app.quadrant3_label.text()} - {self.app.quadrant3_completed_label.text()}", True),
                (self.app.quadrant4_list, self.app.quadrant4_label.text(), False),
                (self.app.quadrant4_completed_list, f"{self.app.quadrant4_label.text()} - {self.app.quadrant4_completed_label.text()}", True),
            ]
            for lst, category, completed in mapping:
                for i in range(lst.count()):
                    item = lst.item(i)
                    if not item or not (item.flags() & Qt.ItemIsSelectable):
                        continue

                    data = item.data(Qt.UserRole) or {}
                    text = data.get("text", item.text())
                    date_str = data.get("date")
                    time_str = data.get("time")
                    file_path = data.get("file_path")
                    description = data.get("description")
                    priority = data.get("priority")
                    tasks.append({
                        "text": text,
                        "date": date_str,
                        "time": time_str,
                        "category": category,
                        "completed": completed,
                        "file_path": file_path,
                        "description": description,
                        "priority": priority,
                    })

            return tasks

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas do calendário: {e}", exc_info=True)
            return []

    def update_task_list(self):
        try:
            self.tasks_list.clear()
            self._apply_highlighted_dates()
            self._update_badge_counts()
            selected_date = self.calendar.selectedDate()
            filter_mode = self.filter_combo.currentData()
            filtered = []

            tasks_all = self._collect_tasks()
            try:
                def _emoji_from_priority(prio) -> str:
                    try:
                        label = prioridade_para_texto(prio, self)
                        if label:
                            emoji = str(label).strip()[:1]
                            if emoji in {"🔴", "🟠", "🟡", "🟢"}:
                                return emoji

                    except Exception:
                        pass

                    return ""

                show_priority = True
                try:
                    show_priority = bool(getattr(self, "show_priority_checkbox", None) and self.show_priority_checkbox.isChecked())

                except Exception:
                    show_priority = True

                tooltip_map = {}
                for task in tasks_all:
                    ds = task.get("date")
                    if not ds:
                        continue

                    text = (task.get("text") or "").strip()
                    if not text:
                        continue

                    time_str = task.get("time") or ""
                    emoji = _emoji_from_priority(task.get("priority")) if show_priority else ""
                    status_text = get_text("Concluída") if task.get("completed") else get_text("Pendente")
                    if time_str:
                        line = f"{emoji} {time_str} — {text} ({status_text})".strip()

                    else:
                        line = f"{emoji} {text} ({status_text})".strip()

                    tooltip_map.setdefault(ds, []).append(line)

                for ds, lines in tooltip_map.items():
                    lines.sort()

                if hasattr(self, "calendar") and hasattr(self.calendar, "set_task_tooltip_map"):
                    self.calendar.set_task_tooltip_map(tooltip_map)

            except Exception as e:
                logger.error(f"Erro ao atualizar tooltip do calendário: {e}", exc_info=True)

            for task in tasks_all:
                date_str = task.get("date")
                if not date_str:
                    continue

                qdate = QDate.fromString(date_str, Qt.ISODate)
                if not qdate.isValid():
                    continue

                if filter_mode == "day" and qdate != selected_date:
                    continue

                if filter_mode == "week":
                    selected_start_of_week = selected_date.addDays(-(selected_date.dayOfWeek() % 7))
                    task_start_of_week = qdate.addDays(-(qdate.dayOfWeek() % 7))
                    if selected_start_of_week != task_start_of_week:
                        continue

                if filter_mode == "month":
                    if qdate.month() != selected_date.month() or qdate.year() != selected_date.year():
                        continue

                filtered.append((qdate, task))

            if not filtered:
                placeholder = QListWidgetItem(get_text("Nenhuma tarefa para o período selecionado."))
                placeholder.setFlags((placeholder.flags() & ~Qt.ItemIsSelectable) & ~Qt.ItemIsEnabled)
                self.tasks_list.addItem(placeholder)
                return

            filtered.sort(key=lambda entry: (entry[0], entry[1]["time"] or "", entry[1]["text"].lower()))
            for qdate, task in filtered:
                status_text = get_text("Concluída") if task.get("completed") else get_text("Pendente")
                date_str = qdate.toString(self._date_format)
                time_str = task.get("time")
                if time_str:
                    dt_str = f"{date_str} {time_str}"

                else:
                    dt_str = date_str

                emoji = ""
                try:
                    if show_priority:
                        emoji = _emoji_from_priority(task.get("priority"))

                except Exception:
                    emoji = ""

                item_text = f"{emoji} {dt_str} — {task['text']} — [{status_text}]".strip()
                item = QListWidgetItem(item_text)
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                try:
                    item.setData(Qt.UserRole, task)

                except Exception:
                    pass

                try:
                    fp = task.get("file_path")
                    if fp:
                        font = item.font() or QFont()
                        font.setBold(True)
                        item.setFont(font)
                        try:
                            item.setForeground(Qt.blue)

                        except Exception:
                            pass

                except Exception:
                    pass

                try:
                    tooltip_lines = []
                    fp = task.get("file_path")
                    if fp:
                        tooltip_lines.append(f"{get_text('Arquivo') or 'Arquivo'}: {fp}")

                    if date_str:
                        tooltip_lines.append(f"{get_text('Data') or 'Data'}: {date_str}")

                    if time_str:
                        tooltip_lines.append(f"{get_text('Horário') or 'Horário'}: {time_str}")

                    desc = task.get("description")
                    if desc:
                        tooltip_lines.append(f"{get_text('Descrição') or 'Descrição'}: {desc}")

                    prio = task.get("priority")
                    if prio is not None and prio != "":
                        prio_text = prioridade_para_texto(prio, self)
                        tooltip_lines.append(f"{get_text('Prioridade') or 'Prioridade'}: {prio_text}")

                    if tooltip_lines:
                        try:
                            item.setToolTip("\n".join(tooltip_lines))

                        except Exception:
                            pass

                except Exception:
                    pass

                self.tasks_list.addItem(item)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas do calendário: {e}", exc_info=True)

    def _on_calendar_context_menu(self, pos):
        try:
            qd = None
            if hasattr(self.calendar, "_date_at_pos"):
                qd = self.calendar._date_at_pos(pos)

            if qd is None or not qd.isValid():
                return

            tasks = _tasks_for_date(self, qd)

            show_priority = True
            try:
                show_priority = bool(getattr(self, "show_priority_checkbox", None) and self.show_priority_checkbox.isChecked())

            except Exception:
                show_priority = True

            menu = QMenu(self.calendar)
            edit_menu = menu.addMenu(get_text("✏️ Editar Tarefa...") or "✏️ Editar Tarefa...")
            remove_menu = menu.addMenu(get_text("🗑️ Remover Tarefa") or "🗑️ Remover Tarefa")

            def _edit_task_from_calendar(task):
                src_list, item = _find_source_item_for_calendar(self.app, task)
                if item is None or src_list is None:
                    QMessageBox.warning(self, get_text("✏️ Editar Tarefa"), get_text("Tarefa não encontrada."))
                    return

                try:
                    edit_task_dialog(self.app, item)

                except Exception:
                    pass

                self.update_task_list()

            def _remove_task_from_calendar(task):
                src_list, item = _find_source_item_for_calendar(self.app, task)
                if item is None or src_list is None:
                    QMessageBox.warning(self, get_text("🗑️ Remover Tarefa"), get_text("Tarefa não encontrada."))
                    return

                try:
                    self.app.remove_task(item, src_list, confirm=False)

                except Exception:
                    pass

                self.update_task_list()

            if not tasks:
                edit_menu.setEnabled(False)
                remove_menu.setEnabled(False)

            else:
                for task in tasks:
                    label = _task_label_for_day(task, show_priority)
                    act_edit = edit_menu.addAction(label)
                    act_edit.triggered.connect(lambda checked=False, t=task: _edit_task_from_calendar(t))

                for task in tasks:
                    label = _task_label_for_day(task, show_priority)
                    act_remove = remove_menu.addAction(label)
                    act_remove.triggered.connect(lambda checked=False, t=task: _remove_task_from_calendar(t))

                remove_menu.addSeparator()
                act_remove_all = remove_menu.addAction(get_text("Remover Todas") or "Remover Todas")

                def _remove_all_tasks():
                    confirm = QMessageBox.question(
                        self,
                        get_text("Remover Todas") or "Remover Todas",
                        get_text("Deseja remover todas as tarefas deste dia?") or "Deseja remover todas as tarefas deste dia?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if confirm != QMessageBox.Yes:
                        return

                    for task in list(tasks):
                        src_list, item = _find_source_item_for_calendar(self.app, task)
                        if item is None or src_list is None:
                            continue

                        try:
                            self.app.remove_task(item, src_list, confirm=False)

                        except Exception:
                            pass

                    self.update_task_list()

                act_remove_all.triggered.connect(_remove_all_tasks)

            menu.exec(self.calendar.mapToGlobal(pos))

        except Exception as e:
            logger.error(f"Erro ao abrir menu de contexto do calendário: {e}", exc_info=True)

    def _prompt_edit_task_for_date(self, qdate: QDate):
        try:
            tasks = _tasks_for_date(self, qdate)
            if not tasks:
                QMessageBox.information(self, get_text("✏️ Editar Tarefa"), get_text("Nenhuma tarefa para este dia."))
                return

            show_priority = True
            try:
                show_priority = bool(getattr(self, "show_priority_checkbox", None) and self.show_priority_checkbox.isChecked())

            except Exception:
                show_priority = True

            items = [f"{i + 1}. {_task_label_for_day(task, show_priority)}" for i, task in enumerate(tasks)]
            choice, ok = QInputDialog.getItem(
                self,
                get_text("✏️ Editar Tarefa") or "✏️ Editar Tarefa",
                get_text("Selecione a tarefa") or "Selecione a tarefa",
                items,
                0,
                False,
            )
            if not ok or not choice:
                return

            idx = items.index(choice)
            task = tasks[idx]
            src_list, item = _find_source_item_for_calendar(self.app, task)
            if item is None or src_list is None:
                QMessageBox.warning(self, get_text("✏️ Editar Tarefa"), get_text("Tarefa não encontrada."))
                return

            try:
                self.app.edit_task_datetime(item, src_list)

            except Exception:
                pass

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao editar tarefa do calendário: {e}", exc_info=True)

    def _prompt_remove_task_for_date(self, qdate: QDate):
        try:
            tasks = _tasks_for_date(self, qdate)
            if not tasks:
                QMessageBox.information(self, get_text("🗑️ Remover Tarefa"), get_text("Nenhuma tarefa para este dia."))
                return

            show_priority = True
            try:
                show_priority = bool(getattr(self, "show_priority_checkbox", None) and self.show_priority_checkbox.isChecked())

            except Exception:
                show_priority = True

            items = [f"{i + 1}. {_task_label_for_day(task, show_priority)}" for i, task in enumerate(tasks)]
            items.append(get_text("Remover Todas") or "Remover Todas")

            choice, ok = QInputDialog.getItem(
                self,
                get_text("🗑️ Remover Tarefa") or "🗑️ Remover Tarefa",
                get_text("Selecione a tarefa") or "Selecione a tarefa",
                items,
                0,
                False,
            )
            if not ok or not choice:
                return

            if choice == items[-1]:
                confirm = QMessageBox.question(
                    self,
                    get_text("Remover Todas") or "Remover Todas",
                    get_text("Deseja remover todas as tarefas deste dia?") or "Deseja remover todas as tarefas deste dia?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if confirm != QMessageBox.Yes:
                    return

                for task in list(tasks):
                    src_list, item = _find_source_item_for_calendar(self.app, task)
                    if item is None or src_list is None:
                        continue

                    try:
                        self.app.remove_task(item, src_list, confirm=False)

                    except Exception:
                        pass

            else:
                idx = items.index(choice)
                task = tasks[idx]
                src_list, item = _find_source_item_for_calendar(self.app, task)
                if item is None or src_list is None:
                    QMessageBox.warning(self, get_text("🗑️ Remover Tarefa"), get_text("Tarefa não encontrada."))
                    return

                try:
                    self.app.remove_task(item, src_list, confirm=False)

                except Exception:
                    pass

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao remover tarefa do calendário: {e}", exc_info=True)

    def _update_badge_counts(self):
        try:
            task_dates = []
            for task in self._collect_tasks():
                date_str = task.get("date")
                if date_str:
                    task_dates.append(date_str)
            
            self.calendar.set_task_counts(task_dates)

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)

    def _on_language_changed(self):
        try:
            self.setWindowTitle(get_text("Calendário de Tarefas"))
            self.filter_label.setText(get_text("Exibir por"))
            self.filter_combo.setItemText(0, get_text("Dia"))
            self.filter_combo.setItemText(1, get_text("Semana"))
            self.filter_combo.setItemText(2, get_text("Mês"))

            try:
                self.tasks_label.setText(get_text("Lista Global de Tarefas:"))

            except Exception:
                pass

            try:
                if hasattr(self, "show_priority_checkbox"):
                    self.show_priority_checkbox.setText(get_text("Mostrar prioridade"))

            except Exception:
                pass

            self._date_format = self.app.date_input.displayFormat() if hasattr(self.app, "date_input") else self._date_format

            self._apply_locale_to_calendar()
            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do calendário: {e}", exc_info=True)

    def _apply_locale_to_calendar(self):
        try:
            idioma = None
            if hasattr(self.app, "gerenciador_traducao"):
                idioma = self.app.gerenciador_traducao.obter_idioma_atual()

            if idioma and idioma.startswith("pt"):
                locale = QLocale(QLocale.Portuguese, QLocale.Brazil)

            elif idioma and idioma.startswith("en"):
                locale = QLocale(QLocale.English, QLocale.UnitedStates)

            else:
                locale = QLocale.system()

            self.calendar.setLocale(locale)
            self.calendar.setFirstDayOfWeek(Qt.Sunday)

        except Exception as e:
            logger.error(f"Erro ao aplicar localidade no calendário: {e}", exc_info=True)

    def _get_task_dates(self):
        dates = set()
        try:
            for task in self._collect_tasks():
                ds = task.get("date")
                if not ds:
                    continue

                qd = QDate.fromString(ds, Qt.ISODate)
                if qd.isValid():
                    dates.add(qd.toString(Qt.ISODate))

        except Exception as e:
            logger.error(f"Erro ao obter datas das tarefas do calendário: {e}", exc_info=True)

        return dates

    def _apply_highlighted_dates(self):
        try:
            new_dates = self._get_task_dates()
            if not hasattr(self, "_highlighted_dates"):
                self._highlighted_dates = set()

            to_clear = self._highlighted_dates - new_dates
            if to_clear:
                blank = QTextCharFormat()
                for ds in to_clear:
                    qd = QDate.fromString(ds, Qt.ISODate)
                    if qd.isValid():
                        self.calendar.setDateTextFormat(qd, blank)

            fmt = QTextCharFormat()
            pal = self.palette()
            base = pal.highlight().color()
            color = QColor(base.red(), base.green(), base.blue(), 60)
            fmt.setBackground(QBrush(color))
            fmt.setFontWeight(QFont.Bold)

            for ds in new_dates:
                qd = QDate.fromString(ds, Qt.ISODate)
                if qd.isValid():
                    self.calendar.setDateTextFormat(qd, fmt)

            self._highlighted_dates = new_dates

        except Exception as e:
            logger.error(f"Erro ao aplicar destaque nas datas do calendário: {e}", exc_info=True)


class RotatedTabButton(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        try:
            self._text = text
            self.setMinimumWidth(25)
            self._recompute_size()

        except Exception as e:
            logger.error(f"Erro ao inicializar RotatedTabButton: {e}", exc_info=True)

    def setText(self, text):
        try:
            self._text = text
            self._recompute_size()
            self.update()

        except Exception as e:
            logger.error(f"Erro ao definir texto do botão de aba: {e}", exc_info=True)

    def text(self):
        try:
            return self._text

        except Exception as e:
            logger.error(f"Erro ao obter texto do botão de aba: {e}", exc_info=True)

    def _recompute_size(self):
        try:
            fm = QFontMetrics(self.font())
            text_w = fm.horizontalAdvance(self._text)
            text_h = fm.height()
            width = text_h + 5
            height = text_w + 20
            self.setFixedSize(QSize(width, height))

        except Exception as e:
            logger.error(f"Erro ao recalcular tamanho do botão de aba: {e}", exc_info=True)

    def mousePressEvent(self, event):
        try:
            self.parent().toggle_panel()
            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"Erro ao processar evento de clique no botão de aba: {e}", exc_info=True)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.save()
            painter.fillRect(self.rect(), self.palette().button().color())
            painter.setPen(self.palette().dark().color())
            painter.drawRect(0, 0, self.width()-1, self.height()-1)
            painter.translate(0, self.height())
            painter.rotate(270)
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(self._text)
            x = (self.height() - text_w) / 2
            y = (self.width() + fm.ascent() - fm.descent()) / 2
            painter.setPen(self.palette().buttonText().color())
            painter.drawText(x, y, self._text)
            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao pintar botão de aba: {e}", exc_info=True)


class CalendarPanel(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._date_format = app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy"
            self._highlighted_dates = set()

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(5, 1, 5, 9)
            main_layout.setSpacing(6)

            self.calendar = BadgeCalendarWidget(self)
            initial_date = app.date_input.date() if hasattr(app, "date_input") else QDate.currentDate()
            self.calendar.setSelectedDate(initial_date)
            self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.calendar.customContextMenuRequested.connect(self._on_calendar_context_menu)

            hint = self.calendar.minimumSizeHint()
            fallback = QSize(300, 260)

            self.calendar_frame = NativeLineEditFrame(self.calendar, self)
            self.calendar_frame.setMinimumSize(hint.expandedTo(fallback))
            self.calendar_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self._apply_locale_to_calendar()
            main_layout.addWidget(self.calendar_frame)

            controls_layout = QHBoxLayout()
            self.filter_label = QLabel(get_text("Exibir por"), self)
            controls_layout.addWidget(self.filter_label)

            self.filter_combo = QComboBox(self)
            self.filter_combo.addItem(get_text("Dia"), "day")
            self.filter_combo.addItem(get_text("Semana"), "week")
            self.filter_combo.addItem(get_text("Mês"), "month")
            controls_layout.addWidget(self.filter_combo)
            controls_layout.addStretch()
            self.show_priority_checkbox = QCheckBox(get_text("Mostrar prioridade"), self)
            self.show_priority_checkbox.setChecked(True)
            self.show_priority_checkbox.stateChanged.connect(self.update_task_list)
            controls_layout.addWidget(self.show_priority_checkbox)
            main_layout.addLayout(controls_layout)

            self.tasks_label = QLabel(get_text("Lista Global de Tarefas:"), self)
            main_layout.addWidget(self.tasks_label)

            self.tasks_list = QListWidget(self)
            self.tasks_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.tasks_list.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.tasks_list.setSelectionRectVisible(True)
            self.tasks_list.setDragEnabled(False)
            self.tasks_list.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.tasks_list.setMouseTracking(True)
            self.tasks_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tasks_list.customContextMenuRequested.connect(lambda pt: show_context_menu(self.app, pt, self.tasks_list))

            try:
                self.tasks_list.itemDoubleClicked.connect(lambda item: CalendarDialog._open_linked_file(self, item))

            except Exception:
                pass

            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarPanel: {e}", exc_info=True)

    def _collect_tasks(self):
        try:
            return CalendarDialog._collect_tasks(self)

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas: {e}", exc_info=True)

    def update_task_list(self):
        try:
            return CalendarDialog.update_task_list(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas: {e}", exc_info=True)

    def _update_badge_counts(self):
        try:
            return CalendarDialog._update_badge_counts(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)

    def _get_task_dates(self):
        try:
            return CalendarDialog._get_task_dates(self)

        except Exception as e:
            logger.error(f"Erro ao obter datas de tarefas: {e}", exc_info=True)

    def _apply_highlighted_dates(self):
        try:
            return CalendarDialog._apply_highlighted_dates(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar datas destacadas: {e}", exc_info=True)

    def _on_language_changed(self):
        try:
            self.filter_label.setText(get_text("Exibir por"))
            self.filter_combo.setItemText(0, get_text("Dia"))
            self.filter_combo.setItemText(1, get_text("Semana"))
            self.filter_combo.setItemText(2, get_text("Mês"))

            try:
                self.tasks_label.setText(get_text("Lista Global de Tarefas:"))

            except Exception:
                pass

            try:
                if hasattr(self, "show_priority_checkbox"):
                    self.show_priority_checkbox.setText(get_text("Mostrar prioridade"))

            except Exception:
                pass

            self._date_format = self.app.date_input.displayFormat() if hasattr(self.app, "date_input") else self._date_format
            self._apply_locale_to_calendar()
            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do painel de calendário: {e}", exc_info=True)

    def _apply_locale_to_calendar(self):
        try:
            return CalendarDialog._apply_locale_to_calendar(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar locale ao calendário: {e}", exc_info=True)

    def _on_calendar_context_menu(self, pos):
        try:
            return CalendarDialog._on_calendar_context_menu(self, pos)

        except Exception as e:
            logger.error(f"Erro ao abrir menu de contexto do calendário (painel): {e}", exc_info=True)

    def _prompt_edit_task_for_date(self, qdate: QDate):
        try:
            return CalendarDialog._prompt_edit_task_for_date(self, qdate)

        except Exception as e:
            logger.error(f"Erro ao editar tarefa do calendário (painel): {e}", exc_info=True)

    def _prompt_remove_task_for_date(self, qdate: QDate):
        try:
            return CalendarDialog._prompt_remove_task_for_date(self, qdate)

        except Exception as e:
            logger.error(f"Erro ao remover tarefa do calendário (painel): {e}", exc_info=True)


class Calendar(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._expanded = False
            self._panel_width = 360

            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 11, 0, 0)
            layout.setSpacing(0)

            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

            self.toggle_button = RotatedTabButton(get_text("Mostrar Calendário"), self)
            self.toggle_button.setMinimumWidth(25)
            layout.addWidget(self.toggle_button, 0, Qt.AlignLeft | Qt.AlignTop)

            self.calendar_panel = CalendarPanel(app, self)
            self.calendar_panel.setFixedWidth(self._panel_width)
            self.calendar_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            layout.addWidget(self.calendar_panel, 1)

            self.calendar_panel.setVisible(False)
            self._apply_fixed_width()

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self.on_language_changed)

        except Exception as e:
            logger.error(f"Erro ao inicializar Calendar: {e}", exc_info=True)

    def _apply_fixed_width(self):
        try:
            btn_w = self.toggle_button.width()
            total = btn_w + (self._panel_width if self._expanded else 0)
            self.setFixedWidth(total)

        except Exception as e:
            logger.error(f"Erro ao aplicar largura fixa: {e}", exc_info=True)

    def toggle_panel(self, open_if_hidden=False):
        try:
            previous = self._expanded
            if open_if_hidden and not self._expanded:
                self._expanded = True

            else:
                self._expanded = not self._expanded

            self.calendar_panel.setVisible(self._expanded)

            if self._expanded:
                hint_w = max(self.calendar_panel.sizeHint().width(), 300)
                self._panel_width = max(self._panel_width, hint_w)
                self.calendar_panel.setFixedWidth(self._panel_width)
                self.toggle_button.setText(get_text("Recolher Calendário"))

            else:
                self.toggle_button.setText(get_text("Mostrar Calendário"))

            self._apply_fixed_width()

            try:
                main_win = getattr(self, "app", None)
                if not main_win:
                    return

                if main_win.isMaximized():
                    try:
                        central = main_win.centralWidget()
                        if central:
                            central.updateGeometry()

                    except Exception:
                        pass

                    main_win.update()
                    return

                avail_w = None
                try:
                    wh = main_win.windowHandle()
                    if wh and wh.screen():
                        avail_w = wh.screen().availableGeometry().width()

                except Exception:
                    avail_w = None

                if avail_w is None:
                    try:
                        avail_w = main_win.screen().availableGeometry().width()

                    except Exception:
                        avail_w = 99999

                if self._expanded and not previous:
                    desired = main_win.width() + self._panel_width
                    new_w = min(desired, avail_w)
                    main_win.resize(new_w, main_win.height())

                elif (not self._expanded) and previous:
                    new_w = max(400, main_win.width() - self._panel_width)
                    main_win.resize(new_w, main_win.height())

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao alternar painel de calendário: {e}", exc_info=True)

    def on_language_changed(self):
        try:
            self.toggle_button.setText(get_text("Recolher Calendário") if self._expanded else get_text("Mostrar Calendário"))
            try:
                self.calendar_panel._on_language_changed()

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do calendário: {e}", exc_info=True)
