from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QBrush, QColor, QFont
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _apply_highlighted_dates(self):
    try:
        new_dates = self._get_task_dates()
        if not hasattr(self, "_highlighted_dates"):
            self._highlighted_dates = set()

        to_clear = self._highlighted_dates - new_dates
        if to_clear:
            blank = QTextCharFormat()
            for ds in to_clear:
                qd = QDate.fromString(ds, Qt.ISODate)
                if qd.isValid():
                    self.calendar.setDateTextFormat(qd, blank)

        fmt = QTextCharFormat()
        pal = self.palette()
        base = pal.highlight().color()
        color = QColor(base.red(), base.green(), base.blue(), 60)
        fmt.setBackground(QBrush(color))
        fmt.setFontWeight(QFont.Bold)

        for ds in new_dates:
            qd = QDate.fromString(ds, Qt.ISODate)
            if qd.isValid():
                self.calendar.setDateTextFormat(qd, fmt)

        self._highlighted_dates = new_dates

    except Exception as e:
        logger.error(f"Erro ao aplicar destaque nas datas do calendário: {e}", exc_info=True)
