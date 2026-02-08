from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _clear_all_lists(self):
    try:
        for lst in (
            self.app.quadrant1_list, self.app.quadrant2_list, self.app.quadrant3_list, self.app.quadrant4_list,
            self.app.quadrant1_completed_list, self.app.quadrant2_completed_list, self.app.quadrant3_completed_list, self.app.quadrant4_completed_list
        ):
            lst.clear()

    except Exception as e:
        logger.error(f"Erro ao limpar todas as listas: {e}", exc_info=True)
