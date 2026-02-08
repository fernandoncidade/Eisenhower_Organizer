from .mmc_01_compute_widget_height import _compute_widget_height
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _apply_widget_min_height(app, widget, name: str | None = None):
    try:
        h = _compute_widget_height(app, widget, name)
        widget.setMinimumHeight(h)

    except Exception:
        pass
