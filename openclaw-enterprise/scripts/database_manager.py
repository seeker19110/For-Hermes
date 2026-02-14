#!/usr/bin/env python3
"""
Database Manager - Расширенная база данных для автономного бота
=================================================================
Добавляет: sessions, campaigns, analytics, bot_state

Tables:
- sessions: Персистентность сессий
- campaigns: Маркетинговые кампании
- analytics: Аналитика и метрики
- bot_state: Состояние бота для восстановления
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path


class DatabaseManager:
    """
    Менеджер расширенной базы данных.
    Обеспечивает персистентность всех данных бота.
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data/user_profiles.db
            base_dir = Path(__file__).parent.parent.parent
            db_path = base_dir / "data" / "user_profiles.db"
        
        self.db_path = str(db_path)
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self):
        """Создать все необходимые таблицы."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица сессий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Таблица кампаний
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
        
        # Таблица аналитики
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
        
        # Таблица состояния бота
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_key TEXT UNIQUE NOT NULL,
                state_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        # Таблица ошибок
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
        
        # Индексы для производительности
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
        
        conn.commit()
        conn.close()
    
    # =========================================================================
    # SESSIONS - Управление сессиями
    # =========================================================================
    
    def create_session(self, session_id: str, platform: str, metadata: Dict = None) -> bool:
        """Создать новую сессию."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sessions (session_id, platform, metadata)
                VALUES (?, ?, ?)
            """, (session_id, platform, json.dumps(metadata or {})))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_session_activity(self, session_id: str) -> bool:
        """Обновить время последней активности сессии."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE sessions 
                SET last_active = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def end_session(self, session_id: str) -> bool:
        """Завершить сессию."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE sessions 
                SET status = 'ended', ended_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_active_session(self, platform: str = None) -> Optional[Dict]:
        """Получить активную сессию."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if platform:
                cursor.execute("""
                    SELECT * FROM sessions 
                    WHERE status = 'active' AND platform = ?
                    ORDER BY last_active DESC LIMIT 1
                """, (platform,))
            else:
                cursor.execute("""
                    SELECT * FROM sessions 
                    WHERE status = 'active' 
                    ORDER BY last_active DESC LIMIT 1
                """)
            
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    # =========================================================================
    # CAMPAIGNS - Управление кампаниями
    # =========================================================================
    
    def create_campaign(self, campaign_id: str, name: str, 
                       description: str = None, budget: float = 0.0) -> bool:
        """Создать новую кампанию."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO campaigns (campaign_id, name, description, budget)
                VALUES (?, ?, ?, ?)
            """, (campaign_id, name, description, budget))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_campaign_metrics(self, campaign_id: str, metrics: Dict) -> bool:
        """Обновить метрики кампании."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE campaigns 
                SET metrics = ?
                WHERE campaign_id = ?
            """, (json.dumps(metrics), campaign_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        """Получить кампанию по ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM campaigns WHERE campaign_id = ?
            """, (campaign_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_active_campaigns(self) -> List[Dict]:
        """Получить все активные кампании."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM campaigns WHERE status = 'active'
                ORDER BY started_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # =========================================================================
    # ANALYTICS - Аналитика и события
    # =========================================================================
    
    def log_event(self, event_type: str, event_name: str,
                  user_id: str = None, session_id: str = None,
                  metadata: Dict = None) -> bool:
        """Записать событие в аналитику."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO analytics (event_type, event_name, user_id, session_id, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (event_type, event_name, user_id, session_id, json.dumps(metadata or {})))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_events(self, event_type: str = None, 
                   since: datetime = None, limit: int = 100) -> List[Dict]:
        """Получить события из аналитики."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM analytics WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_analytics_summary(self, days: int = 7) -> Dict:
        """Получить сводку аналитики за период."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Всего событий
            cursor.execute("""
                SELECT event_type, COUNT(*) as count 
                FROM analytics 
                WHERE timestamp >= ?
                GROUP BY event_type
            """, (since,))
            events_by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Уникальные пользователи
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) 
                FROM analytics 
                WHERE timestamp >= ? AND user_id IS NOT NULL
            """, (since,))
            unique_users = cursor.fetchone()[0] or 0
            
            # Всего сессий
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sessions 
                WHERE started_at >= ?
            """, (since,))
            total_sessions = cursor.fetchone()[0] or 0
            
            return {
                "period_days": days,
                "events_by_type": events_by_type,
                "unique_users": unique_users,
                "total_sessions": total_sessions,
                "total_events": sum(events_by_type.values())
            }
        finally:
            conn.close()
    
    # =========================================================================
    # BOT STATE - Состояние бота
    # =========================================================================
    
    def set_state(self, key: str, value: Any, ttl_seconds: int = None) -> bool:
        """Установить состояние бота."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            expires_at = None
            if ttl_seconds:
                expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
            
            cursor.execute("""
                INSERT INTO bot_state (state_key, state_value, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(state_key) DO UPDATE SET
                    state_value = excluded.state_value,
                    updated_at = CURRENT_TIMESTAMP,
                    expires_at = excluded.expires_at
            """, (key, json.dumps(value), expires_at))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_state(self, key: str) -> Optional[Any]:
        """Получить состояние бота."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT state_value, expires_at FROM bot_state 
                WHERE state_key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Проверка на истечение срока
            if row[1]:  # expires_at
                expires = datetime.fromisoformat(row[1])
                if expires < datetime.now():
                    return None
            
            return json.loads(row[0])
        finally:
            conn.close()
    
    def delete_state(self, key: str) -> bool:
        """Удалить состояние бота."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM bot_state WHERE state_key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # =========================================================================
    # ERROR LOG - Логирование ошибок
    # =========================================================================
    
    def log_error(self, error_type: str, error_message: str,
                  stack_trace: str = None, context: Dict = None) -> int:
        """Записать ошибку в лог."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO error_log (error_type, error_message, stack_trace, context)
                VALUES (?, ?, ?, ?)
            """, (error_type, error_message, stack_trace, json.dumps(context or {})))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def resolve_error(self, error_id: int) -> bool:
        """Отметить ошибку как решенную."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE error_log 
                SET resolved = 1, resolved_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (error_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_unresolved_errors(self) -> List[Dict]:
        """Получить нерешенные ошибки."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM error_log 
                WHERE resolved = 0 
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()


# Singleton instance
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Получить экземпляр базы данных."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# ============================================================================
# УТИЛИТЫ ДЛЯ СОХРАНЕНИЯ СОСТОЯНИЯ
# ============================================================================

def save_bot_state(state_type: str, data: Dict) -> bool:
    """
    Сохранить состояние бота.
    Используется для восстановления после сбоев.
    """
    db = get_database()
    return db.set_state(f"bot_state_{state_type}", data, ttl_seconds=86400 * 7)


def load_bot_state(state_type: str) -> Optional[Dict]:
    """
    Загрузить состояние бота.
    Используется для восстановления после сбоев.
    """
    db = get_database()
    return db.get_state(f"bot_state_{state_type}")


def save_cycle_state(cycle_number: int, processed_messages: List[str]) -> bool:
    """Сохранить состояние цикла для восстановления."""
    return save_bot_state("cycle", {
        "cycle_number": cycle_number,
        "processed_messages": processed_messages,
        "timestamp": datetime.now().isoformat()
    })


def load_cycle_state() -> Optional[Dict]:
    """Загрузить состояние последнего цикла."""
    return load_bot_state("cycle")
