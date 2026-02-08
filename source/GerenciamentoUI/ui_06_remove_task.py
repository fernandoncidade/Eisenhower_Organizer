from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication, Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _list_has_selectable_items(lst) -> bool:
    try:
        for i in range(lst.count()):
            it = lst.item(i)
            if it and (it.flags() & Qt.ItemIsSelectable):
                return True

        return False

    except Exception:
        return False

def _ensure_placeholder(app, lst, placeholder_text: str):
    try:
        if lst is None:
            return

        if not _list_has_selectable_items(lst):
            lst.blockSignals(True)
            try:
                lst.clear()
                app.add_placeholder(lst, placeholder_text)

            finally:
                lst.blockSignals(False)

            return

        return

    except Exception as e:
        logger.debug(f"Falha ao garantir placeholder: {e}", exc_info=True)

def _garantir_placeholders_em_todas_as_listas(app):
    try:
        _ensure_placeholder(app, getattr(app, "quadrant1_list", None), get_text("1º Quadrante"))
        _ensure_placeholder(app, getattr(app, "quadrant2_list", None), get_text("2º Quadrante"))
        _ensure_placeholder(app, getattr(app, "quadrant3_list", None), get_text("3º Quadrante"))
        _ensure_placeholder(app, getattr(app, "quadrant4_list", None), get_text("4º Quadrante"))
        _ensure_placeholder(app, getattr(app, "quadrant1_completed_list", None), get_text("Nenhuma Tarefa Concluída"))
        _ensure_placeholder(app, getattr(app, "quadrant2_completed_list", None), get_text("Nenhuma Tarefa Concluída"))
        _ensure_placeholder(app, getattr(app, "quadrant3_completed_list", None), get_text("Nenhuma Tarefa Concluída"))
        _ensure_placeholder(app, getattr(app, "quadrant4_completed_list", None), get_text("Nenhuma Tarefa Concluída"))

    except Exception as e:
        logger.debug(f"Falha ao garantir placeholders globais: {e}", exc_info=True)

def remove_task(app, item, list_widget, confirm: bool = True) -> bool:
    try:
        if not item or not (item.flags() & Qt.ItemIsSelectable):
            return False

        if confirm:
            msg = QMessageBox(app)
            msg.setWindowTitle(get_text("🗑️ Remover Tarefa"))
            msg.setText(get_text("Deseja remover a tarefa '{item}'?").replace("{item}", item.text()))
            btn_yes = msg.addButton(get_text("Yes"), QMessageBox.YesRole)
            btn_no = msg.addButton(get_text("No"), QMessageBox.NoRole)
            msg.exec()

            if msg.clickedButton() != btn_yes:
                return False

        data = item.data(Qt.UserRole) or {}
        removed_from_same_list = False
        try:
            quadrant_lists = [
                getattr(app, "quadrant1_list", None),
                getattr(app, "quadrant2_list", None),
                getattr(app, "quadrant3_list", None),
                getattr(app, "quadrant4_list", None),
                getattr(app, "quadrant1_completed_list", None),
                getattr(app, "quadrant2_completed_list", None),
                getattr(app, "quadrant3_completed_list", None),
                getattr(app, "quadrant4_completed_list", None),
            ]

            for qlst in quadrant_lists:
                if qlst is None:
                    continue

                for i in range(qlst.count()):
                    it = qlst.item(i)
                    if not it:
                        continue

                    if not (it.flags() & Qt.ItemIsSelectable):
                        continue

                    d = it.data(Qt.UserRole) or {}
                    try:
                        if str(d.get("text") or "").strip() == str(data.get("text") or "").strip() and (d.get("date") or "") == (data.get("date") or "") and (d.get("time") or "") == (data.get("time") or ""):
                            if qlst is list_widget and it is item:
                                removed_from_same_list = True
                                qlst.takeItem(i)

                            else:
                                qlst.takeItem(i)

                            try:
                                if hasattr(app, "cleanup_time_groups"):
                                    app.cleanup_time_groups(qlst)

                            except Exception:
                                pass

                            break

                    except Exception:
                        continue

        except Exception:
            pass

        if not removed_from_same_list:
            try:
                list_widget.takeItem(list_widget.row(item))

            except Exception:
                pass

        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(list_widget)

        except Exception:
            pass

        _garantir_placeholders_em_todas_as_listas(app)

        try:
            app.save_tasks()

        except Exception:
            pass

        try:
            if not getattr(app, "_suppress_calendar_update", False):
                if hasattr(app, "calendar_pane") and app.calendar_pane:
                    app.calendar_pane.calendar_panel.update_task_list()

        except Exception:
            pass

        return True

    except Exception as e:
        logger.error(f"Erro ao remover tarefa: {e}", exc_info=True)
        return False
