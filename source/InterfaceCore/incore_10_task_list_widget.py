from PySide6.QtCore import Qt, QPoint, QItemSelectionModel
from PySide6.QtWidgets import QListWidget, QAbstractItemView, QLabel, QApplication
from PySide6.QtGui import QDrag, QPalette, QColor, QPixmap, QPainter, QCursor
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class TaskListWidget(QListWidget):
    def __init__(self, app, is_completed: bool, parent=None):
        super().__init__(parent)
        self._app = app
        self._is_completed = bool(is_completed)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        try:
            self.setSelectionRectVisible(True)

        except Exception:
            pass

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        try:
            ref_palette = None

            if hasattr(self._app, "palette"):
                ref_palette = self._app.palette()

            elif self.window() is not None:
                ref_palette = self.window().palette()

            if ref_palette is not None:
                pal = self.palette()
                window_color = ref_palette.color(QPalette.Window)
                pal.setColor(QPalette.Base, window_color)
                pal.setColor(QPalette.AlternateBase, window_color)
                self.setPalette(pal)
                self.setAutoFillBackground(True)

                try:
                    self.viewport().setAutoFillBackground(True)

                except Exception:
                    pass

            self.setMouseTracking(True)
            self._hover_preview = None
            self._current_hover_item = None
            self._drag_start_pos = None
            self._drag_start_item = None
            self._selection_rect_enabled = True

        except Exception:
            self._hover_preview = None
            self._current_hover_item = None
            self._drag_start_pos = None
            self._drag_start_item = None
            self._selection_rect_enabled = True

    def _create_preview_widget(self):
        lbl = QLabel(None, Qt.ToolTip)
        lbl.setAttribute(Qt.WA_ShowWithoutActivating)
        lbl.setWindowFlags(Qt.ToolTip)
        lbl.setWordWrap(True)
        font = lbl.font()
        font.setPointSize(max(9, font.pointSize() - 1))
        lbl.setFont(font)

        lbl.setAutoFillBackground(True)
        pal = lbl.palette()
        pal.setColor(QPalette.Window, QColor("#ffffe0"))
        pal.setColor(QPalette.WindowText, QColor("#000000"))
        lbl.setPalette(pal)

        lbl.setContentsMargins(6, 6, 6, 6)
        lbl.setMargin(0)

        try:
            lbl.setFrameStyle(lbl.Panel | lbl.Plain)
            lbl.setLineWidth(1)

        except Exception:
            pass

        return lbl

    def _show_preview_for_item(self, item, global_pos: QPoint):
        try:
            if item is None:
                self._hide_preview()
                return

            data = item.data(Qt.UserRole) or {}
            desc = data.get("description") or ""
            if not desc:
                desc = item.toolTip() or ""

            if not desc:
                self._hide_preview()
                return

            preview_text = "\n".join([ln for ln in desc.splitlines() if ln.strip()][:3])
            if not preview_text:
                self._hide_preview()
                return

            if self._hover_preview is None:
                self._hover_preview = self._create_preview_widget()

            lbl = self._hover_preview._label
            lbl.setText(preview_text)
            self._hover_preview.adjustSize()
            geo = self._hover_preview.frameGeometry()
            x = global_pos.x() + 16
            y = global_pos.y() + 16
            screen = self.window().screen() if self.window() else None
            if screen:
                scr_geo = screen.availableGeometry()
                if x + geo.width() > scr_geo.right():
                    x = global_pos.x() - geo.width() - 16

                if y + geo.height() > scr_geo.bottom():
                    y = scr_geo.bottom() - geo.height() - 8

            self._hover_preview.move(x, y)
            self._hover_preview.show()
            self._current_hover_item = item

        except Exception:
            pass

    def _hide_preview(self):
        try:
            if self._hover_preview:
                try:
                    self._hover_preview.hide()

                except Exception:
                    pass

            self._current_hover_item = None

        except Exception:
            pass

    def _build_drag_pixmap(self, items):
        try:
            rects = []
            for it in items:
                if it is None:
                    continue

                r = self.visualItemRect(it)
                if r.isValid():
                    rects.append(r)

            if not rects:
                return None, None

            union = rects[0]
            for r in rects[1:]:
                union = union.united(r)

            pixmap = QPixmap(union.size())
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setOpacity(0.6)

            for it in items:
                r = self.visualItemRect(it)
                if not r.isValid():
                    continue

                item_pix = self.viewport().grab(r)
                painter.drawPixmap(r.topLeft() - union.topLeft(), item_pix)

            painter.end()
            return pixmap, union

        except Exception:
            return None, None

    def mouseMoveEvent(self, event):
        try:
            item = self.itemAt(event.pos())
            global_pos = self.mapToGlobal(event.pos())
            if item is not None and item is not self._current_hover_item:
                self._show_preview_for_item(item, global_pos)

            elif item is None:
                self._hide_preview()

            drag_started = False
            try:
                if event.buttons() & Qt.LeftButton and self._drag_start_pos is not None:
                    start_item = self._drag_start_item if self._drag_start_item is not None else self.itemAt(self._drag_start_pos)
                    if start_item and start_item.isSelected():
                        delta = event.pos() - self._drag_start_pos
                        if delta.manhattanLength() >= QApplication.startDragDistance():
                            if not self.selectedItems():
                                self.setCurrentItem(start_item)

                            self.startDrag(Qt.MoveAction)
                            self._drag_start_pos = None
                            self._drag_start_item = None
                            drag_started = True

            except Exception:
                pass

            if not drag_started:
                super().mouseMoveEvent(event)

        except Exception:
            pass

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self._drag_start_pos = event.pos()
                item = self.itemAt(event.pos())
                self._drag_start_item = item
                modifiers = event.modifiers()
                if item is not None and item.isSelected() and not (modifiers & (Qt.ControlModifier | Qt.ShiftModifier)):
                    try:
                        self._selection_rect_enabled = False
                        self.setSelectionRectVisible(False)

                    except Exception:
                        pass

                    self.setCurrentItem(item, QItemSelectionModel.NoUpdate)
                    return

                try:
                    self._selection_rect_enabled = True
                    self.setSelectionRectVisible(True)

                except Exception:
                    pass

        except Exception:
            pass

        super().mousePressEvent(event)

    def leaveEvent(self, event):
        try:
            self._hide_preview()

        except Exception:
            pass

        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                super().mouseReleaseEvent(event)
                if not self._selection_rect_enabled:
                    try:
                        self.setSelectionRectVisible(False)

                    except Exception:
                        pass

                self._drag_start_pos = None
                self._drag_start_item = None
                return

        except Exception:
            pass

        super().mouseReleaseEvent(event)

    def startDrag(self, supportedActions):
        try:
            if not self.selectedItems():
                return

            mime = self.model().mimeData(self.selectedIndexes())
            if mime is None:
                return

            drag = QDrag(self)
            drag.setMimeData(mime)

            pixmap, union = self._build_drag_pixmap(self.selectedItems())
            if pixmap is not None:
                drag.setPixmap(pixmap)
                try:
                    hotspot = None
                    if self._drag_start_pos is not None and union is not None:
                        hotspot = self._drag_start_pos - union.topLeft()

                    else:
                        vp_pos = self.viewport().mapFromGlobal(QCursor.pos())
                        if union is not None:
                            hotspot = vp_pos - union.topLeft()

                    if hotspot is not None:
                        drag.setHotSpot(hotspot)

                except Exception:
                    pass

            drag.exec(Qt.MoveAction | Qt.CopyAction)

        except Exception as e:
            logger.error(f"Erro no startDrag do TaskListWidget: {e}", exc_info=True)

    def dropEvent(self, event):
        try:
            source = event.source()
            if not isinstance(source, QListWidget):
                return super().dropEvent(event)

            if source is self:
                event.ignore()
                return

            dragged_items = [it for it in source.selectedItems() if (it.flags() & Qt.ItemIsSelectable)]
            if not dragged_items:
                event.ignore()
                return

            new_state = Qt.Checked if self._is_completed else Qt.Unchecked

            source.blockSignals(True)
            self.blockSignals(True)
            try:
                for item in list(dragged_items):
                    if not (item.flags() & Qt.ItemIsSelectable):
                        continue

                    self._app.move_item_between_lists(item, source, self, new_state)

            finally:
                source.blockSignals(False)
                self.blockSignals(False)

            try:
                self._app.save_tasks()

            except Exception as e:
                logger.error(f"Erro ao salvar tarefas após drag-and-drop: {e}", exc_info=True)

            try:
                if hasattr(self._app, "calendar_pane") and self._app.calendar_pane:
                    self._app.calendar_pane.calendar_panel.update_task_list()

            except Exception as e:
                logger.error(f"Erro ao atualizar calendário após drag-and-drop: {e}", exc_info=True)

            event.setDropAction(Qt.MoveAction)
            event.accept()

        except Exception as e:
            logger.error(f"Erro no dropEvent do TaskListWidget: {e}", exc_info=True)
            event.ignore()
