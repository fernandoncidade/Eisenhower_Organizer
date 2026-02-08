from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def closeEvent(self, event):
    try:
        if hasattr(self.app, "gerenciador_traducao"):
            try:
                self.app.gerenciador_traducao.idioma_alterado.disconnect(self._on_language_changed)

            except (RuntimeError, TypeError):
                pass

        super().closeEvent(event)

    except Exception as e:
        logger.error(f"Erro ao fechar CalendarDialog: {e}", exc_info=True)
