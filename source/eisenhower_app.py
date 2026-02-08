import os
from PySide6.QtCore import QCoreApplication, Qt, QTimer, QEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtGui import QFont, QColor, QPalette
from source.utils.IconUtils import get_icon_path
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.language.tr_01_gerenciadorTraducao import GerenciadorTraducao
from source.InterfaceCore import (
    init_ui as core_init_ui, 
    add_placeholder as core_add_placeholder, 
    criar_menu_configuracoes as core_criar_menu, 
    definir_idioma as core_definir_idioma, 
    atualizar_textos as core_atualizar_textos, 
    atualizar_placeholders as core_atualizar_placeholders, 
    show_context_menu as core_show_context_menu, 
    exibir_sobre as core_exibir_sobre, 
    Arquivo,
    prioridade_para_texto
)
from source.GerenciamentoUI import (
    add_task as ui_add_task, 
    handle_item_checked as ui_handle_item_checked, 
    move_item_between_lists as ui_move_item_between_lists, 
    remove_task as ui_remove_task, 
    save_tasks as ui_save_tasks, 
    load_tasks as ui_load_tasks, 
    Calendar, 
    edit_task_datetime as ui_edit_task_datetime, 
    move_task_to_quadrant as ui_move_task_to_quadrant
)
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)


class EisenhowerMatrixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gerenciador_traducao = GerenciadorTraducao()
        self.gerenciador_traducao.idioma_alterado.connect(self.atualizar_textos)
        self.gerenciador_traducao.aplicar_traducao()

        self.setWindowTitle(get_text("Matriz de Eisenhower - Organizador de Tarefas"))
        self.setMinimumSize(400, 200)
        self.resize(1000, 700)
        self.move(100, 100)

        icon_path = get_icon_path("organizador.ico")

        if icon_path:
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))

        self.tasks_path = os.path.join(obter_caminho_persistente(), "tasks.json")
        self.arquivo = Arquivo(self)

        self.initUI()

        try:
            self._apply_theme_palette()

        except Exception:
            pass

        self.load_tasks()
        self.criar_menu_configuracoes()
        QTimer.singleShot(0, self._clamp_window_to_screen)

    def closeEvent(self, event):
        try:
            for attr in ("_sobre_dialog", "_manual_dialog"):
                dlg = getattr(self, attr, None)
                if dlg is not None:
                    try:
                        dlg.close()

                    except Exception:
                        pass

        finally:
            super().closeEvent(event)

    def changeEvent(self, event):
        try:
            if event and event.type() in (
                QEvent.ApplicationPaletteChange,
                QEvent.PaletteChange,
                QEvent.StyleChange,
            ):
                QTimer.singleShot(0, self._apply_theme_palette)

        except Exception:
            pass

        super().changeEvent(event)

    def criar_menu_configuracoes(self):
        core_criar_menu(self)

    def definir_idioma(self, codigo_idioma):
        core_definir_idioma(self, codigo_idioma)

    def initUI(self):
        core_init_ui(self)
        try:
            old_central = self.centralWidget()
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            self.calendar_pane = Calendar(self)
            layout.addWidget(self.calendar_pane, 0, Qt.AlignLeft)
            layout.addWidget(old_central, 1)

            self.setCentralWidget(container)
            self._main_content = old_central
            self._root_container = container
            self._hide_legacy_calendar_button()

        except Exception as e:
            logger.error(f"Erro ao inicializar UI: {e}", exc_info=True)

    def _apply_theme_palette(self):
        def _apply_window_bg(widget, color):
            if widget is None:
                return

            try:
                pal = widget.palette()
                pal.setColor(QPalette.Window, color)
                widget.setAutoFillBackground(True)
                widget.setPalette(pal)

            except Exception:
                pass

        def _apply_list_bg(widget, color):
            if widget is None:
                return

            try:
                pal = widget.palette()
                pal.setColor(QPalette.Base, color)
                pal.setColor(QPalette.AlternateBase, color)
                widget.setPalette(pal)
                widget.setAutoFillBackground(True)

                try:
                    widget.viewport().setAutoFillBackground(True)

                except Exception:
                    pass

            except Exception:
                pass

        def _apply_input_bg(widget, color):
            if widget is None:
                return

            try:
                pal = widget.palette()
                pal.setColor(QPalette.Base, color)
                pal.setColor(QPalette.AlternateBase, color)

                if isinstance(widget, QComboBox):
                    pal.setColor(QPalette.Button, color)
                    pal.setColor(QPalette.Window, color)

                widget.setPalette(pal)

                if isinstance(widget, QComboBox):
                    view = widget.view()

                    if view is not None:
                        view_pal = view.palette()
                        view_pal.setColor(QPalette.Base, color)
                        view_pal.setColor(QPalette.AlternateBase, color)
                        view.setPalette(view_pal)

            except Exception:
                pass

        try:
            base_color = self.palette().color(QPalette.Window)
            main_color = QColor(base_color).lighter(120)
            list_color = QColor(base_color).darker(105)

            _apply_window_bg(getattr(self, "_root_container", None), main_color)
            _apply_window_bg(getattr(self, "_main_content", None), main_color)
            _apply_window_bg(getattr(self, "quadrant_tabs", None), main_color)
            _apply_window_bg(getattr(self, "quadrant1_tab", None), main_color)
            _apply_window_bg(getattr(self, "quadrant2_tab", None), main_color)
            _apply_window_bg(getattr(self, "quadrant3_tab", None), main_color)
            _apply_window_bg(getattr(self, "quadrant4_tab", None), main_color)

            for label_name in (
                "quadrant1_label",
                "quadrant2_label",
                "quadrant3_label",
                "quadrant4_label",
                "quadrant1_completed_label",
                "quadrant2_completed_label",
                "quadrant3_completed_label",
                "quadrant4_completed_label",
            ):
                _apply_window_bg(getattr(self, label_name, None), main_color)

            for list_name in (
                "quadrant1_list",
                "quadrant2_list",
                "quadrant3_list",
                "quadrant4_list",
                "quadrant1_completed_list",
                "quadrant2_completed_list",
                "quadrant3_completed_list",
                "quadrant4_completed_list",
            ):
                _apply_list_bg(getattr(self, list_name, None), list_color)

            for input_name in (
                "task_input",
                "date_input",
                "time_input",
                "quadrant_selector",
            ):
                _apply_input_bg(getattr(self, input_name, None), list_color)

            try:
                panel = self.calendar_pane.calendar_panel if hasattr(self, "calendar_pane") and self.calendar_pane else None
                _apply_window_bg(panel, main_color)
                _apply_window_bg(getattr(panel, "tasks_label", None), main_color)
                _apply_list_bg(getattr(panel, "tasks_list", None), list_color)
                _apply_input_bg(getattr(panel, "filter_combo", None), list_color)

            except Exception:
                pass

            try:
                tabs = getattr(self, "quadrant_tabs", None)

                if tabs is not None:
                    tab_bar = tabs.tabBar()

                    if tab_bar is not None:
                        tab_bar.update()

                    if hasattr(tabs, "refresh_quadrant_style"):
                        tabs.refresh_quadrant_style()

            except Exception:
                pass

        except Exception:
            pass

    def _hide_legacy_calendar_button(self):
        try:
            for btn in self.findChildren(QPushButton):
                if btn.text().strip().lower() in {
                    get_text("Calendário").strip().lower(),
                    "calendário", "calendario", "calendar"
                }:
                    btn.hide()

        except Exception as e:
            logger.error(f"Erro ao ocultar botão legado do calendário: {e}", exc_info=True)

    def _clamp_window_to_screen(self):
        try:
            wh = self.windowHandle()
            screen = wh.screen() if wh and wh.screen() else self.screen()
            if screen is None:
                return

            avail = screen.availableGeometry()
            geo = self.geometry()
            new_w = min(geo.width(), avail.width())
            new_h = min(geo.height(), avail.height())
            new_x = max(avail.x(), min(geo.x(), avail.x() + avail.width() - new_w))
            new_y = max(avail.y(), min(geo.y(), avail.y() + avail.height() - new_h))

            if new_w != geo.width() or new_h != geo.height():
                self.resize(new_w, new_h)

            if new_x != geo.x() or new_y != geo.y():
                self.move(new_x, new_y)

        except Exception as e:
            logger.error(f"Erro ao ajustar janela ao monitor: {e}", exc_info=True)

    def add_placeholder(self, list_widget, text):
        core_add_placeholder(self, list_widget, text)

    def _is_group_header(self, item):
        try:
            return item.data(Qt.UserRole + 1) == "group_header"

        except Exception:
            return False

    def _time_group_label(self, time_str: str) -> str:
        try:
            hh = int((time_str or "0:0").split(":")[0])

        except Exception:
            hh = 0

        return f"{hh:02d}:00–{hh:02d}:59"

    def _time_key(self, time_str: str):
        if not time_str:
            return (999, 999)

        try:
            parts = time_str.split(":")
            return (int(parts[0]), int(parts[1]))

        except Exception:
            return (999, 999)

    def insert_task_into_quadrant_list(self, lst, item):
        data = item.data(Qt.UserRole) or {}
        time_str = data.get("time")
        if not time_str:
            try:
                tooltip_lines = []
                fp = data.get("file_path")
                if fp:
                    tooltip_lines.append((get_text("Arquivo") or "Arquivo") + f": {fp}")
                    try:
                        font = item.font() or QFont()
                        font.setBold(True)
                        item.setFont(font)

                        try:
                            item.setForeground(Qt.blue)

                        except Exception:
                            pass

                    except Exception:
                        pass

                ds = data.get("date")
                if ds:
                    try:
                        from PySide6.QtCore import QDate
                        qd = QDate.fromString(ds, Qt.ISODate)
                        if qd.isValid() and hasattr(self, "date_input"):
                            date_human = qd.toString(self.date_input.displayFormat())

                        else:
                            date_human = ds

                    except Exception:
                        date_human = ds

                    tooltip_lines.append((get_text("Data") or "Data") + f": {date_human}")

                if time_str:
                    tooltip_lines.append((get_text("Horário") or "Horário") + f": {time_str}")

                desc = data.get("description")
                if desc:
                    tooltip_lines.append((get_text("Descrição") or "Descrição") + f": {desc}")

                prio = data.get("priority")
                if prio is not None and prio != "":
                    prio_text = prioridade_para_texto(prio, self)
                    tooltip_lines.append((get_text("Prioridade") or "Prioridade") + f": {prio_text}")

                if tooltip_lines:
                    try:
                        item.setToolTip("\n".join(tooltip_lines))

                    except Exception:
                        pass

            except Exception:
                pass

            lst.addItem(item)
            return

        if lst.count() == 1 and not (lst.item(0).flags() & Qt.ItemIsSelectable):
            lst.clear()

        label = self._time_group_label(time_str)

        header_index = None
        insert_header_index = None
        existing_headers = []
        for i in range(lst.count()):
            it = lst.item(i)
            if not it:
                continue

            if self._is_group_header(it):
                existing_headers.append((i, it.text()))

        for idx, text in existing_headers:
            if text == label:
                header_index = idx
                break

        if header_index is None:
            try:
                hour = int(label.split(":")[0])

            except Exception:
                hour = 0

            insert_header_index = lst.count()
            for idx, text in existing_headers:
                try:
                    h2 = int(text.split(":")[0])

                except Exception:
                    h2 = 0

                if hour < h2:
                    insert_header_index = idx
                    break

            from PySide6.QtWidgets import QListWidgetItem
            header = QListWidgetItem(label)
            from PySide6.QtCore import Qt as _Qt
            header.setFlags((header.flags() & ~_Qt.ItemIsSelectable) & ~_Qt.ItemIsEnabled)
            header.setData(_Qt.UserRole + 1, "group_header")
            lst.insertItem(insert_header_index, header)
            header_index = insert_header_index

        start = header_index + 1
        end = lst.count()
        for i in range(start, lst.count()):
            it = lst.item(i)
            if it and self._is_group_header(it):
                end = i
                break

        new_key = (self._time_key(time_str), (data.get("text") or item.text()).lower())
        pos = end
        for i in range(start, end):
            it = lst.item(i)
            idata = it.data(Qt.UserRole) or {}
            ikey = (self._time_key(idata.get("time")), (idata.get("text") or it.text()).lower())
            if new_key < ikey:
                pos = i
                break

        try:
            tooltip_lines = []
            fp = data.get("file_path")
            if fp:
                tooltip_lines.append((get_text("Arquivo") or "Arquivo") + f": {fp}")
                try:
                    font = item.font() or QFont()
                    font.setBold(True)
                    item.setFont(font)

                    try:
                        item.setForeground(Qt.blue)

                    except Exception:
                        pass

                except Exception:
                    pass

            ds = data.get("date")
            if ds:
                try:
                    from PySide6.QtCore import QDate
                    qd = QDate.fromString(ds, Qt.ISODate)
                    if qd.isValid() and hasattr(self, "date_input"):
                        date_human = qd.toString(self.date_input.displayFormat())

                    else:
                        date_human = ds

                except Exception:
                    date_human = ds

                tooltip_lines.append((get_text("Data") or "Data") + f": {date_human}")

            if time_str:
                tooltip_lines.append((get_text("Horário") or "Horário") + f": {time_str}")

            desc = data.get("description")
            if desc:
                tooltip_lines.append((get_text("Descrição") or "Descrição") + f": {desc}")

            prio = data.get("priority")
            if prio is not None and prio != "":
                prio_text = prioridade_para_texto(prio, self)
                tooltip_lines.append((get_text("Prioridade") or "Prioridade") + f": {prio_text}")

            if tooltip_lines:
                try:
                    item.setToolTip("\n".join(tooltip_lines))

                except Exception:
                    pass

        except Exception:
            pass

        lst.insertItem(pos, item)

    def cleanup_time_groups(self, lst):
        i = 0
        from PySide6.QtCore import Qt as _Qt
        while i < lst.count():
            it = lst.item(i)
            if it and self._is_group_header(it):
                if i + 1 >= lst.count() or self._is_group_header(lst.item(i + 1)) or (lst.item(i + 1).flags() & _Qt.ItemIsSelectable) == 0:
                    j = i + 1
                    found_task = False
                    while j < lst.count():
                        it2 = lst.item(j)
                        if self._is_group_header(it2):
                            break

                        if it2.flags() & _Qt.ItemIsSelectable:
                            found_task = True
                            break

                        j += 1

                    if not found_task:
                        lst.takeItem(i)
                        continue

            i += 1

    def add_task(self):
        ui_add_task(self)
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas no calendário: {e}", exc_info=True)

    def handle_item_checked(self, item, source_list, target_list):
        ui_handle_item_checked(self, item, source_list, target_list)

    def move_item_between_lists(self, item, source, target, new_check_state):
        ui_move_item_between_lists(self, item, source, target, new_check_state)

    def remove_task(self, item, list_widget, confirm: bool = True):
        try:
            removed = ui_remove_task(self, item, list_widget, confirm)

        except Exception as e:
            logger.error(f"Erro ao chamar utilitário remove_task: {e}", exc_info=True)
            removed = False

        try:
            self.cleanup_time_groups(list_widget)
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao remover tarefa: {e}", exc_info=True)

        return removed

    def save_tasks(self):
        ui_save_tasks(self)

    def load_tasks(self):
        ui_load_tasks(self)
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao carregar tarefas: {e}", exc_info=True)

    def atualizar_textos(self):
        def _apply_updates():
            try:
                core_atualizar_textos(self)
                if hasattr(self, "calendar_pane") and self.calendar_pane:
                    self.calendar_pane.on_language_changed()

            except Exception as e:
                logger.error(f"Erro ao atualizar textos: {e}", exc_info=True)

        try:
            QTimer.singleShot(0, _apply_updates)

        except Exception:
            _apply_updates()

    def atualizar_placeholders(self):
        core_atualizar_placeholders(self)

    def exibir_sobre(self):
        core_exibir_sobre(self)

    def show_context_menu(self, point, list_widget):
        core_show_context_menu(self, point, list_widget)

    def open_calendar(self):
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.toggle_panel(open_if_hidden=True)

        except Exception as e:
            logger.error(f"Erro ao abrir calendário: {e}", exc_info=True)

    def nova_sessao(self):
        self.arquivo.novo()

    def abrir_arquivo(self):
        self.arquivo.abrir_arquivo()

    def salvar_como(self):
        self.arquivo.salvar_como()

    def limpar_tudo(self):
        self.arquivo.limpar_tudo()

    def sair_app(self):
        self.arquivo.sair()

    def edit_task_datetime(self, item, list_widget):
        ui_edit_task_datetime(self, item, list_widget)

    def move_task_to_quadrant(self, item, source_list, target_list):
        ui_move_task_to_quadrant(self, item, source_list, target_list)
