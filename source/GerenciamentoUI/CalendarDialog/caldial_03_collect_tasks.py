from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _collect_tasks(self):
    try:
        tasks = []
        mapping = [
            (self.app.quadrant1_list, self.app.quadrant1_label.text(), False),
            (self.app.quadrant1_completed_list, f"{self.app.quadrant1_label.text()} - {self.app.quadrant1_completed_label.text()}", True),
            (self.app.quadrant2_list, self.app.quadrant2_label.text(), False),
            (self.app.quadrant2_completed_list, f"{self.app.quadrant2_label.text()} - {self.app.quadrant2_completed_label.text()}", True),
            (self.app.quadrant3_list, self.app.quadrant3_label.text(), False),
            (self.app.quadrant3_completed_list, f"{self.app.quadrant3_label.text()} - {self.app.quadrant3_completed_label.text()}", True),
            (self.app.quadrant4_list, self.app.quadrant4_label.text(), False),
            (self.app.quadrant4_completed_list, f"{self.app.quadrant4_label.text()} - {self.app.quadrant4_completed_label.text()}", True),
        ]
        for lst, category, completed in mapping:
            for i in range(lst.count()):
                item = lst.item(i)
                if not item or not (item.flags() & Qt.ItemIsSelectable):
                    continue

                data = item.data(Qt.UserRole) or {}
                text = data.get("text", item.text())
                date_str = data.get("date")
                time_str = data.get("time")
                file_path = data.get("file_path")
                description = data.get("description")
                priority = data.get("priority")
                tasks.append({
                    "text": text,
                    "date": date_str,
                    "time": time_str,
                    "category": category,
                    "completed": completed,
                    "file_path": file_path,
                    "description": description,
                    "priority": priority,
                })

        return tasks

    except Exception as e:
        logger.error(f"Erro ao coletar tarefas do calendário: {e}", exc_info=True)
        return []
