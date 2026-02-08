from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _parse_text_date_time(self, raw_text: str):
    base = (raw_text or "").strip()
    date_iso = None
    time_str = None

    if " — " in base:
        left, right = base.rsplit(" — ", 1)
        tail = right.strip()

        try:
            from PySide6.QtCore import QDate, QTime
            fmts = []

            try:
                fmts.append(self.app.date_input.displayFormat())

            except Exception as e:
                logger.error(f"Erro ao obter formato de data para parsing: {e}", exc_info=True)

            fmts += ["dd/MM/yyyy", "d/M/yyyy", "MM/dd/yyyy", "M/d/yyyy", "yyyy-MM-dd"]
            parts = tail.split()

            if len(parts) == 2:
                d_candidate, t_candidate = parts

                for fmt in fmts:
                    qd = QDate.fromString(d_candidate, fmt)

                    if qd and qd.isValid():
                        qt = QTime.fromString(t_candidate, "HH:mm")

                        if qt.isValid():
                            date_iso = qd.toString(Qt.ISODate)
                            time_str = qt.toString("HH:mm")
                            base = left.strip()
                            break

            if date_iso is None:
                for fmt in fmts:
                    qd = QDate.fromString(tail, fmt)

                    if qd and qd.isValid():
                        date_iso = qd.toString(Qt.ISODate)
                        base = left.strip()
                        break

            if date_iso is None:
                from PySide6.QtCore import QTime
                qt = QTime.fromString(tail, "HH:mm")

                if qt.isValid():
                    time_str = qt.toString("HH:mm")
                    base = left.strip()

        except Exception as e:
            logger.error(f"Erro ao fazer parsing de data/hora: {e}", exc_info=True)

    return base, date_iso, time_str
