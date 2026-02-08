from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _is_completed_list(app, lst) -> bool:
    try:
        return lst in (
            app.quadrant1_completed_list,
            app.quadrant2_completed_list,
            app.quadrant3_completed_list,
            app.quadrant4_completed_list,
        )

    except Exception as e:
        logger.error(f"Error checking if list is completed list: {e}", exc_info=True)
        return False
