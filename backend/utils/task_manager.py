"""
Gestionnaire de tâches asynchrones pour la génération de FAQ
"""
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TaskManager:
    """Gestionnaire simple de tâches en arrière-plan"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def create_task(self, task_name: str, **task_data) -> str:
        """Crée une nouvelle tâche et retourne son ID"""
        task_id = str(uuid.uuid4())

        with self.lock:
            self.tasks[task_id] = {
                'id': task_id,
                'name': task_name,
                'status': 'pending',
                'progress': 0,
                'message': 'Tâche créée',
                'result': None,
                'error': None,
                'created_at': datetime.now(),
                'started_at': None,
                'completed_at': None,
                **task_data
            }

        logger.info(f"Tâche créée: {task_id} - {task_name}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une tâche"""
        with self.lock:
            return self.tasks.get(task_id)

    def update_task(self, task_id: str, **updates):
        """Met à jour une tâche"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(updates)
                logger.info(f"Tâche mise à jour: {task_id} - {updates}")

    def start_task(self, task_id: str):
        """Marque une tâche comme démarrée"""
        self.update_task(task_id,
                        status='running',
                        started_at=datetime.now(),
                        message='Tâche en cours...')

    def complete_task(self, task_id: str, result: Any = None):
        """Marque une tâche comme terminée avec succès"""
        self.update_task(task_id,
                        status='completed',
                        progress=100,
                        result=result,
                        completed_at=datetime.now(),
                        message='Tâche terminée avec succès',
                        keep_until=datetime.now().timestamp() + 300)  # Garder 5 minutes

    def fail_task(self, task_id: str, error: str):
        """Marque une tâche comme échouée"""
        self.update_task(task_id,
                        status='failed',
                        error=error,
                        completed_at=datetime.now(),
                        message=f'Tâche échouée: {error}',
                        keep_until=datetime.now().timestamp() + 300)  # Garder 5 minutes

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Nettoie les anciennes tâches"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self.lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task['created_at'].timestamp() < cutoff_time:
                    to_remove.append(task_id)

            for task_id in to_remove:
                del self.tasks[task_id]
                logger.info(f"Tâche supprimée (trop ancienne): {task_id}")

# Instance globale du gestionnaire de tâches
task_manager = TaskManager()
