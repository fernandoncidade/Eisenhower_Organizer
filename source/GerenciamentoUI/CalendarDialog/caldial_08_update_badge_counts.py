from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _update_badge_counts(self):
    try:
        task_dates = []
        for task in self._collect_tasks():
            date_str = task.get("date")
            if date_str:
                task_dates.append(date_str)
        
        self.calendar.set_task_counts(task_dates)

    except Exception as e:
        logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)
