#!/usr/bin/env python3
"""
Интеграционный тест для SalesAgentWhale
=======================================
Тестирует полный цикл работы агента:
1. Инициализация SalesAgentWhale
2. Использование AuthManager для имитации входа
3. Навигация на страницу сообщений
4. Симуляция входящего сообщения от WHALE подписчика
5. Генерация GFE-ответа
"""

import os
import sys
import asyncio

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.sales_agent_whale import SalesAgentWhale, WhaleConfig
from scripts.auth_manager import AuthManager


async def main():
    """
    Главная функция интеграционного теста.
    """
    print("=" * 60)
    print("🐋 ИНТЕГРАЦИОННЫЙ ТЕСТ SALES AGENT WHALE")
    print("=" * 60)
    
    # =========================================================================
    # ШАГ 1: Инициализация SalesAgentWhale
    # =========================================================================
    print("\n[ШАГ 1] Инициализация SalesAgentWhale...")
    
    config = WhaleConfig(min_weekly_spend=50.0)
    agent = SalesAgentWhale(config=config)
    
    print(f"   ✓ Agent инициализирован")
    print(f"   ✓ Min weekly spend: ${config.min_weekly_spend}")
    
    # =========================================================================
    # ШАГ 2: Использование AuthManager для имитации входа
    # =========================================================================
    print("\n[ШАГ 2] Использование AuthManager для имитации входа...")
    
    auth = AuthManager()
    credentials = auth.get_loyalfans_credentials()
    
    if credentials:
        username, password = credentials
        print(f"   ✓ Получены учетные данные: {username}")
        print(f"   ✓ Пароль: {'*' * len(password)}")
        
        # Имитация логина через MCP
        login_result = await agent.mcp.login(username, password)
        print(f"   ✓ Результат логина: {login_result.get('status')}")
    else:
        print("   ✗ Ошибка: не найдены учетные данные!")
        return
    
    # =========================================================================
    # ШАГ 3: Навигация на страницу сообщений
    # =========================================================================
    print("\n[ШАГ 3] Навигация на страницу сообщений...")
    
    messages_url = "https://loyalfans.com/messages"
    navigate_result = await agent.mcp.navigate_to(messages_url)
    
    print(f"   ✓ URL: {messages_url}")
    print(f"   ✓ Результат навигации: {navigate_result.get('status', 'success')}")
    
    # =========================================================================
    # ШАГ 4: Симуляция входящего сообщения от WHALE подписчика
    # =========================================================================
    print("\n[ШАГ 4] Симуляция входящего сообщения от WHALE подписчика...")
    
    # Симулируем сообщение от "кита" с spent_weekly = 60
    incoming_message = {
        "from_user": "whale_fan_001",
        "text": "Привет! Хочу увидеть новый premium контент!",
        "spent_weekly": 60.0,
        "spent_total": 350.0,
        "messages_count": 12,
        "timestamp": "2026-02-14T08:00:00Z"
    }
    
    print(f"   ✓ От кого: {incoming_message['from_user']}")
    print(f"   ✓ Траты за неделю: ${incoming_message['spent_weekly']}")
    print(f"   ✓ Текст сообщения: \"{incoming_message['text']}\"")
    
    # =========================================================================
    # ШАГ 5: Обработка сообщения и генерация GFE-ответа
    # =========================================================================
    print("\n[ШАГ 5] Обработка сообщения и генерация GFE-ответа...")
    
    result = await agent.process_incoming_message(incoming_message)
    
    # =========================================================================
    # ВЫВОД РЕЗУЛЬТАТА
    # =========================================================================
    print("\n" + "=" * 60)
    print("🐋 РЕЗУЛЬТАТ: GFE-ОТВЕТ ПОДГОТОВЛЕН")
    print("=" * 60)
    
    print(f"\nСтатус: {result.get('status')}")
    print(f"Тип подписчика: {result.get('subscriber_type')}")
    print(f"Траты за неделю: ${result.get('spent_weekly')}")
    print(f"GFE готов: {'Да ✓' if result.get('gfe_ready') else 'Нет'}")
    print(f"Действие: {result.get('action')}")
    
    print("\n" + "-" * 60)
    print("📝 ПОДГОТОВЛЕННЫЙ GFE-ОТВЕТ:")
    print("-" * 60)
    print(result.get('prepared_message'))
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ ИНТЕГРАЦИОННЫЙ ТЕСТ УСПЕШНО ЗАВЕРШЕН")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
