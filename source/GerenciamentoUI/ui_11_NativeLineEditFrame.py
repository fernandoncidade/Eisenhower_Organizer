from PySide6.QtWidgets import QVBoxLayout, QWidget, QStyle, QStyleOptionFrame
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPainter
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class NativeLineEditFrame(QWidget):
    def __init__(self, child: QWidget, parent=None):
        super().__init__(parent)
        try:
            self._child = child
            self._layout = QVBoxLayout(self)
            self._layout.setSpacing(0)
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.addWidget(self._child)
            self._update_margins_from_style()

        except Exception as e:
            logger.error(f"Erro ao inicializar NativeLineEditFrame: {e}", exc_info=True)

    def _frame_width(self) -> int:
        try:
            return int(self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, None, self))

        except Exception:
            return 2

    def _update_margins_from_style(self):
        try:
            fw = self._frame_width()
            self._layout.setContentsMargins(fw, fw, fw, fw)
            self.updateGeometry()
            self.update()

        except Exception as e:
            logger.error(f"Erro ao atualizar margens do frame nativo: {e}", exc_info=True)

    def changeEvent(self, event):
        try:
            if event and event.type() in (QEvent.StyleChange, QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
                self._update_margins_from_style()

            super().changeEvent(event)

        except Exception as e:
            logger.error(f"Erro ao processar changeEvent no frame nativo: {e}", exc_info=True)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            opt = QStyleOptionFrame()
            opt.initFrom(self)
            opt.rect = self.rect()
            opt.lineWidth = self._frame_width()
            opt.midLineWidth = 0
            opt.state |= QStyle.State_Sunken
            self.style().drawPrimitive(QStyle.PE_FrameLineEdit, opt, painter, self)

        except Exception as e:
            logger.error(f"Erro ao pintar frame nativo: {e}", exc_info=True)
