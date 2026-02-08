from PySide6.QtWidgets import QCalendarWidget, QAbstractItemView, QToolTip
from PySide6.QtCore import Qt, QDate, QEvent, QRect
from PySide6.QtGui import QPainter, QFontMetrics, QBrush, QFont, QPen
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class BadgeCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self._task_counts_by_date = {}  # {date_str: count}
            self._task_counts_by_week = {}  # {week_number: count}
            self._task_counts_by_month = {}  # {(year, month): count}
            self._tasks_by_date = {}  # {date_iso_str: [lines]}

        except Exception as e:
            logger.error(f"Erro ao inicializar BadgeCalendarWidget: {e}", exc_info=True)

        try:
            self.setMouseTracking(True)

        except Exception:
            pass

    def set_task_tooltip_map(self, tasks_by_date: dict):
        try:
            self._tasks_by_date = tasks_by_date or {}

        except Exception as e:
            logger.error(f"Erro ao definir mapa de tooltip do calendário: {e}", exc_info=True)

    def set_task_counts(self, task_dates_iso):
        try:
            self._task_counts_by_date.clear()
            self._task_counts_by_week.clear()
            self._task_counts_by_month.clear()

            for date_str in task_dates_iso:
                qdate = QDate.fromString(date_str, Qt.ISODate)
                if not qdate.isValid():
                    continue

                self._task_counts_by_date[date_str] = self._task_counts_by_date.get(date_str, 0) + 1

                week_num = qdate.weekNumber()[0]
                self._task_counts_by_week[week_num] = self._task_counts_by_week.get(week_num, 0) + 1

                month_key = (qdate.year(), qdate.month())
                self._task_counts_by_month[month_key] = self._task_counts_by_month.get(month_key, 0) + 1

            self.updateCells()

        except Exception as e:
            logger.error(f"Erro ao definir contadores de tarefas: {e}", exc_info=True)

    def paintCell(self, painter, rect, date):
        try:
            super().paintCell(painter, rect, date)

            date_str = date.toString(Qt.ISODate)
            count = self._task_counts_by_date.get(date_str, 0)

            if count > 0:
                self._draw_badge(painter, rect, count)

        except Exception as e:
            logger.error(f"Erro ao pintar célula do calendário: {e}", exc_info=True)

    def _draw_badge(self, painter, cell_rect, count):
        try:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)

            text = str(count)
            font = QFont(painter.font())
            font.setPointSize(max(7, font.pointSize() - 2))
            font.setBold(True)
            painter.setFont(font)

            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()

            badge_size = max(16, text_width + 8)
            badge_size = min(badge_size, cell_rect.width() // 2)

            badge_x = cell_rect.right() - badge_size - 2
            badge_y = cell_rect.top() + 2
            badge_rect = QRect(badge_x, badge_y, badge_size, badge_size)

            pal = self.palette()
            badge_color = pal.highlight().color()
            badge_color.setAlpha(200)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(badge_color))
            painter.drawEllipse(badge_rect)

            text_color = pal.highlightedText().color()
            painter.setPen(QPen(text_color))
            painter.drawText(badge_rect, Qt.AlignCenter, text)

            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao desenhar badge: {e}", exc_info=True)

    def _date_at_pos(self, pos):
        try:
            if hasattr(self, "dateAt"):
                try:
                    qd = self.dateAt(pos)
                    if isinstance(qd, QDate) and qd.isValid():
                        return qd

                except Exception:
                    pass

            view = self.findChild(QAbstractItemView)
            if view is not None:
                vpos = view.mapFrom(self, pos)
                idx = view.indexAt(vpos)
                if idx.isValid():
                    for role in (Qt.UserRole, Qt.UserRole + 1, Qt.UserRole + 2, Qt.DisplayRole):
                        try:
                            val = idx.data(role)
                            if isinstance(val, QDate) and val.isValid():
                                return val

                        except Exception:
                            pass

                    try:
                        day_val = idx.data(Qt.DisplayRole)
                        day = int(day_val)
                        if day > 0:
                            qd = QDate(self.yearShown(), self.monthShown(), day)
                            if qd.isValid():
                                return qd

                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Erro ao obter data pelo mouse no calendário: {e}", exc_info=True)

        return None

    def event(self, event):
        try:
            if event.type() == QEvent.ToolTip:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
                qd = self._date_at_pos(pos)
                if qd and qd.isValid():
                    ds = qd.toString(Qt.ISODate)
                    lines = self._tasks_by_date.get(ds) or []
                    if lines:
                        QToolTip.showText(event.globalPos(), "\n".join(lines), self)
                        return True

                QToolTip.hideText()
                event.ignore()
                return True

        except Exception as e:
            logger.error(f"Erro ao exibir tooltip no calendário: {e}", exc_info=True)

        return super().event(event)

    def get_week_count(self, week_number):
        return self._task_counts_by_week.get(week_number, 0)

    def get_month_count(self, year, month):
        return self._task_counts_by_month.get((year, month), 0)
