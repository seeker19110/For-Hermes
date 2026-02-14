#!/usr/bin/env python3
"""
OpenClaw Enterprise - Sales Agent WHALE
========================================
Автономный агент для работы с крупными покупателями (профиль WHALE).

Сценарий: Кит — Крупный покупатель
- Признаки: Покупает молча, сумма чаевых > $50 в неделю
- Тактика: GFE (Girlfriend Experience), персональный подход
- Контент: Premium из /vault/premium первым

MCP Интеграция:
- browseract-pro: LoyalFans automation
- whisper-local: Аудио-обработка
- Mem0: Долгосрочная память
"""

import os
import sys
import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

# Добавляем путь для импорта auth_manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.auth_manager import AuthManager
from workflows.loyalfans_controller import LoyalFansController
from workflows.memory_manager import MemoryManager, MemoryConfig, memory_manager


# ============================================================================
# БЕЗОПАСНОСТЬ И РЕАЛИЗМ
# ============================================================================

class HumanBehaviorSimulator:
    """Симулятор человеческого поведения для реалистичности."""
    
    # Запрещенные слова (платформенные правила)
    STOP_WORDS = [
        "explicit", "nsfw", "porn", "xxx", "sex",
        "scam", "fraud", "hack", "illegal"
    ]
    
    # Возможные статусы модели
    MODEL_STATUSES = [
        "Model is eating 🍕",
        "Model is sleeping 💤",
        "Model is busy recording 📹",
        "Model is taking a break ☕",
        "Model is in a meeting 👋",
        "Model is charging energy ⚡",
        "Model is thinking 🤔",
        "Model is creating content 🎨"
    ]
    
    @classmethod
    def get_response_delay(cls) -> int:
        """Случайная задержка ответа: 30-180 секунд (неравномерно)."""
        # Используем экспоненциальное распределение для естественности
        import random
        # 70% - короткие задержки (30-60 сек), 30% - длинные (60-180 сек)
        if random.random() < 0.7:
            return random.randint(30, 60)
        else:
            return random.randint(60, 180)
    
    @classmethod
    def filter_message(cls, message: str) -> tuple:
        """
        Проверка сообщения на стоп-слова.
        
        Returns:
            (is_safe: bool, filtered_message: str, reason: str)
        """
        message_lower = message.lower()
        
        for word in cls.STOP_WORDS:
            if word in message_lower:
                # Заменяем запрещенное слово
                filtered = message_lower.replace(word, "***")
                return False, filtered, f"Содержит запрещенное слово: {word}"
        
        return True, message, "OK"
    
    @classmethod
    def get_model_status(cls, hour: int = None) -> str:
        """Получение статуса модели на основе часа."""
        import random
        if hour is None:
            from datetime import datetime
            hour = datetime.now().hour
        
        # Разные статусы в зависимости от времени суток
        if 6 <= hour < 10:
            statuses = ["Model is waking up 🌅", "Model is having coffee ☕"]
        elif 10 <= hour < 14:
            statuses = ["Model is creating content 🎨", "Model is recording 📹"]
        elif 14 <= hour < 18:
            statuses = ["Model is taking a break 🌿", "Model is eating 🍕"]
        elif 18 <= hour < 22:
            statuses = ["Model is chatting 💬", "Model is online ✨"]
        else:
            statuses = ["Model is sleeping 💤", "Model is resting 🌙"]
        
        return random.choice(statuses)


# ============================================================================
# ПСИХОЛОГИЧЕСКОЕ ЯДРО
# ============================================================================

