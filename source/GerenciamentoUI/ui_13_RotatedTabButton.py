from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QFontMetrics
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class RotatedTabButton(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        try:
            self._text = text
            self.setMinimumWidth(25)
            self._recompute_size()

        except Exception as e:
            logger.error(f"Erro ao inicializar RotatedTabButton: {e}", exc_info=True)

    def setText(self, text):
        try:
            self._text = text
            self._recompute_size()
            self.update()

        except Exception as e:
            logger.error(f"Erro ao definir texto do botão de aba: {e}", exc_info=True)

    def text(self):
        try:
            return self._text

        except Exception as e:
            logger.error(f"Erro ao obter texto do botão de aba: {e}", exc_info=True)

    def _recompute_size(self):
        try:
            fm = QFontMetrics(self.font())
            text_w = fm.horizontalAdvance(self._text)
            text_h = fm.height()
            width = text_h + 5
            height = text_w + 20
            self.setFixedSize(QSize(width, height))

        except Exception as e:
            logger.error(f"Erro ao recalcular tamanho do botão de aba: {e}", exc_info=True)

    def mousePressEvent(self, event):
        try:
            self.parent().toggle_panel()
            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"Erro ao processar evento de clique no botão de aba: {e}", exc_info=True)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.save()
            painter.fillRect(self.rect(), self.palette().button().color())
            painter.setPen(self.palette().dark().color())
            painter.drawRect(0, 0, self.width()-1, self.height()-1)
            painter.translate(0, self.height())
            painter.rotate(270)
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(self._text)
            x = (self.height() - text_w) / 2
            y = (self.width() + fm.ascent() - fm.descent()) / 2
            painter.setPen(self.palette().buttonText().color())
            painter.drawText(x, y, self._text)
            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao pintar botão de aba: {e}", exc_info=True)
