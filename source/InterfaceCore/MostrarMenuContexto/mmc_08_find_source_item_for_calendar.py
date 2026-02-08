from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _find_source_item_for_calendar(app, task_dict):
    try:
        if not isinstance(task_dict, dict):
            return None, None

        cat = task_dict.get("category")
        if not cat:
            return None, None

        completed = bool(task_dict.get("completed"))
        labels = [
            getattr(app, "quadrant1_label", None).text() if getattr(app, "quadrant1_label", None) is not None else None,
            getattr(app, "quadrant2_label", None).text() if getattr(app, "quadrant2_label", None) is not None else None,
            getattr(app, "quadrant3_label", None).text() if getattr(app, "quadrant3_label", None) is not None else None,
            getattr(app, "quadrant4_label", None).text() if getattr(app, "quadrant4_label", None) is not None else None,
        ]
        pending = [getattr(app, "quadrant1_list", None), getattr(app, "quadrant2_list", None), getattr(app, "quadrant3_list", None), getattr(app, "quadrant4_list", None)]
        done = [getattr(app, "quadrant1_completed_list", None), getattr(app, "quadrant2_completed_list", None), getattr(app, "quadrant3_completed_list", None), getattr(app, "quadrant4_completed_list", None)]

        def _norm_text(value) -> str:
            return str(value or "").strip()

        def _norm_prio(value):
            try:
                return int(value)

            except Exception as e:
                logger.error(f"Error normalizing priority value '{value}': {e}", exc_info=True)
                return _norm_text(value)

        def _same_task(left: dict, right: dict) -> bool:
            return (
                _norm_text(left.get("text")) == _norm_text(right.get("text"))
                and _norm_text(left.get("date")) == _norm_text(right.get("date"))
                and _norm_text(left.get("time")) == _norm_text(right.get("time"))
                and _norm_text(left.get("file_path")) == _norm_text(right.get("file_path"))
                and _norm_text(left.get("description")) == _norm_text(right.get("description"))
                and _norm_prio(left.get("priority")) == _norm_prio(right.get("priority"))
            )

        for idx, label in enumerate(labels):
            try:
                if not label:
                    continue

                if not str(cat).startswith(label):
                    continue

                src_list = done[idx] if completed else pending[idx]
                if src_list is None:
                    continue

                for i in range(src_list.count()):
                    it = src_list.item(i)
                    if not it:
                        continue

                    if not (it.flags() & Qt.ItemIsSelectable):
                        continue

                    d = it.data(Qt.UserRole) or {}
                    if _same_task(d, task_dict):
                        return src_list, it

            except Exception as e:
                logger.error(f"Error finding source item for calendar: {e}", exc_info=True)
                continue

    except Exception as e:
        logger.error(f"Unexpected error in _find_source_item_for_calendar: {e}", exc_info=True)

    return None, None
