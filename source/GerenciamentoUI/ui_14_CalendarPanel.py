from PySide6.QtWidgets import QVBoxLayout, QComboBox, QListWidget, QCheckBox, QLabel, QHBoxLayout, QAbstractItemView, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QDate, QCoreApplication, QSize
from PySide6.QtGui import QPalette, QColor
from .ui_10_BadgeCalendarWidget import BadgeCalendarWidget
from .ui_11_NativeLineEditFrame import NativeLineEditFrame
from .ui_12_CalendarDialog import CalendarDialog
from source.InterfaceCore.incore_07_MostrarMenuContexto import show_context_menu
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)


class CalendarPanel(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._date_format = app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy"
            self._highlighted_dates = set()

            def _apply_window_bg(widget, color):
                try:
                    pal = widget.palette()
                    pal.setColor(QPalette.Window, color)
                    widget.setAutoFillBackground(True)
                    widget.setPalette(pal)

                except Exception:
                    pass

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(5, 1, 5, 9)
            main_layout.setSpacing(6)

            try:
                base_color = self.app.palette().color(QPalette.Window)
                header_color = QColor(base_color).lighter(120)
                _apply_window_bg(self, header_color)

            except Exception:
                pass

            self.calendar = BadgeCalendarWidget(self)
            initial_date = app.date_input.date() if hasattr(app, "date_input") else QDate.currentDate()
            self.calendar.setSelectedDate(initial_date)
            self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.calendar.customContextMenuRequested.connect(self._on_calendar_context_menu)

            hint = self.calendar.minimumSizeHint()
            fallback = QSize(300, 260)

            self.calendar_frame = NativeLineEditFrame(self.calendar, self)
            self.calendar_frame.setMinimumSize(hint.expandedTo(fallback))
            self.calendar_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self._apply_locale_to_calendar()
            main_layout.addWidget(self.calendar_frame)

            controls_layout = QHBoxLayout()
            self.filter_label = QLabel(get_text("Exibir por"), self)
            controls_layout.addWidget(self.filter_label)

            self.filter_combo = QComboBox(self)
            self.filter_combo.addItem(get_text("Dia"), "day")
            self.filter_combo.addItem(get_text("Semana"), "week")
            self.filter_combo.addItem(get_text("Mês"), "month")
            controls_layout.addWidget(self.filter_combo)
            controls_layout.addStretch()
            self.show_priority_checkbox = QCheckBox(get_text("Mostrar prioridade"), self)
            self.show_priority_checkbox.setChecked(True)
            self.show_priority_checkbox.stateChanged.connect(self.update_task_list)
            controls_layout.addWidget(self.show_priority_checkbox)
            main_layout.addLayout(controls_layout)

            self.tasks_label = QLabel(get_text("Lista Global de Tarefas:"), self)

            try:
                base_color = self.app.palette().color(QPalette.Window)
                header_color = QColor(base_color).lighter(120)
                _apply_window_bg(self.tasks_label, header_color)

            except Exception:
                pass

            main_layout.addWidget(self.tasks_label)

            self.tasks_list = QListWidget(self)
            self.tasks_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.tasks_list.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.tasks_list.setSelectionRectVisible(True)
            self.tasks_list.setDragEnabled(False)
            self.tasks_list.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.tasks_list.setMouseTracking(True)
            self.tasks_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tasks_list.customContextMenuRequested.connect(lambda pt: show_context_menu(self.app, pt, self.tasks_list))

            try:
                base_color = self.app.palette().color(QPalette.Window)
                pal = self.tasks_list.palette()
                pal.setColor(QPalette.Base, base_color)
                pal.setColor(QPalette.AlternateBase, base_color)
                self.tasks_list.setPalette(pal)
                self.tasks_list.setAutoFillBackground(True)

                try:
                    self.tasks_list.viewport().setAutoFillBackground(True)

                except Exception:
                    pass

            except Exception:
                pass

            try:
                self.tasks_list.itemDoubleClicked.connect(lambda item: CalendarDialog._open_linked_file(self, item))

            except Exception:
                pass

            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarPanel: {e}", exc_info=True)

    def _collect_tasks(self):
        try:
            return CalendarDialog._collect_tasks(self)

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas: {e}", exc_info=True)

    def update_task_list(self):
        try:
            return CalendarDialog.update_task_list(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas: {e}", exc_info=True)

    def _update_badge_counts(self):
        try:
            return CalendarDialog._update_badge_counts(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)

    def _get_task_dates(self):
        try:
            return CalendarDialog._get_task_dates(self)

        except Exception as e:
            logger.error(f"Erro ao obter datas de tarefas: {e}", exc_info=True)

    def _apply_highlighted_dates(self):
        try:
            return CalendarDialog._apply_highlighted_dates(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar datas destacadas: {e}", exc_info=True)

    def _on_language_changed(self):
        try:
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
            logger.error(f"Erro ao atualizar idioma do painel de calendário: {e}", exc_info=True)

    def _apply_locale_to_calendar(self):
        try:
            return CalendarDialog._apply_locale_to_calendar(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar locale ao calendário: {e}", exc_info=True)

    def _on_calendar_context_menu(self, pos):
        try:
            return CalendarDialog._on_calendar_context_menu(self, pos)

        except Exception as e:
            logger.error(f"Erro ao abrir menu de contexto do calendário (painel): {e}", exc_info=True)

    def _prompt_edit_task_for_date(self, qdate: QDate):
        try:
            return CalendarDialog._prompt_edit_task_for_date(self, qdate)

        except Exception as e:
            logger.error(f"Erro ao editar tarefa do calendário (painel): {e}", exc_info=True)

    def _prompt_remove_task_for_date(self, qdate: QDate):
        try:
            return CalendarDialog._prompt_remove_task_for_date(self, qdate)

        except Exception as e:
            logger.error(f"Erro ao remover tarefa do calendário (painel): {e}", exc_info=True)