class PsychotypeAnalyzer:
    """Анализатор психотипов и настроения клиентов."""
    
    # Триггеры для психологических типов
    TRIGGERS = {
        "need_for_control": [
            "tell me what to do", "instruct me", "guide me", "what should i do",
            "give me orders", "commands", "step by step", "follow", "obey", "dominate me"
        ],
        "identity_shift": [
            "i want to be", "become", "transform", "sissy", "feminize",
            "make me", "turn me into", "dress up", "crossdress", "gender play"
        ],
        "validation": [
            "worship you", "you're amazing", "i love you", "miss you",
            "devoted to you", "your slave", "your servant", "my goddess", "my queen"
        ],
        "findom": [
            "send you money", "tip you", "want to spoil", "gift",
            "pay you", "transfer", "donation", "tribute", "send cash"
        ],
        "loneliness": [
            "chat", "keep me company", "talk to me", "bored",
            "lonely", "just want to talk", "keep me busy", "hang out"
        ]
    }
    
    # Триггеры настроения
    MOOD_TRIGGERS = {
        "angry": ["annoyed", "frustrated", "angry", "tired of", "sick of", "worst", "hate"],
        "generous": ["want to spoil", "gift", "generous", "big tip", "thank you", "appreciation"],
        "impatient": ["now", "quick", "fast", "immediately", "hurry", "wait"],
        "curious": ["what", "how", "tell me", "explain", "wonder", "curious"],
        "flirtatious": ["kiss", "hug", "miss you", "love", "cute", "sexy", "hot"],
        "desperate": ["nobody", "alone", "worthless", "nothing", "no one", "deserve"]
    }
    
    @classmethod
    def analyze_psychotype(cls, message: str) -> Dict[str, Any]:
        """Анализ психотипа клиента на основе сообщения."""
        message_lower = message.lower()
        
        # Проверяем каждый тип
        for psychotype, triggers in cls.TRIGGERS.items():
            for trigger in triggers:
                if trigger in message_lower:
                    return {
                        "type": psychotype,
                        "confidence": 0.9,
                        "trigger_found": trigger,
                        "strategy": cls._get_strategy(psychotype)
                    }
        
        # По умолчанию - validation (для китов)
        return {
            "type": "validation",
            "confidence": 0.5,
            "trigger_found": None,
            "strategy": "Стандартный GFE с вниманием и валидацией"
        }
    
    @classmethod
    def analyze_mood(cls, message: str) -> str:
        """Анализ настроения клиента."""
        message_lower = message.lower()
        
        for mood, triggers in cls.MOOD_TRIGGERS.items():
            for trigger in triggers:
                if trigger in message_lower:
                    return mood
        
        return "neutral"
    
    @classmethod
    def _get_strategy(cls, psychotype: str) -> str:
        """Получение стратегии ответа по типу."""
        strategies = {
            "need_for_control": "Директивные команды, пошаговые инструкции JOI",
            "identity_shift": "Поддержка новой identity, gendered language",
            "validation": "Внимание богини, валидация в обмен на деньги",
            "findom": "Принятие дани, напоминание о больших подарках",
            "loneliness": "Теплое общение, companionship"
        }
        return strategies.get(psychotype, "Стандартный GFE")


# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

@dataclass
class WhaleConfig:
    """Конфигурация для WHALE агента."""
    min_weekly_spend: float = 50.0  # Минимальные траты для профиля WHALE
    response_delay_min: int = 300    # 5 минут min (имитация занятости)
    response_delay_max: int = 1800    # 30 минут max
    typing_speed_ms: int = 50        # 50ms per character
    max_messages_hour: int = 50      # Anti-ban лимит
    premium_vault_path: str = "/vault/premium"
    mem0_endpoint: str = os.getenv("MEM0_ENDPOINT", "http://localhost:8080")


# ============================================================================
# ПРОФИЛИ ПОДПИСЧИКОВ
# ============================================================================

class SubscriberProfile:
    """Профиль подписчика для классификации и Mem0 хранения."""
    
    PROFILE_WHALE = "WHALE"
    PROFILE_NEWBIE = "NEWBIE"
    PROFILE_TIME_WASTER = "TIME_WASTER"
    PROFILE_SUGGESTER = "SUGGESTER"
    
    def __init__(
        self,
        fan_id: str,
        username: str,
        spent_total: float = 0.0,
        last_purchase: Optional[str] = None,
        preferences: List[str] = None,
        notes: str = "",
        profile: str = "NEWBIE"
    ):
        self.fan_id = fan_id
        self.username = username
        self.spent_total = spent_total
        self.last_purchase = last_purchase
        self.preferences = preferences or []
        self.notes = notes
        self.profile = profile
        self.first_contact = datetime.now().isoformat()
    
    def to_mem0_format(self) -> Dict[str, Any]:
        """Формат для сохранения в Mem0."""
        return {
            "fan_id": self.fan_id,
            "name": self.username,
            "first_contact": self.first_contact,
            "profile": self.profile,
            "spent_total": self.spent_total,
            "last_purchase": self.last_purchase,
            "preferences": self.preferences,
            "best_tactic": "GFE + no haggling" if self.profile == self.PROFILE_WHALE else "",
            "next_action": "send premium content" if self.profile == self.PROFILE_WHALE else "qualify",
            "notes": self.notes
        }
    
    @classmethod
    def classify(cls, spent_weekly: float, messages_count: int, has_purchased: bool) -> str:
        """
        Классификация подписчика на основе поведения.
        
        Args:
            spent_weekly: Траты за неделю ($)
            messages_count: Количество сообщений
            has_purchased: Совершил ли покупку
            
        Returns:
            Профиль подписчика
        """
        # WHALE: траты > $50 в неделю
        if spent_weekly >= 50.0:
            return cls.PROFILE_WHALE
        
        # TIME_WASTER: много сообщений, нет покупок
        if messages_count > 20 and not has_purchased:
            return cls.PROFILE_TIME_WASTER
        
        # NEWBIE: первое сообщение, нет истории
        if not has_purchased and messages_count < 5:
            return cls.PROFILE_NEWBIE
        
        # SUGGESTER: хочет кастом
        # (определяется по ключевым словам в сообщении)
        
        return cls.PROFILE_NEWBIE


