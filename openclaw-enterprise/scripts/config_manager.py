#!/usr/bin/env python3
"""
Config Manager - Управление конфигурацией бота
===============================================
Централизованное управление настройками бота.

Features:
- YAML/JSON конфигурация
- Переменные окружения
- Runtime конфигурация
- Валидация настроек
"""

import os
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class BotConfig:
    """Конфигурация бота."""
    # Основные настройки
    check_interval: int = 60  # секунды
    mock_mode: bool = True
    
    # Лимиты
    max_messages_per_cycle: int = 50
    max_whales_per_cycle: int = 10
    rate_limit_per_minute: int = 20
    
    # Психология
    min_weekly_spend: float = 50.0
    enable_psychotype_analysis: bool = True
    
    # Безопасность
    enable_human_simulator: bool = True
    min_response_delay: int = 30  # секунды
    max_response_delay: int = 180  # секунды
    enable_stopword_filter: bool = True
    
    # Telegram
    telegram_enabled: bool = True
    telegram_admin_id: Optional[str] = None
    telegram_token: Optional[str] = None
    
    # База данных
    db_path: str = "data/user_profiles.db"
    enable_analytics: bool = True
    
    # Автономия
    auto_recovery: bool = True
    max_retries: int = 3
    retry_delay: int = 10  # секунды
    
    # Mem0 (если используется)
    mem0_enabled: bool = False
    mem0_api_key: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    path: str = "data/user_profiles.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/bot.log"
    max_size_mb: int = 10
    backup_count: int = 5


