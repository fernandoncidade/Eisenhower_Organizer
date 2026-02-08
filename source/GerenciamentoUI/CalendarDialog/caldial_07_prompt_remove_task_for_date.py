from PySide6.QtWidgets import QInputDialog, QMessageBox
from PySide6.QtCore import Qt, QDate, QCoreApplication
from source.InterfaceCore.incore_07_MostrarMenuContexto import _find_source_item_for_calendar
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
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

            removed_count = 0
            failed_count = 0

            for task in list(tasks):
                src_list, item = _find_source_item_for_calendar(self.app, task)

                if item is None or src_list is None:
                    failed_count += 1
                    continue

                try:
                    if self.app.remove_task(item, src_list, confirm=False):
                        removed_count += 1

                    else:
                        failed_count += 1

                except Exception:
                    failed_count += 1

            try:
                if removed_count > 0 and failed_count == 0:
                    QMessageBox.information(
                        self,
                        get_text("🗑️ Remover Tarefa"),
                        get_text("Tarefa(s) removida(s) com sucesso.") or "Tarefa(s) removida(s) com sucesso.",
                    )
                elif removed_count > 0:
                    QMessageBox.warning(
                        self,
                        get_text("🗑️ Remover Tarefa"),
                        get_text("Algumas tarefas nao puderam ser removidas.") or "Algumas tarefas nao puderam ser removidas.",
                    )
                else:
                    QMessageBox.warning(
                        self,
                        get_text("🗑️ Remover Tarefa"),
                        get_text("Nao foi possivel remover as tarefas deste dia.") or "Nao foi possivel remover as tarefas deste dia.",
                    )

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
                removed = self.app.remove_task(item, src_list, confirm=True)

            except Exception:
                removed = False

            if removed:
                self.update_task_list()

            return

        self.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao remover tarefa do calendário: {e}", exc_info=True)
