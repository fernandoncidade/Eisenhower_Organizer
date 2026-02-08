from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _quadrant_options(app):
    try:
        return [
            app.quadrant1_label.text(),
            app.quadrant2_label.text(),
            app.quadrant3_label.text(),
            app.quadrant4_label.text(),
        ]

    except Exception as e:
        logger.error(f"Error getting quadrant options: {e}", exc_info=True)
        return []
