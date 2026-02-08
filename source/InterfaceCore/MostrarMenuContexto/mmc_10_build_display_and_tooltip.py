from PySide6.QtCore import QCoreApplication, Qt, QDate
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _build_display_and_tooltip(app, base_text: str, date_iso: str | None, time_str: str | None):
    display_text = base_text
    tooltip_lines = []

    try:
        if date_iso:
            qd = QDate.fromString(date_iso, Qt.ISODate)

            if qd.isValid():
                date_human = qd.toString(app.date_input.displayFormat())

                if time_str:
                    display_text = f"{base_text} — {date_human} {time_str}"

                else:
                    display_text = f"{base_text} — {date_human}"

                tooltip_lines.append(f"{get_text('Data') or 'Data'}: {date_human}")

        if time_str:
            tooltip_lines.append(f"{get_text('Horário') or 'Horário'}: {time_str}")

        return display_text, ("\n".join(tooltip_lines) if tooltip_lines else "")

    except Exception as e:
        logger.error(f"Error building display and tooltip: {e}", exc_info=True)
        return display_text, ("\n".join(tooltip_lines) if tooltip_lines else "")
