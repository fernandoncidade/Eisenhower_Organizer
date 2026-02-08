from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def novo(self):
    self._clear_all_lists()
    self._add_placeholders_after_clear()
    self.app.task_input.clear()

    try:
        self.app.save_tasks()

        if hasattr(self.app, "calendar_pane") and self.app.calendar_pane:
            self.app.calendar_pane.calendar_panel.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao iniciar nova sessão: {e}", exc_info=True)

    QMessageBox.information(self.app, self.get_text("Novo"), self.get_text("Nova sessão iniciada.") or "Nova sessão iniciada.")
