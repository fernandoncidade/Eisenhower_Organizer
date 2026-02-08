from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _compute_widget_height(app, widget, name: str | None = None) -> int:
    try:
        if hasattr(app, "widget_heights") and isinstance(app.widget_heights, dict) and name in app.widget_heights:
            v = int(app.widget_heights.get(name) or 0)
            if v > 0:
                return v

        if hasattr(app, "widget_height_override") and isinstance(app.widget_height_override, int) and app.widget_height_override > 0:
            return int(app.widget_height_override)

        fm = widget.fontMetrics()
        return max(26, int(fm.height() * 1.2))

    except Exception as e:
        logger.error(f"Error computing widget height: {e}", exc_info=True)
        return 28
