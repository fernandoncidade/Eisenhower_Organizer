from PySide6.QtWidgets import QHBoxLayout,QWidget, QSizePolicy
from PySide6.QtCore import Qt, QCoreApplication
from .ui_13_RotatedTabButton import RotatedTabButton
from .ui_14_CalendarPanel import CalendarPanel
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)


class Calendar(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._expanded = False
            self._panel_width = 360

            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 11, 0, 0)
            layout.setSpacing(0)

            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

            self.toggle_button = RotatedTabButton(get_text("Mostrar Calendário"), self)
            self.toggle_button.setMinimumWidth(25)
            layout.addWidget(self.toggle_button, 0, Qt.AlignLeft | Qt.AlignTop)

            self.calendar_panel = CalendarPanel(app, self)
            self.calendar_panel.setFixedWidth(self._panel_width)
            self.calendar_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            layout.addWidget(self.calendar_panel, 1)

            self.calendar_panel.setVisible(False)
            self._apply_fixed_width()

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self.on_language_changed)

        except Exception as e:
            logger.error(f"Erro ao inicializar Calendar: {e}", exc_info=True)

    def _apply_fixed_width(self):
        try:
            btn_w = self.toggle_button.width()
            total = btn_w + (self._panel_width if self._expanded else 0)
            self.setFixedWidth(total)

        except Exception as e:
            logger.error(f"Erro ao aplicar largura fixa: {e}", exc_info=True)

    def toggle_panel(self, open_if_hidden=False):
        try:
            previous = self._expanded
            if open_if_hidden and not self._expanded:
                self._expanded = True

            else:
                self._expanded = not self._expanded

            self.calendar_panel.setVisible(self._expanded)

            if self._expanded:
                hint_w = max(self.calendar_panel.sizeHint().width(), 300)
                self._panel_width = max(self._panel_width, hint_w)
                self.calendar_panel.setFixedWidth(self._panel_width)
                self.toggle_button.setText(get_text("Recolher Calendário"))

            else:
                self.toggle_button.setText(get_text("Mostrar Calendário"))

            self._apply_fixed_width()

            try:
                main_win = getattr(self, "app", None)
                if not main_win:
                    return

                if main_win.isMaximized():
                    try:
                        central = main_win.centralWidget()
                        if central:
                            central.updateGeometry()

                    except Exception:
                        pass

                    main_win.update()
                    return

                avail_w = None
                try:
                    wh = main_win.windowHandle()
                    if wh and wh.screen():
                        avail_w = wh.screen().availableGeometry().width()

                except Exception:
                    avail_w = None

                if avail_w is None:
                    try:
                        avail_w = main_win.screen().availableGeometry().width()

                    except Exception:
                        avail_w = 99999

                if self._expanded and not previous:
                    desired = main_win.width() + self._panel_width
                    new_w = min(desired, avail_w)
                    main_win.resize(new_w, main_win.height())

                elif (not self._expanded) and previous:
                    new_w = max(400, main_win.width() - self._panel_width)
                    main_win.resize(new_w, main_win.height())

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao alternar painel de calendário: {e}", exc_info=True)

    def on_language_changed(self):
        try:
            self.toggle_button.setText(get_text("Recolher Calendário") if self._expanded else get_text("Mostrar Calendário"))
            try:
                self.calendar_panel._on_language_changed()

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do calendário: {e}", exc_info=True)
