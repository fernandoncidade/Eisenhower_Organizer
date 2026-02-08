from PySide6.QtCore import QCoreApplication
from source.InterfaceCore.Arquivo import (
    _clear_all_lists,
    _add_placeholders_after_clear,
    novo,
    limpar_tudo,
    _parse_text_date_time,
    abrir_arquivo,
    salvar_como,
)


class Arquivo:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def get_text(text):
        return QCoreApplication.translate("InterfaceGrafica", text)

    def _clear_all_lists(self):
        return _clear_all_lists(self)

    def _add_placeholders_after_clear(self):
        return _add_placeholders_after_clear(self)

    def novo(self):
        return novo(self)

    def limpar_tudo(self):
        return limpar_tudo(self)

    def sair(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def _parse_text_date_time(self, raw_text: str):
        return _parse_text_date_time(self, raw_text)

    def abrir_arquivo(self):
        return abrir_arquivo(self)

    def salvar_como(self):
        return salvar_como(self)
