from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, Qt
from .mmc_05_is_completed_list import _is_completed_list
from .mmc_06_quadrant_options import _quadrant_options
from .mmc_07_target_list_for_quadrant import _target_list_for_quadrant
from .mmc_08_find_source_item_for_calendar import _find_source_item_for_calendar
from .mmc_11_edit_task_dialog import edit_task_dialog
from .mmc_12_move_to_quadrant import _move_to_quadrant
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def mostrar_menu_contexto(app, point, list_widget):
    try:
        item = list_widget.itemAt(point)
        if not item:
            return

        if not bool(item.flags() & Qt.ItemIsSelectable):
            return

        menu = QMenu(list_widget)
        selected_items = list_widget.selectedItems() or []

        if item not in selected_items:
            selected_items = [item]

        selected_items = [it for it in selected_items if it and (it.flags() & Qt.ItemIsSelectable)]

        def _resolve_item(it):
            try:
                data_for_resolution = it.data(Qt.UserRole) or {}
                if isinstance(data_for_resolution, dict) and data_for_resolution.get("category"):
                    src_list_for_move, src_item_for_move = _find_source_item_for_calendar(app, data_for_resolution)
                    if src_list_for_move is not None and src_item_for_move is not None:
                        return src_list_for_move, src_item_for_move, True

            except Exception:
                pass

            return list_widget, it, False

        def _edit_task():
            edit_task_dialog(app, item)

        editar_acao = QAction(get_text("✏️ Editar Tarefa") or "✏️ Editar Tarefa", app)
        editar_acao.triggered.connect(_edit_task)
        menu.addAction(editar_acao)

        try:
            opts = _quadrant_options(app)
            mover_menu = QMenu(get_text("🔀 Mover para outro quadrante"), app)

            for idx, label in enumerate(opts):
                a = QAction(label, app)
                def _make_handler(i):
                    def _handler():
                        try:
                            for it in selected_items:
                                source_list, source_item, _ = _resolve_item(it)
                                keep_completed = _is_completed_list(app, source_list)
                                target = _target_list_for_quadrant(app, i, keep_completed=keep_completed)
                                if target is None or target is source_list:
                                    continue

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
            mover_acao = QAction(get_text("🔀 Mover para outro quadrante"), app)
            mover_acao.triggered.connect(lambda: _move_to_quadrant(app, item, list_widget))
            menu.addAction(mover_acao)

        menu.addSeparator()
        remover_acao = QAction(get_text("🗑️ Remover Tarefa"), app)

        def _remove_selected():
            try:
                if not selected_items:
                    return

                if len(selected_items) == 1:
                    single_text = selected_items[0].text() if selected_items[0] is not None else ""
                    prompt = get_text("Deseja remover a tarefa '{item}'?").replace("{item}", single_text)

                else:
                    prompt = get_text("Deseja remover as tarefas selecionadas?") or "Deseja remover as tarefas selecionadas?"

                reply = QMessageBox.question(
                    app,
                    get_text("🗑️ Remover Tarefa"),
                    prompt,
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

                is_calendar_list = False

                try:
                    for it in selected_items:
                        d = it.data(Qt.UserRole)
                        if isinstance(d, dict) and d.get("category"):
                            is_calendar_list = True
                            break

                except Exception:
                    is_calendar_list = False

                try:
                    setattr(app, "_suppress_calendar_update", True)

                except Exception:
                    pass

                removed_count = 0
                failed_count = 0

                if is_calendar_list:
                    tasks_to_remove = []

                    for it in selected_items:
                        try:
                            d = it.data(Qt.UserRole)
                            if isinstance(d, dict) and d.get("category"):
                                tasks_to_remove.append(d)

                        except Exception:
                            continue

                    seen = set()

                    for task in tasks_to_remove:
                        try:
                            key = (
                                str(task.get("text") or "").strip(),
                                str(task.get("date") or ""),
                                str(task.get("time") or ""),
                                str(task.get("category") or ""),
                                bool(task.get("completed")),
                            )
                            if key in seen:
                                continue

                            seen.add(key)

                        except Exception:
                            pass

                        src_list_rem, src_item_rem = _find_source_item_for_calendar(app, task)

                        if src_list_rem is None or src_item_rem is None:
                            continue

                        try:
                            if app.remove_task(src_item_rem, src_list_rem, confirm=False):
                                removed_count += 1

                            else:
                                failed_count += 1

                        except Exception:
                            failed_count += 1

                else:
                    for it in selected_items:
                        src_list_rem, src_item_rem, _ = _resolve_item(it)

                        try:
                            if app.remove_task(src_item_rem, src_list_rem, confirm=False):
                                removed_count += 1

                            else:
                                failed_count += 1

                        except Exception:
                            failed_count += 1

                try:
                    app.save_tasks()

                except Exception:
                    pass

                try:
                    if hasattr(app, "calendar_pane") and app.calendar_pane:
                        app.calendar_pane.calendar_panel.update_task_list()

                except Exception:
                    pass

                try:
                    setattr(app, "_suppress_calendar_update", False)

                except Exception:
                    pass

                try:
                    if removed_count > 0 and failed_count == 0:
                        QMessageBox.information(
                            app,
                            get_text("🗑️ Remover Tarefa"),
                            get_text("Tarefa(s) removida(s) com sucesso.") or "Tarefa(s) removida(s) com sucesso.",
                        )
                    elif removed_count > 0:
                        QMessageBox.warning(
                            app,
                            get_text("🗑️ Remover Tarefa"),
                            get_text("Algumas tarefas nao puderam ser removidas.") or "Algumas tarefas nao puderam ser removidas.",
                        )
                    else:
                        QMessageBox.warning(
                            app,
                            get_text("🗑️ Remover Tarefa"),
                            get_text("Nao foi possivel remover as tarefas selecionadas.") or "Nao foi possivel remover as tarefas selecionadas.",
                        )

                except Exception:
                    pass

            except Exception:
                pass

        remover_acao.triggered.connect(_remove_selected)
        menu.addAction(remover_acao)
        menu.exec(list_widget.mapToGlobal(point))

    except Exception as e:
        logger.error(f"Erro ao exibir menu de contexto: {e}", exc_info=True)
