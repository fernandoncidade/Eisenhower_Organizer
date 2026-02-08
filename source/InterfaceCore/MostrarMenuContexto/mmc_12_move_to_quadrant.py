from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import QCoreApplication, Qt
from .mmc_05_is_completed_list import _is_completed_list
from .mmc_06_quadrant_options import _quadrant_options
from .mmc_07_target_list_for_quadrant import _target_list_for_quadrant
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

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
