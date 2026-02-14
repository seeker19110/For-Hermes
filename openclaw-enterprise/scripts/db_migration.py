#!/usr/bin/env python3
"""
Database Migration - Миграция базы данных
==========================================
Создает дополнительные таблицы для автономного бота.

Tables added:
- sessions: Управление сессиями
- campaigns: Маркетинговые кампании  
- analytics: Аналитика событий
- bot_state: Состояние бота
- error_log: Логи ошибок
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime


def get_db_path() -> str:
    """Получить путь к базе данных."""
    base_dir = Path(__file__).parent.parent.parent
    return str(base_dir / "data" / "user_profiles.db")


def migrate():
    """Выполнить миграцию."""
    db_path = get_db_path()
    
    print("🔄 Миграция базы данных...")
    print(f"   База: {db_path}")
    print()
    
    # Проверяем существование БД
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    created_tables = []
    
    # 1. Таблица sessions
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_platform ON sessions(platform)")
        created_tables.append("sessions")
        print("   ✅ sessions")
    except Exception as e:
        print(f"   ❌ sessions: {e}")
    
    # 2. Таблица campaigns
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                target_audience TEXT,
                budget REAL DEFAULT 0.0,
                spent REAL DEFAULT 0.0,
                metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
        created_tables.append("campaigns")
        print("   ✅ campaigns")
    except Exception as e:
        print(f"   ❌ campaigns: {e}")
    
    # 3. Таблица analytics
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_name TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)")
        created_tables.append("analytics")
        print("   ✅ analytics")
    except Exception as e:
        print(f"   ❌ analytics: {e}")
    
    # 4. Таблица bot_state
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_key TEXT UNIQUE NOT NULL,
                state_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_state_key ON bot_state(state_key)")
        created_tables.append("bot_state")
        print("   ✅ bot_state")
    except Exception as e:
        print(f"   ❌ bot_state: {e}")
    
    # 5. Таблица error_log
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_log_resolved ON error_log(resolved)")
        created_tables.append("error_log")
        print("   ✅ error_log")
    except Exception as e:
        print(f"   ❌ error_log: {e}")
    
    conn.commit()
    conn.close()
    
    print()
    print(f"✅ Миграция завершена! Создано таблиц: {len(created_tables)}")
    print(f"   Таблицы: {', '.join(created_tables)}")
    
    # Показываем все таблицы
    print()
    print("📋 Все таблицы в БД:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for row in cursor.fetchall():
        cursor.execute(f"SELECT COUNT(*) FROM {row[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {row[0]}: {count} записей")
    conn.close()
    
    return True


if __name__ == "__main__":
    migrate()
