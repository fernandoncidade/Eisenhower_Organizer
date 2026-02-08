from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt, QDate, QCoreApplication
from PySide6.QtGui import QFont
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

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