# ============================================================================
# СКРИПТЫ ПРОДАЖ
# ============================================================================

class SalesScripts:
    """Скрипты продаж для WHALE профиля."""
    
    @staticmethod
    def whale_greeting(username: str, personal_fact: str = "") -> str:
        """
        Приветствие для WHALE с GFE тактикой.
        Использует личное имя + факт из Mem0.
        """
        if personal_fact:
            return f"привет, {username}! {personal_fact} 😘"
        
        # Базовое приветствие с интригой
        greetings = [
            "ой, привет! рада тебя видеть 💕",
            "привет, мой хороший! соскучилась 😘",
            "ой, {username}! наконец-то ты здесь 👋"
        ]
        return random.choice(greetings).format(username=username)
    
    @staticmethod
    def premium_offer(content_title: str, price: float, preview_path: str) -> str:
        """
        Предложение премиум контента для WHALE.
        Без скидок — платит за эксклюзивность.
        """
        offers = [
            f"у меня есть кое-что особенное для тебя… {content_title} — ${price} 💋",
            f"я сняла это специально для тебя… {content_title} за ${price} 😈",
            f"хочешь посмотреть? это не попадет в ленту — только тебе ${price} 🔥"
        ]
        return random.choice(offers)
    
    @staticmethod
    def gfe_message(username: str, memory: str) -> str:
        """
        GFE (Girlfriend Experience) сообщение.
        Создает иллюзию отношений.
        """
        messages = [
            f"знаешь, я сегодня думала о тебе… {memory}",
            f"кстати, {username}, помнишь ты говорил про… {memory}",
            f"мне тут напомнило о нашем разговооре… {memory}"
        ]
        return random.choice(messages).format(username=username, memory=memory)
    
    @staticmethod
    def objection_expensive(username: str) -> str:
        """
        Обработка возражения 'дорого' для WHALE.
        WHALE не просит скидку, но на всякий случай.
        """
        return f"я понимаю, {username}, но это эксклюзив. больше никто такого не увидит 💎"


# ============================================================================
# MCP ИНСТРУМЕНТЫ (заглушки для интеграции)
# ============================================================================

