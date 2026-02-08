from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _add_placeholders_after_clear(self):
    try:
        self.app.add_placeholder(self.app.quadrant1_list, self.get_text("1º Quadrante"))
        self.app.add_placeholder(self.app.quadrant2_list, self.get_text("2º Quadrante"))
        self.app.add_placeholder(self.app.quadrant3_list, self.get_text("3º Quadrante"))
        self.app.add_placeholder(self.app.quadrant4_list, self.get_text("4º Quadrante"))
        self.app.add_placeholder(self.app.quadrant1_completed_list, self.get_text("Nenhuma Tarefa Concluída"))
        self.app.add_placeholder(self.app.quadrant2_completed_list, self.get_text("Nenhuma Tarefa Concluída"))
        self.app.add_placeholder(self.app.quadrant3_completed_list, self.get_text("Nenhuma Tarefa Concluída"))
        self.app.add_placeholder(self.app.quadrant4_completed_list, self.get_text("Nenhuma Tarefa Concluída"))

    except Exception as e:
        logger.error(f"Erro ao adicionar placeholders após limpar: {e}", exc_info=True)
