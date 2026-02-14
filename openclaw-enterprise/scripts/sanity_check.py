#!/usr/bin/env python3
"""
OpenClaw Enterprise - Sanity Check
===================================
Скрипт для проверки связи с реальным аккаунтом LoyalFans.

Функционал:
1. Логинится в аккаунт
2. Переходит на страницу сообщений
3. Выводит имя последнего написавшего человека
4. НЕ отправляет никаких сообщений

Запуск: python scripts/sanity_check.py
"""

import os
import sys
import asyncio

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'openclaw-enterprise'))

from workflows.loyalfans_controller import LoyalFansController
from scripts.auth_manager import AuthManager


async def sanity_check():
    """Проверка связи с реальным аккаунтом."""
    print("=" * 60)
    print("🧪 OpenClaw Enterprise - Sanity Check")
    print("=" * 60)
    print()
    
    # Получаем учетные данные
    auth = AuthManager()
    credentials = auth.get_loyalfans_credentials()
    
    if not credentials:
        print("❌ ОШИБКА: Не найдены учетные данные LOYALFANS")
        print("   Проверьте файл .env")
        return False
    
    username, password = credentials
    print(f"📋 Учетные данные: {username}")
    print()
    
    # Создаем контроллер
    controller = LoyalFansController(mock_mode=False)
    
    # 1. Логин
    print("🔐 Шаг 1: Логин...")
    try:
        result = await controller.login(username, password)
        if result.get('status') == 'success':
            print(f"   ✅ Логин успешен! Session: {result.get('session_id', 'N/A')[:20]}...")
        else:
            print(f"   ❌ Ошибка логина: {result}")
            return False
    except Exception as e:
        print(f"   ❌ Исключение при логине: {e}")
        return False
    
    print()
    
    # 2. Переход на страницу сообщений
    print("📬 Шаг 2: Переход на страницу сообщений...")
    try:
        await controller.navigate_to("https://loyalfans.com/messages")
        print("   ✅ Навигация выполнена")
    except Exception as e:
        print(f"   ❌ Ошибка навигации: {e}")
        return False
    
    print()
    
    # 3. Получение HTML страницы
    print("📥 Шаг 3: Получение HTML страницы...")
    try:
        html = await controller.get_page_html()
        print(f"   ✅ Получено {len(html)} символов HTML")
    except Exception as e:
        print(f"   ❌ Ошибка получения HTML: {e}")
        return False
    
    print()
    
    # 4. Парсинг сообщений
    print("🔍 Шаг 4: Парсинг сообщений...")
    try:
        messages = await controller.get_unread_messages()
        print(f"   ✅ Найдено сообщений: {len(messages)}")
        
        if messages:
            print()
            print("📬 Последнее сообщение:")
            last_msg = messages[0]
            print(f"   От: {last_msg.username}")
            print(f"   Текст: {last_msg.text[:100]}...")
            print(f"   URL профиля: {last_msg.profile_url}")
        else:
            print("   ℹ️ Нет непрочитанных сообщений")
            
    except Exception as e:
        print(f"   ❌ Ошибка парсинга: {e}")
        # Показываем часть HTML для отладки
        print(f"   📄 HTML (первые 500 символов):")
        print(html[:500])
        return False
    
    print()
    print("=" * 60)
    print("✅ SANITY CHECK ПРОЙДЕН!")
    print("   Система готова к работе с реальным аккаунтом.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(sanity_check())
    sys.exit(0 if success else 1)