class MCPTools:
    """
    Интеграция с MCP серверами.
    В реальном исполнении использует npx @lobstore/browseract-pro и whisper-local.
    """
    
    def __init__(self):
        self.browseract_pro = None  # Будет инициализировано при подключении
        self.whisper_local = None
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Авторизация на LoyalFans."""
        # Реальная реализация: npx @lobstore/browseract-pro login
        return {"status": "success", "session_id": f"session_{username}_{datetime.now().timestamp()}"}
    
    async def get_messages(self, limit: int = 50, unread_only: bool = True) -> List[Dict]:
        """Получить сообщения."""
        # Реальная реализация: browseract_pro.get_messages()
        return []
    
    async def send_message(self, user: str, text: str) -> Dict[str, Any]:
        """Отправить сообщение."""
        # Реальная реализация: browseract_pro.send_message()
        return {"status": "sent", "to": user, "text": text}
    
    async def get_subscribers(self, limit: int = 100, sort_by: str = "spending") -> List[Dict]:
        """Получить список подписчиков."""
        # Реальная реализация: browseract_pro.get_subscribers()
        return []
    
    async def post_content(self, content_type: str, text: str, media: List[str] = None) -> Dict[str, Any]:
        """Опубликовать контент."""
        # Реальная реализация: browseract_pro.post_content()
        return {"status": "posted", "type": content_type}
    
    async def create_ppv(self, title: str, price: float, media: List[str], description: str = "") -> Dict[str, Any]:
        """Создать PPV контент."""
        # Реальная реализация: browseract_pro.create_ppv()
        return {"status": "created", "ppv_id": f"ppv_{title}_{datetime.now().timestamp()}", "price": price}
    
    async def transcribe(self, audio_file: str, language: str = "ru") -> Dict[str, Any]:
        """Транскрибировать аудио."""
        # Реальная реализация: npx @lobstore/whisper-local transcribe
        return {"status": "transcribed", "text": "", "language": language}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Анализ тональности."""
        # Реальная реализация: whisper_local.analyze_sentiment()
        return {"sentiment": "positive", "score": 0.8}
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Извлечь ключевые слова."""
        # Реальная реализация: whisper_local.extract_keywords()
        return []
    
    async def learn_patterns(self, transcriptions: List[str], target: str) -> Dict[str, Any]:
        """Обучить модель на паттернах."""
        # Реальная реализация: whisper_local.learn_patterns()
        return {"status": "learned", "patterns": len(transcriptions)}


    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """Перейти по URL."""
        # Реальная реализация: browseract_pro.navigate_to(url)
        return {"status": "navigated", "url": url}


# ============================================================================
# ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================================

class SalesAgentWhale:
    """
    Агент для работы с WHALE подписчиками.
    
    Особенности:
    - GFE (Girlfriend Experience) тактика
    - Персональный подход с использованием Mem0
    - Premium контент первым
    - Без скидок (платит за эксклюзивность)
    """
    
    def __init__(self, config: WhaleConfig = None, mock_mode: bool = True):
        self.config = config or WhaleConfig()
        self.mcp = MCPTools()
        self.auth = AuthManager()  # Используем AuthManager для безопасных учетных данных
        self.controller = LoyalFansController(mock_mode=mock_mode)  # Page Controller
        self.subscribers: Dict[str, SubscriberProfile] = {}
        self.message_count_hour = 0
        self.last_reset = datetime.now()
        self.logged_in = False
    
    async def initialize(self) -> Dict[str, Any]:
        """Инициализация агента и подключение к MCP."""
        # Используем AuthManager для безопасного получения учетных данных
        credentials = self.auth.get_loyalfans_credentials()
        
        if not credentials:
            return {"status": "error", "message": "Missing LOYALFANS credentials"}
        
        username, password = credentials
        
        # Логин в LoyalFans
        login_result = await self.mcp.login(username, password)
        
        if login_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Login failed",
                "details": login_result
            }
        
        self.logged_in = True
        
        # Переход в раздел Messages после успешного логина
        print("\n📬 Переход в раздел Messages...")
        messages_result = await self.mcp.navigate_to("https://loyalfans.com/messages")
        
        return {
            "status": "initialized",
            "login": login_result,
            "messages_navigation": messages_result,
            "config": {
                "min_weekly_spend": self.config.min_weekly_spend,
                "max_messages_hour": self.config.max_messages_hour
            }
        }
    
    async def start_workflow(self) -> Dict[str, Any]:
        """
        START команда: Начать рабочий цикл агента.
        1. Подключиться к LoyalFans
        2. Проверить новые сообщения
        3. Сканировать активность подписчиков
        4. Сформировать приоритетный список задач
        """
        # Инициализация
        init_result = await self.initialize()
        if init_result.get("status") == "error":
            return init_result
        
        # Проверка сообщений
        messages = await self.mcp.get_messages(limit=50, unread_only=True)
        
        # Сканирование подписчиков
        subscribers = await self.mcp.get_subscribers(limit=100, sort_by="spending")
        
        # Классификация и формирование задач
        tasks = await self._build_task_list(messages, subscribers)
        
        return {
            "status": "workflow_started",
            "unread_messages": len(messages),
            "active_subscribers": len(subscribers),
            "tasks": tasks
        }
    
    async def _build_task_list(self, messages: List[Dict], subscribers: List[Dict]) -> List[Dict]:
        """Сформировать приоритетный список задач."""
        tasks = []
        
        # Приоритет 1: Новые сообщения (критично)
        for msg in messages:
            tasks.append({
                "priority": "critical",
                "type": "reply",
                "subscriber_id": msg.get("from_user"),
                "message": msg.get("text")
            })
        
        # Приоритет 2: Новые подписчики (важно)
        for sub in subscribers:
            if sub.get("is_new"):
                tasks.append({
                    "priority": "important",
                    "type": "greeting",
                    "subscriber_id": sub.get("username")
                })
        
        # Приоритет 3: WHALE подписчики (обычно)
        for sub in subscribers:
            spent_weekly = sub.get("spent_weekly", 0)
            if spent_weekly >= self.config.min_weekly_spend:
                tasks.append({
                    "priority": "normal",
                    "type": "whale_engage",
                    "subscriber_id": sub.get("username"),
                    "spent_weekly": spent_weekly
                })
        
        return tasks
    
    async def process_incoming_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработать входящее сообщение от подписчика.
        Проверяет spent_weekly и подготавливает ответ по сценарию GFE.
        
        Args:
            message: Dict с полями from_user, text, spent_weekly и т.д.
            
        Returns:
            Dict с подготовленным ответом (НЕ отправляет, только готовит)
        """
        from_user = message.get("from_user", "unknown")
        spent_weekly = message.get("spent_weekly", 0.0)
        message_text = message.get("text", "")
        
        print(f"\n📬 Входящее сообщение от {from_user}")
        print(f"   spent_weekly: ${spent_weekly:.2f}")
        
        # Проверка: если spent_weekly > 50, это WHALE - используем GFE сценарий
        if spent_weekly > self.config.min_weekly_spend:
            print(f"   🐋 WHALE detected! Подготовка GFE ответа...")
            
            # Подготовка GFE ответа (только подготовка, не отправляем)
            prepared_response = self._prepare_gfe_response(
                username=from_user,
                spent_weekly=spent_weekly,
                original_message=message_text
            )
            
            return {
                "status": "prepared",
                "gfe_ready": True,
                "subscriber_type": "WHALE",
                "spent_weekly": spent_weekly,
                "prepared_message": prepared_response,
                "action": "ready_to_send",
                "note": "Ответ подготовлен, но НЕ отправлен (требует подтверждения)"
            }
        else:
            # Обычный подписчик
            print(f"   💬 Обычный подписчик")
            
            return {
                "status": "prepared",
                "gfe_ready": False,
                "subscriber_type": "REGULAR",
                "spent_weekly": spent_weekly,
                "prepared_message": None,
                "action": "skip"
            }
    
    async def _get_memory_context(self, fan_id: str, username: str) -> List[str]:
        """
        Получить контекст из памяти для пользователя.
        Context Injection - извлекает последние факты перед генерацией ответа.
        
        Args:
            fan_id: ID пользователя
            username: Имя пользователя
            
        Returns:
            Список фактов из памяти
        """
        try:
            context = await memory_manager.get_context_for_response(fan_id, username)
            if context.recent_facts:
                print(f"   💭 Загружено из памяти: {len(context.recent_facts)} фактов")
                for i, fact in enumerate(context.recent_facts, 1):
                    print(f"      {i}. {fact}")
            return context.recent_facts
        except Exception as e:
            print(f"   ⚠️ Ошибка загрузки памяти: {e}")
            return []
    
    async def _save_to_memory(self, fan_id: str, username: str,
                            message: str, response: str) -> List:
        """
        Сохранить факты из разговора в память.
        Long-term Memory - чтобы агент помнил о пользователе.
        
        Args:
            fan_id: ID пользователя
            username: Имя пользователя
            message: Сообщение от пользователя
            response: Ответ агента
            
        Returns:
            Список сохраненных фактов
        """
        try:
            # Извлекаем и сохраняем факты
            saved_facts = await memory_manager.extract_and_save_facts(
                user_id=fan_id,
                message=message,
                response=response
            )
            if saved_facts:
                print(f"   💾 Сохранено в память: {len(saved_facts)} фактов")
            return saved_facts
        except Exception as e:
            print(f"   ⚠️ Ошибка сохранения в память: {e}")
            return []
    
    def _prepare_gfe_response(self, username: str, spent_weekly: float,
                            original_message: str, memory_facts: List[str] = None) -> str:
        """
        Подготовить GFE (Girlfriend Experience) ответ для WHALE подписчика.
        Теперь с использованием фактов из памяти И ПСИХОТИПА!
        
        Args:
            username: Имя подписчика
            spent_weekly: Траты за неделю
            original_message: Оригинальное сообщение от подписчика
            memory_facts: Факты из памяти для персонализации
            
        Returns:
            Подготовленный текст ответа (не отправляется)
        """
        import random
        
        # Шаг 1: Определяем психотип клиента по его сообщению
        psychotype = PsychotypeDetector.detect(original_message)
        print(f"   🎯 Определен психотип: {psychotype}")
        
        # Шаг 2: Используем адаптивные скрипты для генерации ответа
        adaptive_response = AdaptiveSalesScripts.generate_adaptive_response(
            username=username,
            psychotype=psychotype,
            memory_facts=memory_facts,
            spent_weekly=spent_weekly
        )
        
        # Шаг 3: Логируем (старая логика для совместимости)
        print(f"\n🐋 GFE ОТВЕТ ПОДГОТОВЛЕН (с адаптивным стилем):")
        print(f"   Для: {username}")
        print(f"   spent_weekly: ${spent_weekly:.2f}")
        print(f"   Психотип: {psychotype}")
        if memory_facts:
            print(f"   💭 Использовано фактов из памяти: {len(memory_facts)}")
        print(f"   ---")
        print(adaptive_response)
        print(f"   ---")
        
        return adaptive_response
    
    async def engage_whale(self, subscriber: SubscriberProfile) -> Dict[str, Any]:
        """
        ENGAGE команда для WHALE: Начать диалог с крупным покупателем.
        
        Тактика:
        1. Загрузить профиль из Mem0
        2. Персональное приветствие с GFE
        3. Предложить premium контент
        """
        # Получить персональный факт из Mem0
        personal_fact = subscriber.notes or ""
        
        # GFE приветствие
        greeting = SalesScripts.whale_greeting(subscriber.username, personal_fact)
        
        # Отправить сообщение через Controller (реальная отправка)
        result = await self.controller.send_message(subscriber.username, greeting)
        print(f"   ✓ GFE приветствие отправлено: {subscriber.username}")
        
        # Предложить premium контент (через паузу для реалистичности)
        await asyncio.sleep(2)
        
        # Пример premium предложения
        premium_offer = SalesScripts.premium_offer(
            content_title="эксклюзивное видео",
            price=75.0,
            preview_path=f"{self.config.premium_vault_path}/teaser.mp4"
        )
        
        result = await self.controller.send_message(subscriber.username, premium_offer)
        print(f"   ✓ Premium предложение отправлено: {subscriber.username}")
        
        # Обновить профиль в Mem0
        await self._update_mem0(subscriber)
        
        return {
            "status": "engaged",
            "username": subscriber.username,
            "greeting_sent": True,
            "premium_offered": True
        }
    
    async def process_incoming_from_controller(self) -> Dict[str, Any]:
        """
        Обработать входящие сообщения через LoyalFansController.
        
       流程:
        1. Получить непрочитанные сообщения через controller.get_unread_messages()
        2. Для каждого сообщения:
           - Проверить траты через controller.get_user_spend()
           - Если это Кит (> $50) -> сгенерировать GFE ответ
           - Отправить ответ через controller.send_message()
        """
        print("\n🔄 Обработка входящих сообщений через Controller...")
        
        # Шаг 1: Получаем непрочитанные сообщения
        messages = await self.controller.get_unread_messages()
        print(f"   ✓ Получено сообщений: {len(messages)}")
        
        whales_engaged = 0
        whales_data = []  # Данные о китах для Telegram уведомлений
        
        # Шаг 2: Обрабатываем каждое сообщение
        for msg in messages:
            print(f"\n   📬 Сообщение от: {msg.username}")
            print(f"      Текст: {msg.text[:50]}...")
            
            # Проверяем траты пользователя
            profile = await self.controller.get_user_spend(msg.profile_url)
            print(f"      spent_weekly: ${profile.spent_weekly:.2f}")
            print(f"      is_whale: {profile.is_whale}")
            
            # Если это Кит - генерируем и отправляем GFE ответ
            if profile.is_whale:
                print(f"      🐋 WHALE detected! Генерация GFE ответа...")
                
                # === Context Injection: Загружаем факты из памяти ===
                memory_facts = await self._get_memory_context(
                    fan_id=msg.profile_url,
                    username=msg.username
                )
                
                # Генерируем GFE ответ с использованием памяти
                gfe_response = self._prepare_gfe_response(
                    username=msg.username,
                    spent_weekly=profile.spent_weekly,
                    original_message=msg.text,
                    memory_facts=memory_facts
                )
                
                # Отправляем через controller
                await self.controller.send_message(msg.username, gfe_response)
                print(f"      ✓ GFE ответ отправлен")
                
                # === Long-term Memory: Сохраняем факты о пользователе ===
                await self._save_to_memory(
                    fan_id=msg.profile_url,
                    username=msg.username,
                    message=msg.text,
                    response=gfe_response
                )
                
                whales_engaged += 1
                
                # Сохраняем данные о ките для Telegram уведомления
                whales_data.append({
                    "message_id": msg.message_id,
                    "username": msg.username,
                    "message": msg.text,
                    "response": gfe_response,
                    "spent_weekly": profile.spent_weekly
                })
            else:
                print(f"      💬 Обычный подписчик - пропускаем")
        
        return {
            "status": "processed",
            "total_messages": len(messages),
            "whales_engaged": whales_engaged,
            "whales_data": whales_data
        }
    
    async def send_premium_content(self, subscriber: SubscriberProfile, content_id: str) -> Dict[str, Any]:
        """
        Отправить premium контент WHALE подписчику.
        Приоритетная доставка из /vault/premium.
        """
        # Создать PPV
        ppv_result = await self.mcp.create_ppv(
            title=f"Эксклюзив для {subscriber.username}",
            price=75.0,
            media=[content_id],
            description="Эксклюзивный контент"
        )
        
        # Отправить ссылку подписчику
        message = f"вот твой эксклюзив, мой хороший 💋 [PPV_LINK]"
        await self.mcp.send_message(subscriber.username, message)
        
        return {
            "status": "premium_sent",
            "ppv_id": ppv_result.get("ppv_id"),
            "to": subscriber.username
        }
    
    async def learn_from_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        LEARN команда: Активировать режим обучения.
        Использует whisper-local для анализа аудио/видео.
        """
        # Транскрибировать
        transcription = await self.mcp.transcribe(audio_file, language="ru")
        
        # Анализ тональности
        sentiment = await self.mcp.analyze_sentiment(transcription.get("text", ""))
        
        # Извлечь ключевые слова
        keywords = await self.mcp.extract_keywords(
            transcription.get("text", ""),
            max_keywords=10
        )
        
        # Обучить модель
        learn_result = await self.mcp.learn_patterns(
            transcriptions=[transcription.get("text", "")],
            target="whale_preferences"
        )
        
        return {
            "status": "learned",
            "transcription": transcription,
            "sentiment": sentiment,
            "keywords": keywords,
            "patterns_updated": learn_result.get("patterns", 0)
        }
    
    async def _update_mem0(self, subscriber: SubscriberProfile) -> Dict[str, Any]:
        """Обновить профиль подписчика в Mem0."""
        # В реальной реализации: API call к Mem0
        profile_data = subscriber.to_mem0_format()
        self.subscribers[subscriber.fan_id] = subscriber
        
        return {"status": "updated", "profile": profile_data}
    
    def _calculate_typing_time(self, text: str) -> int:
        """Рассчитать время 'печатания' для реалистичности."""
        return len(text) * self.config.typing_speed_ms
    
    async def _check_rate_limit(self) -> bool:
        """Проверить rate limit (anti-ban)."""
        now = datetime.now()
        
        # Сброс счетчика каждый час
        if (now - self.last_reset).total_seconds() > 3600:
            self.message_count_hour = 0
            self.last_reset = now
        
        if self.message_count_hour >= self.config.max_messages_hour:
            return False
        
        self.message_count_hour += 1
        return True


# ============================================================================
# ПСИХОТИПЫ VIP КЛИЕНТОВ
# ============================================================================

class PsychotypeDetector:
    """
    Определение психотипа клиента по ключевым словам и паттернам поведения.
    
    Type A (Interactive): Предпочитает пошаговое взаимодействие, задает вопросы
    Type B (Power Dynamics): Предпочитает, чтобы инициатива исходила от агента
    """
    
    # Ключевые слова для Type A (Interactive)
    TYPE_A_KEYWORDS = [
        "how to", "what to do", "teach me", "show me",
        "explain", "guide me", "help me", "what should",
        "instructions", "steps", "learn", "understand",
        "как сделать", "что делать", "научи", "покажи",
        "объясни", "помоги", "расскажи", "шаг", "научи меня"
    ]
    
    # Ключевые слова для Type B (Power Dynamics)
    TYPE_B_KEYWORDS = [
        "anything", "whatever", "your choice", "surprise me",
        "your wish", "do what you want", "i'm yours",
        "command me", "tell me what to do", "submit", "obey",
        "что угодно", "как хочешь", "твой выбор", "удиви меня",
        "твоя воля", "делай что хочешь", "я твой", "прикажи",
        "слушаю", "подчиняюсь", "буду делать как скажешь"
    ]
    
    @classmethod
    def detect(cls, message: str) -> str:
        """
        Определить психотип клиента по сообщению.
        
        Args:
            message: Текст сообщения от клиента
            
        Returns:
            'TYPE_A' (Interactive) или 'TYPE_B' (Power Dynamics)
        """
        message_lower = message.lower()
        
        # Подсчет совпадений
        type_a_score = 0
        type_b_score = 0
        
        for keyword in cls.TYPE_A_KEYWORDS:
            if keyword.lower() in message_lower:
                type_a_score += 1
                
        for keyword in cls.TYPE_B_KEYWORDS:
            if keyword.lower() in message_lower:
                type_b_score += 1
        
        # Дополнительная проверка паттернов поведения
        # Type A: много вопросов
        question_count = message.count('?')
        if question_count >= 2:
            type_a_score += 1
        
        # Type B: мало вопросов, признаки подчинения
        if question_count == 0 and type_b_score == 0:
            # Проверяем косвенные признаки
            submission_indicators = ["ok", "okay", "sure", "yes", "да", "хорошо"]
            if any(ind in message_lower for ind in submission_indicators):
                type_b_score += 0.5
        
        # Определение результата
        if type_b_score > type_a_score:
            return "TYPE_B"
        elif type_a_score > type_b_score:
            return "TYPE_A"
        else:
            # По умолчанию Type A (безопаснее)
            return "TYPE_A"
    
    @classmethod
    def get_response_style(cls, psychotype: str) -> dict:
        """
        Получить шаблон ответа для определенного психотипа.
        
        Args:
            psychotype: 'TYPE_A' или 'TYPE_B'
            
        Returns:
            Словарь с компонентами ответа
        """
        if psychotype == "TYPE_B":
            return {
                "style": "assertive",
                "use_questions": False,
                "template": "command"
            }
        else:
            return {
                "style": "interactive",
                "use_questions": True,
                "template": "dialogue"
            }


class AdaptiveSalesScripts:
    """
    Адаптивные скрипты продаж, учитывающие психотип клиента.
    """
    
    @staticmethod
    def generate_adaptive_response(
        username: str,
        psychotype: str,
        memory_facts: list = None,
        spent_weekly: float = 0.0
    ) -> str:
        """
        Генерирует адаптивный ответ с учетом психотипа.
        
        Args:
            username: Имя клиента
            psychotype: 'TYPE_A' или 'TYPE_B'
            memory_facts: Факты из памяти
            spent_weekly: Траты за неделю
            
        Returns:
            Готовый текст ответа
        """
        import random
        
        if psychotype == "TYPE_B":
            # Power Dynamics - уверенный, директивный стиль
            return AdaptiveSalesScripts._generate_type_b_response(
                username, memory_facts, spent_weekly
            )
        else:
            # Interactive - диалоговый стиль
            return AdaptiveSalesScripts._generate_type_a_response(
                username, memory_facts, spent_weekly
            )
    
    @staticmethod
    def _generate_type_b_response(username: str, memory_facts: list, spent_weekly: float) -> str:
        """Генерация ответа для Type B (Power Dynamics)."""
        import random
        
        openers = [
            f"Хороший мальчик. 😏",
            f"Мне нравится твоё послушание. 💋",
            f"Ты знаешь, что мне нравится... 😘",
        ]
        
        # Основная часть - директивные утверждения
        commands = [
            "Сейчас я тебе скажу, что ты будешь делать. Слушай внимательно...",
            "Первое: ты откроешь ссылку, которую я пришлю.",
            "Второе: ты сделаешь то, что я скажу.",
            "И третье - ты мне за это спасибо. 💋",
            "Не задавай вопросов. Просто делай, как я скажу.",
        ]
        
        # Добавляем факт из памяти если есть
        if memory_facts:
            memory_tease = f"Помнишь, {random.choice(memory_facts)}? Это было мило... 💕"
        else:
            memory_tease = random.choice([
                "Я думала о тебе сегодня... 💭",
                "Знаешь, ты меня радуешь. 😘",
                "Мне нравится, как ты меня слушаешь.",
            ])
        
        closers = [
            "Понятно? 😏",
            "Жду, когда ты всё сделаешь... 💋",
            "Не подведи меня. 😘",
        ]
        
        # Собираем ответ
        return f"{random.choice(openers)}\n\n{memory_tease}\n\n{random.choice(commands)}\n\n{random.choice(closers)}"
    
    @staticmethod
    def _generate_type_a_response(username: str, memory_facts: list, spent_weekly: float) -> str:
        """Генерация ответа для Type A (Interactive)."""
        import random
        
        openers = [
            f"Привет, зайка! 💋",
            f"Ой, привет! Как дела? ✨",
            f"Приветик! Скучала 😘",
        ]
        
        # Диалоговые вопросы
        if memory_facts:
            questions = [
                f"Ооо, помнишь ты говорил про... {random.choice(memory_facts)}?",
                f"Кстати, {username}, это напоминает мне о том, что ты рассказывал: {random.choice(memory_facts)}",
                f"Знаешь, я сегодня думала о тебе... и о том, что ты рассказал: {random.choice(memory_facts)}",
            ]
        else:
            questions = [
                "Можешь написать поподробнее? Мне интересно всё, что ты думаешь 💕",
                "Ооо, это так мило! Расскажи ещё? 🥺",
                "Ой, как интересно! А что ещё скажешь? 💭",
                "Зайка, ты меня рассмешил! 😄",
            ]
        
        closers = [
            "Можешь рассказать ещё? Мне так нравится с тобой общаться 💕",
            "Окей, увидимся! Целую! 😘",
            "Так, мне пора! Не забывай обо мне, лады? 💋",
            "Ладно, напиши ещё, хорошо? 😘",
        ]
        
        return f"{random.choice(openers)}\n\n{random.choice(questions)}\n\n{random.choice(closers)}"


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

async def main():
    """Демонстрация работы агента."""
    agent = SalesAgentWhale()
    
    # Инициализация
    result = await agent.initialize()
    print(f"Agent initialized: {result}")
    
    # Запустить рабочий цикл
    workflow = await agent.start_workflow()
    print(f"Workflow started: {workflow}")
    
    # Пример: работа с WHALE подписчиком
    whale = SubscriberProfile(
        fan_id="123456",
        username="alex_premium",
        spent_total=250.0,
        last_purchase="2026-02-13",
        preferences=["feet", "stockings", "roleplay"],
        profile=SubscriberProfile.PROFILE_WHALE,
        notes="likes afternoon messages"
    )
    
    engage_result = await agent.engage_whale(whale)
    print(f"Whale engaged: {engage_result}")


if __name__ == "__main__":
    asyncio.run(main())
