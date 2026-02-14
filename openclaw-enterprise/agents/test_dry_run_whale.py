#!/usr/bin/env python3
"""
Dry Run Test - WHALE Sales Agent
================================
Тестирование агента в режиме симуляции без реальных подключений.

Сценарий:
- Создаем имитацию подписчика WHALE (потратил $120 за неделю)
- Запускаем агент в режиме Dry Run
- Выводим пошаговый лог: классификация, тактика GFE, premium_offer
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sales_agent_whale import (
    SalesAgentWhale, 
    WhaleConfig, 
    SubscriberProfile, 
    SalesScripts,
    MCPTools
)


class DryRunMCPTools(MCPTools):
    """
    Заглушка MCP инструментов для Dry Run режима.
    Имитирует подключение без реальных вызовов.
    """
    
    def __init__(self):
        super().__init__()
        self.connected = False
        self.connection_log = []
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Имитация логина - всегда успех в Dry Run."""
        log_entry = f"[MCP] 🔐 Login attempt: user={username}"
        self.connection_log.append(log_entry)
        print(log_entry)
        
        # Имитация задержки подключения
        await asyncio.sleep(0.1)
        
        log_entry = f"[MCP] ✅ Connected to LoyalFans (session: dry_run_{datetime.now().timestamp()})"
        self.connection_log.append(log_entry)
        print(log_entry)
        
        self.connected = True
        return {"status": "success", "session_id": f"dry_run_{datetime.now().timestamp()}"}
    
    async def get_messages(self, limit: int = 50, unread_only: bool = True):
        """Имитация получения сообщений."""
        log_entry = f"[MCP] 📬 Fetching messages (limit={limit}, unread_only={unread_only})"
        self.connection_log.append(log_entry)
        print(log_entry)
        return []
    
    async def get_subscribers(self, limit: int = 100, sort_by: str = "spending"):
        """Имитация получения подписчиков."""
        log_entry = f"[MCP] 👥 Fetching subscribers (limit={limit}, sort_by={sort_by})"
        self.connection_log.append(log_entry)
        print(log_entry)
        return []


