from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QLocale
from source.InterfaceCore.MostrarMenuContexto import (
    _compute_widget_height as _mmc_compute_widget_height,
    _apply_widget_min_height as _mmc_apply_widget_min_height,
    _effective_locale as _mmc_effective_locale,
    _apply_locale_to_dateedit as _mmc_apply_locale_to_dateedit,
    _is_completed_list as _mmc_is_completed_list,
    _quadrant_options as _mmc_quadrant_options,
    _target_list_for_quadrant as _mmc_target_list_for_quadrant,
    _find_source_item_for_calendar as _mmc_find_source_item_for_calendar,
    _base_text_from_item as _mmc_base_text_from_item,
    _build_display_and_tooltip as _mmc_build_display_and_tooltip,
    edit_task_dialog as _mmc_edit_task_dialog,
    _move_to_quadrant as _mmc_move_to_quadrant,
    mostrar_menu_contexto as _mmc_mostrar_menu_contexto,
)
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class MostrarMenuContexto:
    @staticmethod
    def _compute_widget_height(app, widget, name: str | None = None) -> int:
        return _mmc_compute_widget_height(app, widget, name)

    @staticmethod
    def _apply_widget_min_height(app, widget, name: str | None = None):
        return _mmc_apply_widget_min_height(app, widget, name)

    @staticmethod
    def _effective_locale(app) -> QLocale:
        return _mmc_effective_locale(app)

    @staticmethod
    def _apply_locale_to_dateedit(app, de: QDateEdit):
        return _mmc_apply_locale_to_dateedit(app, de)

    @staticmethod
    def _is_completed_list(app, lst) -> bool:
        return _mmc_is_completed_list(app, lst)

    @staticmethod
    def _quadrant_options(app):
        return _mmc_quadrant_options(app)

    @staticmethod
    def _target_list_for_quadrant(app, quadrant_index: int, keep_completed: bool):
        return _mmc_target_list_for_quadrant(app, quadrant_index, keep_completed)

    @staticmethod
    def _find_source_item_for_calendar(app, task_dict):
        return _mmc_find_source_item_for_calendar(app, task_dict)

    @staticmethod
    def _base_text_from_item(item) -> str:
        return _mmc_base_text_from_item(item)

    @staticmethod
    def _build_display_and_tooltip(app, base_text: str, date_iso: str | None, time_str: str | None):
        return _mmc_build_display_and_tooltip(app, base_text, date_iso, time_str)

    @staticmethod
    def edit_task_dialog(app, item):
        return _mmc_edit_task_dialog(app, item)

    @staticmethod
    def _move_to_quadrant(app, item, source_list):
        return _mmc_move_to_quadrant(app, item, source_list)

    @staticmethod
    def mostrar_menu_contexto(app, point, list_widget):
        return _mmc_mostrar_menu_contexto(app, point, list_widget)


def show_context_menu(app, point, list_widget):
    return MostrarMenuContexto.mostrar_menu_contexto(app, point, list_widget)

def _find_source_item_for_calendar(app, task_dict):
    return MostrarMenuContexto._find_source_item_for_calendar(app, task_dict)

def edit_task_dialog(app, item):
    return MostrarMenuContexto.edit_task_dialog(app, item)
