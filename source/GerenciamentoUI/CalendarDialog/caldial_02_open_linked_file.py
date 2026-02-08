from PySide6.QtCore import Qt, QCoreApplication, QUrl
from PySide6.QtGui import QDesktopServices
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _open_linked_file(self, item):
    try:
        if item is None:
            return

        data = item.data(Qt.UserRole) or {}
        path = data.get("file_path")
        if not path:
            return

        import os, subprocess, sys

        try:
            if QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                return

        except Exception:
            pass

        try:
            if os.path.exists(path):
                if sys.platform.startswith("win"):
                    os.startfile(path)
                    return

                elif sys.platform.startswith("darwin"):
                    subprocess.Popen(["open", path])
                    return

                else:
                    subprocess.Popen(["xdg-open", path])
                    return

        except Exception as e:
            logger.error(f"Falha ao abrir arquivo vinculado via fallback: {e}", exc_info=True)

        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, get_text("Erro"), get_text("Arquivo não encontrado."))

        except Exception:
            pass

    except Exception as e:
        logger.error(f"Erro ao abrir arquivo vinculado (Calendar): {e}", exc_info=True)
