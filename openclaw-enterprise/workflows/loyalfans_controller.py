import logging
from typing import Dict, Any
from scripts.auth_manager import AuthManager
from scripts.database_manager import DatabaseManager
from scripts.telegram_notifier import TelegramNotifier
from workflows.memory_manager import MemoryManager

class LoyalFansController:
    def __init__(self, auth: AuthManager, db: DatabaseManager, 
                 memory: MemoryManager, notifier: TelegramNotifier):
        self.auth = auth
        self.db = db
        self.memory = memory
        self.notifier = notifier
        self.session_active = False

    async def execute_workflow(self, user_id: str, action: str, data: Dict[str, Any]):
        try:
            await self._ensure_session(user_id)
            if action == "sync_messages":
                result = await self._handle_message_sync(user_id, data)
                status = "SUCCESS"
            elif action == "upload_media":
                result = await self._handle_media_upload(user_id, data)
                status = "SUCCESS"
            else:
                raise ValueError(f"Unknown action: {action}")
            
            await self.db.log_event(user_id, status.lower(), f"Completed {action}")
            await self.notifier.send_alert(f"Task {action} finished!", status=status)
            return result
        except Exception as e:
            await self._report_failure(user_id, action, e)
            return {"status": "error", "message": str(e)}

    async def _ensure_session(self, user_id: str):
        if not self.session_active:
            await self.auth.get_credentials(user_id)
            await self.memory.get_context(user_id)
            self.session_active = True

    async def _handle_message_sync(self, user_id: str, data: Dict[str, Any]):
        return {"status": "synced", "count": len(data.get("messages", []))}

    async def _handle_media_upload(self, user_id: str, data: Dict[str, Any]):
        return {"status": "uploaded", "url": data.get("file_path")}

    async def _report_failure(self, user_id: str, action: str, error: Exception):
        msg = f"Workflow {action} failed: {str(error)}"
        await self.notifier.send_alert(msg, status="ERROR")
        await self.db.log_event(user_id, "error", msg)