from PySide6.QtCore import QLocale
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _effective_locale(app) -> QLocale:
    try:
        if hasattr(app, "date_input") and app.date_input is not None:
            return app.date_input.locale()

    except Exception as e:
        logger.error(f"Erro ao obter locale efetivo: {e}", exc_info=True)

    try:
        if hasattr(app, "gerenciador_traducao"):
            idioma = app.gerenciador_traducao.obter_idioma_atual()
            if idioma and idioma.startswith("pt"):
                return QLocale(QLocale.Portuguese, QLocale.Brazil)

            if idioma and idioma.startswith("en"):
                return QLocale(QLocale.English, QLocale.UnitedStates)

    except Exception as e:
        logger.error(f"Erro ao obter locale efetivo: {e}", exc_info=True)

    return QLocale.system()
