import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, limit: int = 50):
        """
        Инициализация менеджера памяти с циклическим буфером.
        :param limit: Максимальное количество событий на одного пользователя.
        """
        self.storage: Dict[str, List[Dict[str, Any]]] = {}
        self.limit = limit

    async def get_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Получить историю действий пользователя для контекста ИИ."""
        return self.storage.get(user_id, [])

    async def add_event(self, user_id: str, event_type: str, details: Dict[str, Any]):
        """
        Добавить событие в память. Если лимит превышен, старые события удаляются.
        """
        if user_id not in self.storage:
            self.storage[user_id] = []
        
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        
        self.storage[user_id].append(event)
        
        # Механизм циклического буфера
        if len(self.storage[user_id]) > self.limit:
            self.storage[user_id] = self.storage[user_id][-self.limit:]
            logger.debug(f"Memory limit reached for {user_id}. Oldest event removed.")

    async def clear_memory(self, user_id: str):
        """Полная очистка памяти пользователя."""
        self.storage.pop(user_id, None)
        logger.info(f"Memory cleared for user {user_id}")
