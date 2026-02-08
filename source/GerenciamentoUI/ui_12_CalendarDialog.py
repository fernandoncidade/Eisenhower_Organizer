from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QListWidget, QCheckBox, QLabel, QHBoxLayout, QAbstractItemView, QSizePolicy
from PySide6.QtCore import Qt, QDate, QCoreApplication, QSize
from PySide6.QtGui import QPalette, QColor
from .ui_10_BadgeCalendarWidget import BadgeCalendarWidget
from .ui_11_NativeLineEditFrame import NativeLineEditFrame
from source.InterfaceCore.incore_07_MostrarMenuContexto import show_context_menu
from source.GerenciamentoUI.CalendarDialog import (
    closeEvent,
    _open_linked_file,
    _collect_tasks,
    update_task_list,
    _on_calendar_context_menu,
    _prompt_edit_task_for_date,
    _prompt_remove_task_for_date,
    _update_badge_counts,
    _on_language_changed,
    _apply_locale_to_calendar,
    _get_task_dates,
    _apply_highlighted_dates
)
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)


class CalendarDialog(QDialog):
    def __init__(self, app):
        super().__init__(app)
        try:
            self.app = app
            self.setModal(True)
            self.setWindowTitle(get_text("Calendário de Tarefas"))
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
                self.tasks_list.itemDoubleClicked.connect(self._open_linked_file)

            except Exception:
                pass

            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarDialog: {e}", exc_info=True)

    def closeEvent(self, event):
        return closeEvent(self, event)

    def _open_linked_file(self, item):
        return _open_linked_file(self, item)

    def _collect_tasks(self):
        return _collect_tasks(self)

    def update_task_list(self):
        return update_task_list(self)

    def _on_calendar_context_menu(self, pos):
        return _on_calendar_context_menu(self, pos)

    def _prompt_edit_task_for_date(self, qdate: QDate):
        return _prompt_edit_task_for_date(self, qdate)

    def _prompt_remove_task_for_date(self, qdate: QDate):
        return _prompt_remove_task_for_date(self, qdate)

    def _update_badge_counts(self):
        return _update_badge_counts(self)

    def _on_language_changed(self):
        return _on_language_changed(self)

    def _apply_locale_to_calendar(self):
        return _apply_locale_to_calendar(self)

    def _get_task_dates(self):
        return _get_task_dates(self)

    def _apply_highlighted_dates(self):
        return _apply_highlighted_dates(self)
