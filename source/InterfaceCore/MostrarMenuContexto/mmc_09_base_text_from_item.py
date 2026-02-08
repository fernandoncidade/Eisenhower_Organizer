from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _base_text_from_item(item) -> str:
    try:
        data = item.data(Qt.UserRole) or {}
        base = (data.get("text") or "").strip()
        if base:
            return base

        txt = (item.text() or "").strip()
        if " — " in txt:
            return txt.split(" — ", 1)[0].strip()

        return txt

    except Exception as e:
        logger.error(f"Error getting base text from item: {e}", exc_info=True)
        return ""
