#!/usr/bin/env python3
"""
Auth Manager - Безопасное управление учетными данными
=====================================================
Загружает и передает учетные данные из переменных окружения в browser-secure.

Использование:
    from auth_manager import AuthManager
    
    auth = AuthManager()
    credentials = auth.getloyalfans_credentials()
    
    if credentials:
        username, password = credentials
        # использовать для логина
"""

import os
import sys
from typing import Optional, Tuple, Dict, Any
from pathlib import Path


class AuthManager:
    """
    Менеджер аутентификации для безопасной работы с учетными данными.
    Загружает данные из переменных окружения (.env).
    """
    
    def __init__(self, env_file: str = None):
        """
        Инициализация менеджера аутентификации.
        
        Args:
            env_file: Путь к .env файлу. По умолчанию - .env в корне проекта.
        """
        self.env_file = env_file or self._find_env_file()
        self._load_env()
        
    def _find_env_file(self) -> Optional[str]:
        """Поиск .env файла в стандартных locations."""
        # Проверяем текущую директорию и родительские
        current = Path.cwd()
        for _ in range(3):
            env_path = current / ".env"
            if env_path.exists():
                return str(env_path)
            current = current.parent
            
        # Проверяем openclaw-enterprise
        oe_path = Path("openclaw-enterprise/.env")
        if oe_path.exists():
            return str(oe_path)
            
        return None
    
    def _load_env(self):
        """Загрузка переменных окружения из .env файла."""
        if not self.env_file or not os.path.exists(self.env_file):
            return
            
        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Не перезаписываем существующие переменные
                    if key not in os.environ:
                        os.environ[key] = value
    
    def get_loyalfans_credentials(self) -> Optional[Tuple[str, str]]:
        """
        Получить учетные данные LoyalFans.
        
        Returns:
            Tuple (username, password) или None если не найдены
        """
        username = os.environ.get('LOYALFANS_USERNAME')
        password = os.environ.get('LOYALFANS_PASSWORD')
        
        if not username or not password:
            print("⚠️ Учетные данные LoyalFans не найдены в переменных окружения")
            print("   Убедитесь, что LOYALFANS_USERNAME и LOYALFANS_PASSWORD установлены")
            return None
            
        # Валидация
        if username == 'your_username' or password == 'your_password':
            print("⚠️ Используются placeholder значения из .env.example!")
            print("   Пожалуйста, обновите .env файл реальными учетными данными")
            return None
            
        return (username, password)
    
    def get_api_key(self) -> Optional[str]:
        """Получить API ключ LoyalFans."""
        api_key = os.environ.get('LOYALFANS_API_KEY')
        if api_key and api_key != 'your_api_key':
            return api_key
        return None
    
    def get_proxy_config(self) -> Optional[Dict[str, Any]]:
        """Получить конфигурацию прокси."""
        if not os.environ.get('PROXY_ENABLED', 'false').lower() == 'true':
            return None
            
        proxy_url = os.environ.get('PROXY_URL')
        if not proxy_url:
            return None
            
        return {
            'url': proxy_url,
            'enabled': True
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        """Получить полную конфигурацию аутентификации."""
        credentials = self.get_loyalfans_credentials()
        
        return {
            'has_credentials': credentials is not None,
            'username': credentials[0] if credentials else None,
            'password': '***скрыто***' if credentials else None,
            'api_key': self.get_api_key(),
            'proxy': self.get_proxy_config(),
            'env_file': self.env_file
        }
    
    def validate(self) -> Tuple[bool, str]:
        """
        Проверить валидность учетных данных.
        
        Returns:
            (is_valid, message)
        """
        credentials = self.get_loyalfans_credentials()
        
        if not credentials:
            return False, "Учетные данные не найдены"
            
        username, password = credentials
        
        if len(username) < 3:
            return False, "Слишком короткое имя пользователя"
            
        if len(password) < 6:
            return False, "Слишком короткий пароль"
            
        return True, "Учетные данные валидны"
    
    def get_browseract_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию для передачи в browser-secure/MCP.
        
        Returns:
            Dict с учетными данными для browseract-pro
        """
        credentials = self.get_loyalfans_credentials()
        
        if not credentials:
            return {
                'status': 'error',
                'message': 'Учетные данные не доступны'
            }
        
        username, password = credentials
        
        return {
            'status': 'success',
            'credentials': {
                'username': username,
                'password': password
            },
            'api_key': self.get_api_key(),
            'proxy': self.get_proxy_config()
        }


# Удобная функция для быстрого доступа
def get_auth() -> AuthManager:
    """Получить экземпляр AuthManager."""
    return AuthManager()


if __name__ == "__main__":
    # Тестирование
    print("="*60)
    print("🔐 Auth Manager - Тестирование")
    print("="*60)
    
    auth = AuthManager()
    config = auth.get_all_config()
    
    print(f"\n📋 Конфигурация:")
    print(f"   .env файл: {config['env_file']}")
    print(f"   Учетные данные: {'✅' if config['has_credentials'] else '❌'}")
    print(f"   Username: {config['username'] or 'N/A'}")
    print(f"   API Key: {'✅' if config['api_key'] else '❌'}")
    print(f"   Proxy: {'✅' if config['proxy'] else '❌'}")
    
    is_valid, message = auth.validate()
    print(f"\n✅ Валидация: {message}")
    
    print(f"\n📦 Конфигурация для browseract:")
    browser_config = auth.get_browseract_config()
    print(f"   Status: {browser_config['status']}")
