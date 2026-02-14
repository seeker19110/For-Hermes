import httpx
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    async def send_alert(self, message: str, status: str = "INFO"):
        """
        Отправка уведомления с Markdown-разметкой и статусными эмодзи.
        Статусы: SUCCESS, ERROR, WARNING, INFO.
        """
        icons = {
            "SUCCESS": "✅",
            "ERROR": "🚨",
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        
        status_upper = status.upper()
        icon = icons.get(status_upper, "🔔")
        
        # Формирование сообщения с Markdown (упрощенным для удобства)
        formatted_text = f"{icon} *{status_upper}*\n\n{message}"
        
        payload = {
            "chat_id": self.chat_id,
            "text": formatted_text,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, timeout=10.0)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Telegram notification failed: {e}")
                return False