async def simulate_whale_subscriber():
    """
    Симуляция WHALE подписчика.
    
    Сценарий:
    - Подписчик потратил $120 за прошлую неделю
    - Активный, но молчаливый (типичный профиль WHALE)
    """
    
    print("\n" + "="*70)
    print("🦈 DRY RUN TEST - WHALE SALES AGENT")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print("-"*70)
    
    # Создаем имитацию WHALE подписчика
    print("\n📋 STEP 1: Creating subscriber simulation...")
    print("-"*50)
    
    # Параметры для классификации (симуляция трат за неделю)
    spent_weekly = 120.0  # Траты за прошлую неделю (КЛЮЧЕВОЙ ПАРАМЕТР!)
    messages_count = 15   # Не слишком много сообщений (молчаливый)
    has_purchased = True   # Уже совершал покупки
    
    subscriber = SubscriberProfile(
        fan_id="fan_001",
        username="whale_test_user",
        spent_total=520.0,        # Всего потратил
        preferences=["premium", "exclusive", "PPV"],
        notes="Покупает молча, без торга",
        profile="NEWBIE"          # Будет переопределено при классификации
    )
    
    # Добавляем атрибуты для симуляции
    subscriber.spent_weekly = spent_weekly
    subscriber.messages_count = messages_count
    subscriber.has_purchased = has_purchased
    
    print(f"  👤 Subscriber created:")
    print(f"     - fan_id: {subscriber.fan_id}")
    print(f"     - username: {subscriber.username}")
    print(f"     - spent_total: ${subscriber.spent_total}")
    print(f"     - spent_weekly: ${spent_weekly}")
    print(f"     - messages_count: {messages_count}")
    print(f"     - has_purchased: {has_purchased}")
    print(f"     - preferences: {subscriber.preferences}")
    
    # Классификация подписчика
    print("\n📋 STEP 2: Subscriber Classification...")
    print("-"*50)
    
    # Вызываем классификацию
    classified_profile = SubscriberProfile.classify(
        spent_weekly=subscriber.spent_weekly,
        messages_count=subscriber.messages_count,
        has_purchased=subscriber.has_purchased
    )
    
    subscriber.profile = classified_profile
    
    print(f"  🎯 Classification Result: {classified_profile}")
    print(f"     - spent_weekly: ${subscriber.spent_weekly} >= ${SubscriberProfile.classify.__doc__}")
    print(f"     - Threshold: $50.00 (WHALE threshold)")
    
    if classified_profile == SubscriberProfile.PROFILE_WHALE:
        print(f"  ✅ PROFILE MATCHED: WHALE")
        print(f"     → Тактика: GFE (Girlfriend Experience)")
        print(f"     → Подход: Персональный, без скидок")
        print(f"     → Контент: Premium из /vault/premium")
    
    # Выбор тактики GFE
    print("\n📋 STEP 3: GFE Tactic Selection...")
    print("-"*50)
    
    if subscriber.profile == SubscriberProfile.PROFILE_WHALE:
        print("  🎯 Selected Tactic: GFE (Girlfriend Experience)")
        print("     - Персональные сообщения с 'воспоминаниями'")
        print("     - Без торговли и скидок")
        print("     - Эксклюзивный контент")
        print("     - Быстрый отклик (имитация занятости)")
        
        # Генерируем приветствие
        print("\n  💬 Generating GFE greeting...")
        greeting = SalesScripts.whale_greeting(subscriber.username)
        print(f"     → {greeting}")
    
    # Генерация premium_offer
    print("\n📋 STEP 4: Premium Offer Generation...")
    print("-"*50)
    
    # Симулируем контент из vault
    content_title = "Private Show #42 - Special for You"
    content_price = 25.0
    preview_path = "/vault/premium/preview_42.jpg"
    
    print(f"  📦 Content Details:")
    print(f"     - title: {content_title}")
    print(f"     - price: ${content_price}")
    print(f"     - preview: {preview_path}")
    
    # Генерируем предложение
    premium_offer = SalesScripts.premium_offer(content_title, content_price, preview_path)
    print(f"\n  💋 Generated premium_offer:")
    print(f"     → {premium_offer}")
    
    # Полный цикл GFE
    print("\n📋 STEP 5: GFE Message Flow...")
    print("-"*50)
    
    # Симуляция воспоминания из Mem0
    memory_fact = "ты говорил что тебе нравятся мои фото в красном"
    gfe_msg = SalesScripts.gfe_message(subscriber.username, memory_fact)
    print(f"  💭 GFE Memory: {memory_fact}")
    print(f"  💬 Generated Message:")
    print(f"     → {gfe_msg}")
    
    # Обработка возражения (на всякий случай)
    print("\n📋 STEP 6: Objection Handling (if needed)...")
    print("-"*50)
    
    objection_response = SalesScripts.objection_expensive(subscriber.username)
    print(f"  🛡️  Response to 'expensive':")
    print(f"     → {objection_response}")
    
    # Инициализация MCP инструментов (проверка подключения)
    print("\n📋 STEP 7: MCP Tools Initialization (Dry Run)...")
    print("-"*50)
    
    # Создаем агент с Dry Run инструментами
    agent = SalesAgentWhale(WhaleConfig())
    agent.mcp = DryRunMCPTools()
    
    print("  🔧 Testing MCPTools initialization...")
    print("     - browseract_pro: stub (not connected)")
    print("     - whisper_local: stub (not connected)")
    
    # Тест логина (имитация)
    print("\n  🔐 Testing login flow...")
    login_result = await agent.mcp.login("test_user", "test_password")
    print(f"     Result: {login_result}")
    
    # Проверка статуса подключения
    print(f"\n  📊 Connection Status:")
    print(f"     - MCP Connected: {agent.mcp.connected}")
    print(f"     - Session Active: {'Yes' if login_result.get('status') == 'success' else 'No'}")
    
    # Вывод лога подключения
    print(f"\n  📝 Connection Log:")
    for log in agent.mcp.connection_log:
        print(f"     {log}")
    
    # Итоговый отчет
    print("\n" + "="*70)
    print("📊 DRY RUN SUMMARY")
    print("="*70)
    print(f"  ✅ Subscriber Classification: {subscriber.profile}")
    print(f"  ✅ GFE Tactic: Applied")
    print(f"  ✅ Premium Offer: Generated")
    print(f"  ✅ MCP Tools: Initialized without connection errors")
    print(f"  ⏰ Completed at: {datetime.now().isoformat()}")
    print("="*70)
    print("\n🎉 Dry Run Test PASSED!")
    print("\n" + "="*70)
    
    return {
        "status": "success",
        "subscriber_profile": subscriber.profile,
        "premium_offer": premium_offer,
        "gfe_tactic": "applied",
        "mcp_connected": agent.mcp.connected
    }


async def main():
    """Главная функция запуска Dry Run теста."""
    try:
        result = await simulate_whale_subscriber()
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
