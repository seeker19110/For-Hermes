#!/usr/bin/env python3
"""
System Diagnostic - Самодиагностика системы
=========================================
Проверяет все компоненты системы и создает отчет
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_file(filepath: str, description: str) -> bool:
    """Проверка существования файла."""
    exists = os.path.exists(filepath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    print(f"   {status} {description}: {filepath}")
    return exists


def check_directory(dirpath: str, description: str) -> bool:
    """Проверка существования директории."""
    exists = os.path.isdir(dirpath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    print(f"   {status} {description}: {dirpath}")
    return exists


def check_database(db_path: str) -> dict:
    """Проверка базы данных."""
    result = {"exists": False, "tables": 0, "records": 0}
    
    if not os.path.exists(db_path):
        print(f"   {RED}✗{RESET} База данных не найдена: {db_path}")
        return result
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        result["tables"] = len(tables)
        result["exists"] = True
        
        # Подсчитываем записи
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            result["records"] += count
        
        conn.close()
        
        status = f"{GREEN}✓{RESET}"
        print(f"   {status} База данных: {db_path}")
        print(f"      Таблиц: {result['tables']}, Записей: {result['records']}")
        
    except Exception as e:
        print(f"   {RED}✗{RESET} Ошибка БД: {e}")
    
    return result


def run_diagnostics():
    """Запуск полной диагностики."""
    print("\n" + "="*60)
    print("🔍 СИСТЕМНАЯ ДИАГНОСТИКА")
    print("="*60 + "\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_status": "PASS"
    }
    
    # 1. Проверка структуры проекта
    print("📁 Структура проекта:")
    checks = []
    
    checks.append(check_directory("openclaw-enterprise", "Директория проекта"))
    checks.append(check_directory("logs", "Директория логов"))
    checks.append(check_directory("data", "Директория данных"))
    checks.append(check_directory("vault", "Директория контента"))
    checks.append(check_directory("training", "Директория тренингов"))
    
    results["checks"]["structure"] = all(checks)
    
    # 2. Проверка ключевых файлов
    print("\n📄 Ключевые файлы:")
    checks = []
    
    checks.append(check_file("main.py", "Главный файл"))
    checks.append(check_file("vault/price_list.json", "Прайс-лист"))
    checks.append(check_file("training/psychological_triggers.md", "Триггеры"))
    checks.append(check_file("training/trigger_dictionary.md", "Словарь триггеров"))
    checks.append(check_file("logs/transaction_history.json", "История транзакций"))
    checks.append(check_file("logs/whale_profiles.json", "Профили китов"))
    
    results["checks"]["files"] = all(checks)
    
    # 3. Проверка базы данных
    print("\n🗄️ База данных:")
    db_result = check_database("data/user_profiles.db")
    results["checks"]["database"] = db_result["exists"] and db_result["tables"] >= 3
    
    # 4. Проверка Python модулей
    print("\n🐍 Python модули:")
    checks = []
    
    checks.append(check_file("openclaw-enterprise/agents/sales_agent_whale.py", "Sales Agent"))
    checks.append(check_file("openclaw-enterprise/workflows/loyalfans_controller.py", "Controller"))
    checks.append(check_file("openclaw-enterprise/scripts/telegram_notifier.py", "Telegram"))
    checks.append(check_file("openclaw-enterprise/scripts/auth_manager.py", "Auth Manager"))
    
    results["checks"]["modules"] = all(checks)
    
    # 5. Проверка скриптов
    print("\n⚙️ Скрипты:")
    checks = []
    
    checks.append(check_file("scripts/generate_whales.py", "Генератор китов"))
    
    results["checks"]["scripts"] = all(checks)
    
    # Итог
    print("\n" + "="*60)
    all_passed = all(results["checks"].values())
    
    if all_passed:
        print(f"{GREEN}✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ{RESET}")
        results["overall_status"] = "PASS"
    else:
        print(f"{YELLOW}⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ{RESET}")
        results["overall_status"] = "FAIL"
    
    print("="*60 + "\n")
    
    # Детали
    print("📊 Детали проверок:")
    for check, status in results["checks"].items():
        icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"   {icon} {check}")
    
    print()
    
    return results


def create_ready_file(results: dict):
    """Создание файла READY_FOR_PROD.txt."""
    if results["overall_status"] == "PASS":
        content = f"""
╔══════════════════════════════════════════════════════════════╗
║                    READY FOR PRODUCTION                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Status: ✅ READY                                           ║
║  Date: {results['timestamp']}                         ║
║                                                              ║
║  Проверки пройдены:                                         ║
║  - Структура проекта: {'✓' if results['checks'].get('structure') else '✗'}                                  ║
║  - Ключевые файлы: {'✓' if results['checks'].get('files') else '✗'}                                  ║
║  - База данных: {'✓' if results['checks'].get('database') else '✗'}                                     ║
║  - Python модули: {'✓' if results['checks'].get('modules') else '✗'}                                  ║
║  - Скрипты: {'✓' if results['checks'].get('scripts') else '✗'}                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        with open("READY_FOR_PROD.txt", "w") as f:
            f.write(content)
        print(f"{GREEN}✅ Создан файл READY_FOR_PROD.txt{RESET}")
    else:
        print(f"{YELLOW}⚠️  Система не готова к production{RESET}")
        print(f"{YELLOW}   Сначала исправьте ошибки выше{RESET}")


if __name__ == "__main__":
    results = run_diagnostics()
    create_ready_file(results)
