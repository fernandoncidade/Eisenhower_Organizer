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

        removed = False

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

        def _norm_text(value) -> str:
            return str(value or "").strip()

        def _norm_prio(value):
            try:
                return int(value)

            except Exception:
                return _norm_text(value)

        def _same_task(left: dict, right: dict) -> bool:
            return (
                _norm_text(left.get("text")) == _norm_text(right.get("text"))
                and _norm_text(left.get("date")) == _norm_text(right.get("date"))
                and _norm_text(left.get("time")) == _norm_text(right.get("time"))
                and _norm_text(left.get("file_path")) == _norm_text(right.get("file_path"))
                and _norm_text(left.get("description")) == _norm_text(right.get("description"))
                and _norm_prio(left.get("priority")) == _norm_prio(right.get("priority"))
            )

        removed_from_same_list = False

        try:
            if list_widget is not None:
                row = list_widget.row(item)
                if row >= 0:
                    list_widget.takeItem(row)
                    removed_from_same_list = True
                    removed = True

        except Exception:
            removed_from_same_list = False

        if not removed_from_same_list:
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
                            if _same_task(d, data):
                                qlst.takeItem(i)
                                removed = True

                                try:
                                    if hasattr(app, "cleanup_time_groups"):
                                        app.cleanup_time_groups(qlst)

                                except Exception:
                                    pass

                                raise StopIteration()

                        except StopIteration:
                            raise

                        except Exception:
                            continue

            except StopIteration:
                pass

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

        if confirm:
            try:
                if removed:
                    QMessageBox.information(
                        app,
                        get_text("🗑️ Remover Tarefa"),
                        get_text("Tarefa removida com sucesso.") or "Tarefa removida com sucesso.",
                    )
                else:
                    QMessageBox.warning(
                        app,
                        get_text("🗑️ Remover Tarefa"),
                        get_text("Nao foi possivel remover a tarefa.") or "Nao foi possivel remover a tarefa.",
                    )

            except Exception:
                pass

        return removed

    except Exception as e:
        logger.error(f"Erro ao remover tarefa: {e}", exc_info=True)
        return False
