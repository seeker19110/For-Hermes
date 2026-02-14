#!/usr/bin/env python3
"""
OpenClaw Enterprise - Main Loop
===============================
Бесконечный цикл работы агента SalesAgentWhale.

Функционал:
1. Логинится один раз при старте
2. Запускает цикл проверки сообщений каждые 60 секунд
3. Логирует все действия в консоль
4. Интегрирован DatabaseManager, ConfigManager, ErrorRecovery
5. Поддержка восстановления после сбоев
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openclaw-enterprise'))

from agents.sales_agent_whale import SalesAgentWhale, WhaleConfig
from scripts.auth_manager import AuthManager
from scripts.telegram_notifier import TelegramNotifier, TelegramNotification
from scripts.database_manager import get_database, save_cycle_state, load_cycle_state
from scripts.config_manager import get_config
from scripts.error_recovery import get_recovery_manager


class OpenClawBot:
    """
    Главный класс бота - бесконечный цикл работы агента.
    """
    
    def __init__(self, check_interval: int = None, mock_mode: bool = None):
        """
        Инициализация бота.
        
        Args:
            check_interval: Интервал проверки сообщений в секундах (по умолчанию из конфига)
            mock_mode: Режим мока (по умолчанию из конфига)
        """
        # Загружаем конфигурацию
        config = get_config()
        
        self.check_interval = check_interval or config.bot.check_interval
        self.mock_mode = mock_mode if mock_mode is not None else config.bot.mock_mode
        self.agent: Optional[SalesAgentWhale] = None
        self.auth = AuthManager()
        self.running = False
        self.cycle_count = 0
        
        # Инициализируем менеджеры
        self.db = get_database()
        self.recovery = get_recovery_manager()
        
        # Telegram уведомления
        self.telegram_notifier = TelegramNotifier()
        
        logger.info("🤖 OpenClawBot инициализирован")
        logger.info(f"   check_interval: {self.check_interval}s")
        logger.info(f"   mock_mode: {self.mock_mode}")
        
        # Пытаемся восстановить состояние
        self._restore_state()
    
    def _restore_state(self):
        """Восстановить состояние после перезапуска."""
        try:
            saved_state = load_cycle_state()
            if saved_state:
                logger.info(f"♻️ Восстановлено состояние: цикл {saved_state.get('cycle_number', 0)}")
                self.cycle_count = saved_state.get('cycle_number', 0)
        except Exception as e:
            logger.warning(f"⚠️ Не удалось восстановить состояние: {e}")
    
    async def login(self) -> bool:
        """
        Однократный логин при старте.
        
        Returns:
            True если логин успешен
        """
        logger.info("🔐 Выполняю логин...")
        
        # Получаем учетные данные
        credentials = self.auth.get_loyalfans_credentials()
        
        if not credentials:
            logger.error("❌ Не найдены учетные данные LOYALFANS")
            return False
        
        username, password = credentials
        logger.info(f"   Username: {username}")
        
        # Логинимся через controller
        if self.agent:
            result = await self.agent.controller.login(username, password)
            
            if result.get('status') == 'success':
                logger.info(f"   ✅ Логин успешен! Session: {result.get('session_id', 'N/A')}")
                
                # Сохраняем сессию в БД
                session_id = result.get('session_id', f'session_{datetime.now().timestamp()}')
                self.db.create_session(session_id, 'loyalfans', {'username': username})
                
                return True
            else:
                logger.error(f"   ❌ Ошибка логина: {result}")
                return False
        
        return False
    
    async def process_cycle(self) -> dict:
        """
        Один цикл проверки сообщений.
        
        Returns:
            Результат цикла
        """
        self.cycle_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 ЦИКЛ #{self.cycle_count} | {timestamp}")
        logger.info(f"{'='*60}")
        
        # Логируем начало цикла
        self.db.log_event('cycle', 'start', 
                         metadata={'cycle_number': self.cycle_count})
        
        try:
            # Обрабатываем входящие сообщения через Controller
            result = await self.agent.process_incoming_from_controller()
            
            logger.info(f"   ✅ Обработано: {result.get('total_messages', 0)} сообщений")
            logger.info(f"   🐋 Китов привлечено: {result.get('whales_engaged', 0)}")
            
            # Отправляем Telegram уведомление о китах
            if result.get('whales_engaged', 0) > 0:
                whales_data = result.get('whales_data', [])
                for whale in whales_data:
                    notification = TelegramNotification(
                        message_id=whale.get('message_id', ''),
                        username=whale.get('username', ''),
                        user_message=whale.get('message', ''),
                        prepared_response=whale.get('response', ''),
                        spent_weekly=whale.get('spent_weekly', 0.0),
                        timestamp=datetime.now().isoformat()
                    )
                    self.telegram_notifier.send_whale_notification(notification)
                    logger.info(f"   📱 Telegram уведомление отправлено для {whale.get('username', '')}")
            
            # Сохраняем состояние
            processed = [w.get('username', '') for w in result.get('whales_data', [])]
            save_cycle_state(self.cycle_count, processed)
            
            # Логируем успешное завершение
            self.db.log_event('cycle', 'complete', metadata={
                'cycle_number': self.cycle_count,
                'messages': result.get('total_messages', 0),
                'whales': result.get('whales_engaged', 0)
            })
            
            return result
            
        except Exception as e:
            # Логируем ошибку
            logger.error(f"   ❌ Ошибка в цикле: {e}")
            self.recovery.record_error('CycleError', str(e), 
                                      context={'cycle': self.cycle_count})
            self.db.log_event('cycle', 'error', metadata={
                'cycle_number': self.cycle_count,
                'error': str(e)
            })
            return {"status": "error", "message": str(e)}
    
    async def run(self):
        """
        Главный метод - бесконечный цикл.
        """
        logger.info("🐋 OpenClaw Enterprise - Запуск бота")
        logger.info(f"   Интервал проверки: {self.check_interval} сек")
        logger.info(f"   Режим: {'MOCK' if self.mock_mode else 'PRODUCTION'}")
        
        # Инициализируем агента
        config = WhaleConfig(min_weekly_spend=50.0)
        self.agent = SalesAgentWhale(config=config, mock_mode=self.mock_mode)
        
        # Выполняем логин (один раз)
        if not await self.login():
            logger.error("❌ Не удалось выполнить логин. Бот останавливается.")
            return
        
        # Переходим на страницу сообщений
        logger.info("📬 Переход на страницу сообщений...")
        await self.agent.controller.navigate_to("https://loyalfans.com/messages")
        logger.info("   ✅ Навигация выполнена")
        
        # Бесконечный цикл
        self.running = True
        logger.info(f"\n🚀 БОТ ЗАПУЩЕН! Начинаю проверку сообщений каждые {self.check_interval} сек...")
        logger.info("   Для остановки нажмите Ctrl+C\n")
        
        while self.running:
            try:
                await self.process_cycle()
                
                # Пауза между циклами
                logger.info(f"   😴 Сплю {self.check_interval} секунд...")
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️ Получен сигнал остановки...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Критическая ошибка: {e}")
                
                # Записываем ошибку
                self.recovery.record_error('CriticalError', str(e),
                                          context={'cycle': self.cycle_count})
                
                # Circuit breaker для основного сервиса
                cb = self.recovery.get_circuit_breaker('loyalfans')
                if cb:
                    try:
                        cb.call(lambda: None)  # Проверяем состояние
                    except:
                        logger.error("🚨 Circuit breaker открыт! Приостанавливаю работу...")
                        await asyncio.sleep(cb.recovery_timeout)
                
                logger.info(f"   Повторная попытка через {self.check_interval} сек...")
                await asyncio.sleep(self.check_interval)
        
        # Завершаем сессию
        session = self.db.get_active_session('loyalfans')
        if session:
            self.db.end_session(session['session_id'])
        
        logger.info("👋 Бот остановлен.")
        logger.info(f"   Всего выполнено циклов: {self.cycle_count}")


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

async def main():
    """
    Точка входа.
    """
    # Создаем и запускаем бота
    bot = OpenClawBot()  # Настройки загружаются из конфига
    
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
