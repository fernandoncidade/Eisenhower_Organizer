from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

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
