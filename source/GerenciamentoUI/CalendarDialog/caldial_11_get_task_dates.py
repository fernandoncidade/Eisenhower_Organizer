from PySide6.QtCore import Qt, QDate
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _get_task_dates(self):
    dates = set()
    try:
        for task in self._collect_tasks():
            ds = task.get("date")
            if not ds:
                continue

            qd = QDate.fromString(ds, Qt.ISODate)
            if qd.isValid():
                dates.add(qd.toString(Qt.ISODate))

    except Exception as e:
        logger.error(f"Erro ao obter datas das tarefas do calendário: {e}", exc_info=True)

    return dates
