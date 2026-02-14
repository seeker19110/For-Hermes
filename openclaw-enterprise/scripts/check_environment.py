#!/usr/bin/env python3
"""
Environment Check - Проверка окружения
======================================
Комплексная проверка готовности системы к работе.

Проверяет:
- Python версия и зависимости
- Файловая структура
- Переменные окружения
- Базу данных
- Права доступа
- Сетевое подключение
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Статус проверки."""
    PASS = "✅ PASS"
    WARN = "⚠️ WARN"
    FAIL = "❌ FAIL"
    INFO = "ℹ️ INFO"


@dataclass
class CheckResult:
    """Результат проверки."""
    name: str
    status: CheckStatus
    message: str
    details: str = ""


class EnvironmentChecker:
    """
    Проверка окружения.
    """
    
    def __init__(self):
        self.results: List[CheckResult] = []
        self.base_dir = Path(__file__).parent.parent.parent
    
    def run_all_checks(self) -> bool:
        """
        Запустить все проверки.
        
        Returns:
            True если все проверки пройдены
        """
        print("=" * 60)
        print("🔍 ПРОВЕРКА ОКРУЖЕНИЯ")
        print("=" * 60)
        print()
        
        # 1. Python версия
        self.check_python_version()
        
        # 2. Зависимости
        self.check_dependencies()
        
        # 3. Файловая структура
        self.check_file_structure()
        
        # 4. Переменные окружения
        self.check_environment_variables()
        
        # 5. База данных
        self.check_database()
        
        # 6. Конфигурационные файлы
        self.check_config_files()
        
        # 7. Права доступа
        self.check_permissions()
        
        # Вывод результатов
        self.print_results()
        
        # Итог
        return self.get_summary()
    
    def check_python_version(self):
        """Проверить версию Python."""
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 10:
            self.add_result(CheckStatus.PASS, "Python version", 
                          f"Python {version.major}.{version.minor}.{version.micro}")
        elif version.major >= 3 and version.minor >= 8:
            self.add_result(CheckStatus.WARN, "Python version",
                          f"Python {version.major}.{version.minor}.{version.micro} (рекомендуется 3.10+)")
        else:
            self.add_result(CheckStatus.FAIL, "Python version",
                          f"Python {version.major}.{version.minor} не поддерживается (нужен 3.8+)")
    
    def check_dependencies(self):
        """Проверить установленные зависимости."""
        required = {
            'asyncio': 'asyncio',
            'sqlite3': 'sqlite3',
            'json': 'json',
            'datetime': 'datetime',
            'pathlib': 'pathlib',
        }
        
        optional = {
            'yaml': 'PyYAML',
            'aiohttp': 'aiohttp',
            'requests': 'requests',
            'telebot': 'pyTelegramBotAPI',
        }
        
        # Проверяем обязательные
        for name, module in required.items():
            try:
                __import__(name)
                self.add_result(CheckStatus.PASS, f"Dependency: {module}", "Установлен")
            except ImportError:
                self.add_result(CheckStatus.FAIL, f"Dependency: {module}", "Не найден")
        
        # Проверяем опциональные
        for name, module in optional.items():
            try:
                __import__(name)
                self.add_result(CheckStatus.PASS, f"Optional: {module}", "Установлен")
            except ImportError:
                self.add_result(CheckStatus.INFO, f"Optional: {module}", "Не установлен (опционально)")
    
    def check_file_structure(self):
        """Проверить файловую структуру."""
        required_paths = [
            "main.py",
            "openclaw-enterprise/agents/sales_agent_whale.py",
            "openclaw-enterprise/scripts/telegram_notifier.py",
            "openclaw-enterprise/scripts/auth_manager.py",
            "data/",
            "logs/",
            "vault/",
        ]
        
        for path in required_paths:
            full_path = self.base_dir / path
            if full_path.exists():
                self.add_result(CheckStatus.PASS, f"Path: {path}", "Существует")
            else:
                self.add_result(CheckStatus.FAIL, f"Path: {path}", "Не найден")
    
    def check_environment_variables(self):
        """Проверить переменные окружения."""
        required_vars = [
            'LOYALFANS_USERNAME',
            'LOYALFANS_PASSWORD',
        ]
        
        optional_vars = [
            'TELEGRAM_TOKEN',
            'TELEGRAM_ADMIN_ID',
            'MOCK_MODE',
            'CHECK_INTERVAL',
        ]
        
        # Проверяем обязательные
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                # Скрываем пароль
                display = f"{var}=***" if 'PASSWORD' in var else f"{var}={value}"
                self.add_result(CheckStatus.PASS, f"ENV: {var}", "Установлена")
            else:
                self.add_result(CheckStatus.WARN, f"ENV: {var}", "Не установлена (или MOCK_MODE=True)")
        
        # Проверяем опциональные
        for var in optional_vars:
            value = os.environ.get(var)
            if value:
                self.add_result(CheckStatus.PASS, f"ENV: {var}", f"Установлена: {value}")
            else:
                self.add_result(CheckStatus.INFO, f"ENV: {var}", "Не установлена (опционально)")
    
    def check_database(self):
        """Проверить базу данных."""
        db_path = self.base_dir / "data" / "user_profiles.db"
        
        if not db_path.exists():
            self.add_result(CheckStatus.WARN, "Database", "База данных не существует, будет создана")
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Проверяем таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['user_profiles', 'transactions', 'conversation_history']
            for table in required_tables:
                if table in tables:
                    # Получаем количество записей
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    self.add_result(CheckStatus.PASS, f"Table: {table}", f"{count} записей")
                else:
                    self.add_result(CheckStatus.FAIL, f"Table: {table}", "Отсутствует")
            
            conn.close()
            
        except Exception as e:
            self.add_result(CheckStatus.FAIL, "Database", f"Ошибка: {e}")
    
    def check_config_files(self):
        """Проверить конфигурационные файлы."""
        config_files = [
            "openclaw-enterprise/claw_config.yaml",
            "openclaw-enterprise/.env.example",
            ".env",
        ]
        
        for path in config_files:
            full_path = self.base_dir / path
            if full_path.exists():
                size = full_path.stat().st_size
                self.add_result(CheckStatus.PASS, f"Config: {path}", f"{size} байт")
            else:
                self.add_result(CheckStatus.INFO, f"Config: {path}", "Не найден (опционально)")
    
    def check_permissions(self):
        """Проверить права доступа."""
        # Проверяем возможность записи
        dirs_to_check = ['data', 'logs', 'vault']
        
        for dir_name in dirs_to_check:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                test_file = dir_path / ".write_test"
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    self.add_result(CheckStatus.PASS, f"Permissions: {dir_name}", "Запись разрешена")
                except Exception as e:
                    self.add_result(CheckStatus.FAIL, f"Permissions: {dir_name}", f"Запрещена: {e}")
            else:
                # Пробуем создать
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.add_result(CheckStatus.PASS, f"Permissions: {dir_name}", "Создана директория")
                except Exception as e:
                    self.add_result(CheckStatus.FAIL, f"Permissions: {dir_name}", f"Не могу создать: {e}")
    
    def add_result(self, status: CheckStatus, name: str, message: str):
        """Добавить результат проверки."""
        self.results.append(CheckResult(name, status, message))
    
    def print_results(self):
        """Вывести результаты."""
        for result in self.results:
            status_symbol = {
                CheckStatus.PASS: "✅",
                CheckStatus.WARN: "⚠️",
                CheckStatus.FAIL: "❌",
                CheckStatus.INFO: "ℹ️"
            }.get(result.status, "?")
            
            print(f"{status_symbol} {result.name}")
            print(f"   {result.message}")
            print()
    
    def get_summary(self) -> bool:
        """Получить итоговую статистику."""
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASS)
        warnings = sum(1 for r in self.results if r.status == CheckStatus.WARN)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAIL)
        
        print("=" * 60)
        print("📊 ИТОГИ:")
        print(f"   ✅ Проверок пройдено: {passed}")
        print(f"   ⚠️  Предупреждений: {warnings}")
        print(f"   ❌ Ошибок: {failed}")
        print("=" * 60)
        
        if failed > 0:
            print("\n❌ СИСТЕМА НЕ ГОТОВА К РАБОТЕ!")
            print("   Исправьте ошибки перед запуском.")
            return False
        elif warnings > 0:
            print("\n⚠️  СИСТЕМА РАБОТОСПОСОБНА С ПРЕДУПРЕЖДЕНИЯМИ")
            return True
        else:
            print("\n✅ СИСТЕМА ПОЛНОСТЬЮ ГОТОВА!")
            return True


def main():
    """Точка входа."""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
