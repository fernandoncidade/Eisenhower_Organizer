from PySide6.QtCore import Qt, QLocale
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _apply_locale_to_calendar(self):
    try:
        idioma = None
        if hasattr(self.app, "gerenciador_traducao"):
            idioma = self.app.gerenciador_traducao.obter_idioma_atual()

        if idioma and idioma.startswith("pt"):
            locale = QLocale(QLocale.Portuguese, QLocale.Brazil)

        elif idioma and idioma.startswith("en"):
            locale = QLocale(QLocale.English, QLocale.UnitedStates)

        else:
            locale = QLocale.system()

        self.calendar.setLocale(locale)
        self.calendar.setFirstDayOfWeek(Qt.Sunday)

    except Exception as e:
        logger.error(f"Erro ao aplicar localidade no calendário: {e}", exc_info=True)