class ConfigManager:
    """
    Менеджер конфигурации.
    Загружает и валидирует настройки из файлов и переменных окружения.
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self._bot_config: Optional[BotConfig] = None
        self._db_config: Optional[DatabaseConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._loaded = False
    
    @classmethod
    def get_instance(cls, config_path: str = None) -> 'ConfigManager':
        """Получить экземпляр (Singleton)."""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance
    
    def load(self, force: bool = False) -> bool:
        """
        Загрузить конфигурацию.
        
        Args:
            force: Принудительная перезагрузка
            
        Returns:
            True если загрузка успешна
        """
        if self._loaded and not force:
            return True
        
        # 1. Загружаем из YAML файла
        config_data = self._load_from_yaml()
        
        # 2. Переопределяем из JSON если есть
        config_data = self._merge_with_json(config_data)
        
        # 3. Переопределяем из переменных окружения
        config_data = self._merge_with_env(config_data)
        
        # 4. Создаем датаклассы
        self._bot_config = self._parse_bot_config(config_data.get('bot', {}))
        self._db_config = self._parse_db_config(config_data.get('database', {}))
        self._logging_config = self._parse_logging_config(config_data.get('logging', {}))
        
        self._loaded = True
        return True
    
    def _load_from_yaml(self) -> Dict:
        """Загрузить из YAML файла."""
        config_data = {}
        
        # Ищем YAML файл
        possible_paths = [
            self.config_path,
            "openclaw-enterprise/claw_config.yaml",
            "claw_config.yaml",
            "config.yaml"
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                with open(path, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
                break
        
        return config_data
    
    def _merge_with_json(self, config_data: Dict) -> Dict:
        """Объединить с JSON конфигом."""
        json_paths = [
            "openclaw-enterprise/claw_config.json",
            "claw_config.json",
            "config.json"
        ]
        
        for path in json_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    json_data = json.load(f)
                    config_data = self._deep_merge(config_data, json_data)
                break
        
        return config_data
    
    def _merge_with_env(self, config_data: Dict) -> Dict:
        """Переопределить из переменных окружения."""
        env_mappings = {
            # Bot
            'CHECK_INTERVAL': ('bot', 'check_interval', int),
            'MOCK_MODE': ('bot', 'mock_mode', lambda x: x.lower() == 'true'),
            'MAX_MESSAGES_PER_CYCLE': ('bot', 'max_messages_per_cycle', int),
            'MIN_WEEKLY_SPEND': ('bot', 'min_weekly_spend', float),
            'ENABLE_PSYCHOTYPE': ('bot', 'enable_psychotype_analysis', lambda x: x.lower() == 'true'),
            'MIN_RESPONSE_DELAY': ('bot', 'min_response_delay', int),
            'MAX_RESPONSE_DELAY': ('bot', 'max_response_delay', int),
            
            # Telegram
            'TELEGRAM_TOKEN': ('bot', 'telegram_token', str),
            'TELEGRAM_ADMIN_ID': ('bot', 'telegram_admin_id', str),
            'TELEGRAM_ENABLED': ('bot', 'telegram_enabled', lambda x: x.lower() == 'true'),
            
            # Database
            'DB_PATH': ('database', 'path', str),
            
            # Logging
            'LOG_LEVEL': ('logging', 'level', str),
        }
        
        for env_var, (section, key, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section not in config_data:
                    config_data[section] = {}
                try:
                    config_data[section][key] = converter(value)
                except (ValueError, TypeError):
                    pass  # Игнорируем неверные значения
        
        return config_data
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Глубокое слияние словарей."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _parse_bot_config(self, data: Dict) -> BotConfig:
        """Парсить конфигурацию бота."""
        return BotConfig(
            check_interval=data.get('check_interval', 60),
            mock_mode=data.get('mock_mode', True),
            max_messages_per_cycle=data.get('max_messages_per_cycle', 50),
            max_whales_per_cycle=data.get('max_whales_per_cycle', 10),
            rate_limit_per_minute=data.get('rate_limit_per_minute', 20),
            min_weekly_spend=data.get('min_weekly_spend', 50.0),
            enable_psychotype_analysis=data.get('enable_psychotype_analysis', True),
            enable_human_simulator=data.get('enable_human_simulator', True),
            min_response_delay=data.get('min_response_delay', 30),
            max_response_delay=data.get('max_response_delay', 180),
            enable_stopword_filter=data.get('enable_stopword_filter', True),
            telegram_enabled=data.get('telegram_enabled', True),
            telegram_admin_id=data.get('telegram_admin_id'),
            telegram_token=data.get('telegram_token'),
            db_path=data.get('db_path', 'data/user_profiles.db'),
            enable_analytics=data.get('enable_analytics', True),
            auto_recovery=data.get('auto_recovery', True),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 10),
            mem0_enabled=data.get('mem0_enabled', False),
            mem0_api_key=data.get('mem0_api_key')
        )
    
    def _parse_db_config(self, data: Dict) -> DatabaseConfig:
        """Парсить конфигурацию БД."""
        return DatabaseConfig(
            path=data.get('path', 'data/user_profiles.db'),
            backup_enabled=data.get('backup_enabled', True),
            backup_interval_hours=data.get('backup_interval_hours', 24),
            max_backups=data.get('max_backups', 7)
        )
    
    def _parse_logging_config(self, data: Dict) -> LoggingConfig:
        """Парсить конфигурацию логирования."""
        return LoggingConfig(
            level=data.get('level', 'INFO'),
            format=data.get('format', '%(asctime)s - %(levelname)s - %(message)s'),
            file_enabled=data.get('file_enabled', True),
            file_path=data.get('file_path', 'logs/bot.log'),
            max_size_mb=data.get('max_size_mb', 10),
            backup_count=data.get('backup_count', 5)
        )
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    @property
    def bot(self) -> BotConfig:
        """Получить конфигурацию бота."""
        if self._bot_config is None:
            self.load()
        return self._bot_config
    
    @property
    def database(self) -> DatabaseConfig:
        """Получить конфигурацию БД."""
        if self._db_config is None:
            self.load()
        return self._db_config
    
    @property
    def logging(self) -> LoggingConfig:
        """Получить конфигурацию логирования."""
        if self._logging_config is None:
            self.load()
        return self._logging_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получить значение по ключу.
        
        Args:
            key: Ключ в формате 'section.key' (например, 'bot.check_interval')
            default: Значение по умолчанию
            
        Returns:
            Значение или default
        """
        parts = key.split('.')
        
        if parts[0] == 'bot':
            config = self.bot
        elif parts[0] == 'database':
            config = self.database
        elif parts[0] == 'logging':
            config = self.logging
        else:
            return default
        
        # Рекурсивно ищем значение
        value = config
        for part in parts[1:]:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Установить значение (runtime).
        
        Args:
            key: Ключ в формате 'section.key'
            value: Значение
            
        Returns:
            True если установлено
        """
        parts = key.split('.')
        
        if parts[0] == 'bot':
            config = self.bot
        elif parts[0] == 'database':
            config = self.database
        elif parts[0] == 'logging':
            config = self.logging
        else:
            return False
        
        # Устанавливаем значение
        if len(parts) == 2 and hasattr(config, parts[1]):
            setattr(config, parts[1], value)
            return True
        
        return False
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Валидировать конфигурацию.
        
        Returns:
            Словарь ошибок: {field: [errors]}
        """
        errors = {}
        
        # Проверка бота
        if self.bot.check_interval < 10:
            errors.setdefault('bot.check_interval', []).append(
                'check_interval должен быть >= 10 секунд')
        
        if self.bot.min_response_delay > self.bot.max_response_delay:
            errors.setdefault('bot.response_delay', []).append(
                'min_response_delay должен быть < max_response_delay')
        
        if self.bot.rate_limit_per_minute < 1:
            errors.setdefault('bot.rate_limit_per_minute', []).append(
                'rate_limit_per_minute должен быть >= 1')
        
        # Проверка путей
        if self.bot.mock_mode is False:
            # В production режиме нужны реальные credentials
            if not os.environ.get('LOYALFANS_USERNAME') or not os.environ.get('LOYALFANS_PASSWORD'):
                errors.setdefault('environment', []).append(
                    'В production режиме нужны LOYALFANS_USERNAME и LOYALFANS_PASSWORD')
        
        return errors
    
    def to_dict(self) -> Dict:
        """Экспортировать конфигурацию в словарь."""
        return {
            'bot': self.bot.__dict__,
            'database': self.database.__dict__,
            'logging': self.logging.__dict__
        }
    
    def save(self, path: str = None) -> bool:
        """Сохранить конфигурацию в файл."""
        path = path or self.config_path or "config.yaml"
        
        try:
            with open(path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            return True
        except Exception:
            return False


# Singleton instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Получить экземпляр ConfigManager."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
        _config_instance.load()
    return _config_instance


# ============================================================================
# УТИЛИТЫ ДЛЯ СОЗДАНИЯ КОНФИГУРАЦИИ
# ============================================================================

def create_default_config(path: str = "config.yaml") -> bool:
    """
    Создать файл конфигурации по умолчанию.
    
    Args:
        path: Путь для сохранения
        
    Returns:
        True если успешно
    """
    config = BotConfig()
    
    config_data = {
        'bot': config.__dict__,
        'database': DatabaseConfig().__dict__,
        'logging': LoggingConfig().__dict__
    }
    
    try:
        with open(path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False


def load_config() -> BotConfig:
    """Упрощенная загрузка конфигурации бота."""
    return get_config().bot
