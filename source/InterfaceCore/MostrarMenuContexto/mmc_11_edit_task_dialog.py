from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QFont
from PySide6.QtCore import QCoreApplication, Qt
from .mmc_05_is_completed_list import _is_completed_list
from .mmc_07_target_list_for_quadrant import _target_list_for_quadrant
from .mmc_08_find_source_item_for_calendar import _find_source_item_for_calendar
from .mmc_09_base_text_from_item import _base_text_from_item
from .mmc_10_build_display_and_tooltip import _build_display_and_tooltip
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.InterfaceCore.incore_14_EditTaskDialog import EditTaskDialog
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def edit_task_dialog(app, item):
    try:
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
        initial_date_iso = data.get("date")
        initial_time_str = data.get("time")

        initial_priority = data.get("priority")
        if initial_priority is None:
            if src_list in (app.quadrant1_list, app.quadrant1_completed_list):
                initial_priority = 1

            elif src_list in (app.quadrant2_list, app.quadrant2_completed_list):
                initial_priority = 2

            elif src_list in (app.quadrant3_list, app.quadrant3_completed_list):
                initial_priority = 3

            elif src_list in (app.quadrant4_list, app.quadrant4_completed_list):
                initial_priority = 4

        dlg = EditTaskDialog(
            app,
            parent=app,
            initial_text=initial_text,
            initial_file=initial_file,
            initial_description=initial_desc,
            initial_date_iso=initial_date_iso,
            initial_time_str=initial_time_str,
            initial_priority=initial_priority,
        )
        if dlg.exec() != QDialog.Accepted:
            return

        new_text, new_file_path, new_desc, new_date_iso, new_time_str, new_priority = dlg.get_values()
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

        new_data["date"] = new_date_iso
        new_data["time"] = new_time_str
        new_data["priority"] = new_priority
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

        try:
            prio = new_data.get("priority")
            if prio is not None and prio != "":
                prio_text = prioridade_para_texto(prio, app)
                tooltip_lines.append((get_text("Prioridade") or "Prioridade") + f": {prio_text}")

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

        target_list = lst
        try:
            if isinstance(new_priority, int) and 1 <= new_priority <= 4:
                keep_completed = _is_completed_list(app, lst)
                target_list = _target_list_for_quadrant(app, new_priority - 1, keep_completed=keep_completed) or lst

        except Exception:
            target_list = lst

        row = lst.row(src_item if src_item is not None else item)
        check_state = (src_item if src_item is not None else item).checkState()
        lst.takeItem(row)

        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(lst)

        except Exception:
            pass

        try:
            def _has_selectable_items(q_list):
                for i in range(q_list.count()):
                    it = q_list.item(i)
                    if it and (it.flags() & Qt.ItemIsSelectable):
                        return True

                return False

            if not _has_selectable_items(lst):
                lst.clear()
                placeholders = {
                    app.quadrant1_list: get_text("1º Quadrante"),
                    app.quadrant2_list: get_text("2º Quadrante"),
                    app.quadrant3_list: get_text("3º Quadrante"),
                    app.quadrant4_list: get_text("4º Quadrante"),
                    app.quadrant1_completed_list: get_text("Nenhuma Tarefa Concluída"),
                    app.quadrant2_completed_list: get_text("Nenhuma Tarefa Concluída"),
                    app.quadrant3_completed_list: get_text("Nenhuma Tarefa Concluída"),
                    app.quadrant4_completed_list: get_text("Nenhuma Tarefa Concluída"),
                }
                app.add_placeholder(lst, placeholders.get(lst, get_text("Nenhuma Tarefa Concluída")))

        except Exception:
            pass

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

        if target_list.count() == 1 and not (target_list.item(0).flags() & Qt.ItemIsSelectable):
            target_list.clear()

        if hasattr(app, "insert_task_into_quadrant_list"):
            app.insert_task_into_quadrant_list(target_list, new_item)

        else:
            target_list.addItem(new_item)

        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(target_list)

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
