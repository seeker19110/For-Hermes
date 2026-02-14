#!/usr/bin/env python3
"""
Telegram Connection Test Script
Отправляет тестовое сообщение администратору для проверки работоспособности Telegram Bot API
"""

import os
import sys
import requests
from pathlib import Path

# Добавляем путь для импорта config
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_env_vars():
    """Загрузка переменных окружения из .env файла"""
    env_path = Path(__file__).parent.parent / ".env"
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    return env_vars.get('TELEGRAM_TOKEN'), env_vars.get('TELEGRAM_ADMIN_ID')

def send_test_message(token: str, admin_id: str) -> bool:
    """Отправляет тестовое сообщение через Telegram Bot API"""
    
    if not token or not admin_id:
        print("❌ Ошибка: TELEGRAM_TOKEN или TELEGRAM_ADMIN_ID не найдены в .env")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": admin_id,
        "text": "🚀 Система управления продажами онлайн. Связь установлена!",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Сообщение успешно отправлено!")
            print(f"   Chat ID: {result['result']['chat']['id']}")
            print(f"   Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Ошибка API: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 Telegram Connection Test")
    print("=" * 50)
    
    token, admin_id = load_env_vars()
    
    print(f"\n📋 Конфигурация:")
    print(f"   Token: {'*' * 20}{token[-10:] if token else 'NOT SET'}")
    print(f"   Admin ID: {admin_id or 'NOT SET'}")
    
    print("\n📤 Отправка тестового сообщения...")
    success = send_test_message(token, admin_id)
    
    if success:
        print("\n" + "=" * 50)
        print("✨ Тест пройден успешно!")
        print("=" * 50)
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ Тест не пройден. Проверьте настройки.")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
