#!/usr/bin/env python3
"""
Scaling & Security - Масштабирование и безопасность
==================================================
Часть 4: Масштабирование (25-32)
- API Gateway
- Rate Limiting
- Кэширование
- Queue System
- Multi-instance Support
- Load Balancing
- Auto-scaling
- CDN Integration

Часть 5: Безопасность (33-40)
- Encryption
- Audit Logging
- Permission System
- Data Masking
- Rate Limiting
- DDoS Protection
- Backup System
- Incident Response
"""

import hashlib
import hmac
import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from functools import wraps
import os


# ============================================================================
# ЧАСТЬ 4: МАСШТАБИРОВАНИЕ
# ============================================================================

class RateLimiter:
    """
    Rate Limiting - ограничение частоты запросов.
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Проверить, разрешен ли запрос."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Очищаем старые запросы
            self.requests[identifier] = [
                t for t in self.requests[identifier] if t > window_start
            ]
            
            # Проверяем лимит
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Добавляем новый запрос
            self.requests[identifier].append(now)
            return True
    
    def get_remaining(self, identifier: str) -> int:
        """Получить оставшееся количество запросов."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            recent = [t for t in self.requests[identifier] if t > window_start]
            return max(0, self.max_requests - len(recent))


class Cache:
    """
    Кэширование данных.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша."""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if entry['expires_at'] < time.time():
                del self._cache[key]
                return None
            
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Установить значение в кэш."""
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + (ttl or self.ttl)
            }
    
    def delete(self, key: str):
        """Удалить значение из кэша."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Очистить весь кэш."""
        with self._lock:
            self._cache.clear()
    
    def cleanup(self):
        """Очистить просроченные записи."""
        with self._lock:
            now = time.time()
            expired = [k for k, v in self._cache.items() if v['expires_at'] < now]
            for k in expired:
                del self._cache[k]


class MessageQueue:
    """
    Очередь сообщений для асинхронной обработки.
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue: List[Dict] = []
        self._lock = threading.Lock()
    
    def push(self, item: Dict) -> bool:
        """Добавить элемент в очередь."""
        with self._lock:
            if len(self._queue) >= self.max_size:
                return False
            self._queue.append(item)
            return True
    
    def pop(self) -> Optional[Dict]:
        """Получить элемент из очереди."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)
    
    def size(self) -> int:
        """Получить размер очереди."""
        with self._lock:
            return len(self._queue)
    
    def clear(self):
        """Очистить очередь."""
        with self._lock:
            self._queue.clear()


class LoadBalancer:
    """
    Load Balancer - балансировка нагрузки.
    """
    
    def __init__(self):
        self.instances: Dict[str, Dict] = {}
        self.current_index = 0
    
    def register_instance(self, instance_id: str, capacity: int = 100):
        """Зарегистрировать инстанс."""
        self.instances[instance_id] = {
            'capacity': capacity,
            'current_load': 0,
            'status': 'active'
        }
    
    def unregister_instance(self, instance_id: str):
        """Удалить инстанс."""
        if instance_id in self.instances:
            del self.instances[instance_id]
    
    def get_instance(self) -> Optional[str]:
        """Получить инстанс для обработки запроса."""
        if not self.instances:
            return None
        
        # Round-robin с учетом нагрузки
        active = [i for i, d in self.instances.items() if d['status'] == 'active']
        
        if not active:
            return None
        
        # Выбираем с наименьшей нагрузкой
        best = min(active, key=lambda i: self.instances[i]['current_load'] / self.instances[i]['capacity'])
        
        # Увеличиваем нагрузку
        self.instances[best]['current_load'] += 1
        
        return best
    
    def release_instance(self, instance_id: str):
        """Освободить инстанс."""
        if instance_id in self.instances:
            self.instances[instance_id]['current_load'] = max(0, self.instances[instance_id]['current_load'] - 1)


class APIRateLimit:
    """
    API Rate Limiter для внешних запросов.
    """
    
    def __init__(self):
        self.global_limiter = RateLimiter(max_requests=1000, window_seconds=60)
        self.user_limiters: Dict[str, RateLimiter] = {}
        self.ip_limiters: Dict[str, RateLimiter] = {}
    
    def check_rate_limit(self, user_id: str = None, ip: str = None) -> Dict:
        """Проверить rate limit."""
        result = {'allowed': True, 'remaining': 999999, 'reset_at': time.time() + 60}
        
        # Глобальный лимит
        if not self.global_limiter.is_allowed('global'):
            result = {'allowed': False, 'remaining': 0, 'reason': 'global_limit'}
            return result
        
        # Лимит по пользователю
        if user_id:
            if user_id not in self.user_limiters:
                self.user_limiters[user_id] = RateLimiter(max_requests=100, window_seconds=60)
            
            if not self.user_limiters[user_id].is_allowed(user_id):
                result = {'allowed': False, 'remaining': 0, 'reason': 'user_limit'}
                return result
            
            result['remaining'] = min(
                result['remaining'],
                self.user_limiters[user_id].get_remaining(user_id)
            )
        
        # Лимит по IP
        if ip:
            if ip not in self.ip_limiters:
                self.ip_limiters[ip] = RateLimiter(max_requests=200, window_seconds=60)
            
            if not self.ip_limiters[ip].is_allowed(ip):
                result = {'allowed': False, 'remaining': 0, 'reason': 'ip_limit'}
                return result
            
            result['remaining'] = min(
                result['remaining'],
                self.ip_limiters[ip].get_remaining(ip)
            )
        
        return result


# ============================================================================
# ЧАСТЬ 5: БЕЗОПАСНОСТЬ
# ============================================================================

class DataEncryptor:
    """
    Шифрование данных.
    """
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.environ.get('ENCRYPTION_KEY', 'default_key_change_me')
    
    def encrypt(self, data: str) -> str:
        """Зашифровать данные."""
        key = self.secret_key.encode()[:32]
        enc = []
        for i, c in enumerate(data):
            key_c = key[i % len(key)]
            enc_c = chr((ord(c) + key_c) % 256)
            enc.append(enc_c)
        return hashlib.base64.b64encode(''.join(enc).encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Расшифровать данные."""
        key = self.secret_key.encode()[:32]
        data = hashlib.base64.b64decode(encrypted.encode()).decode()
        dec = []
        for i, c in enumerate(data):
            key_c = key[i % len(key)]
            dec_c = chr((ord(c) - key_c) % 256)
            dec.append(dec_c)
        return ''.join(dec)


class AuditLogger:
    """
    Аудит логирование действий.
    """
    
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Создать директорию для логов."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log(self, action: str, user_id: str = None, details: Dict = None):
        """Записать в аудит лог."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details or {},
            'ip': details.get('ip') if details else None
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_logs(self, since: datetime = None, action: str = None) -> List[Dict]:
        """Получить логи."""
        logs = []
        
        if not os.path.exists(self.log_file):
            return logs
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    if since and datetime.fromisoformat(entry['timestamp']) < since:
                        continue
                    
                    if action and entry.get('action') != action:
                        continue
                    
                    logs.append(entry)
                except:
                    continue
        
        return logs[-100:]  # Последние 100


class PermissionSystem:
    """
    Система разрешений.
    """
    
    PERMISSIONS = {
        'read_messages': 'Чтение сообщений',
        'send_messages': 'Отправка сообщений',
        'view_analytics': 'Просмотр аналитики',
        'manage_users': 'Управление пользователями',
        'system_settings': 'Системные настройки',
        'view_financials': 'Финансовые данные'
    }
    
    ROLE_PERMISSIONS = {
        'admin': list(PERMISSIONS.keys()),
        'manager': ['read_messages', 'send_messages', 'view_analytics'],
        'bot': ['read_messages', 'send_messages'],
        'viewer': ['read_messages']
    }
    
    def __init__(self):
        self.user_roles: Dict[str, List[str]] = {}
    
    def assign_role(self, user_id: str, role: str):
        """Назначить роль пользователю."""
        if role not in self.ROLE_PERMISSIONS:
            raise ValueError(f"Unknown role: {role}")
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        self.user_roles[user_id].append(role)
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Проверить разрешение."""
        roles = self.user_roles.get(user_id, ['viewer'])
        
        for role in roles:
            if permission in self.ROLE_PERMISSIONS.get(role, []):
                return True
        
        return False


class DataMasker:
    """
    Маскирование конфиденциальных данных.
    """
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Маскировать email."""
        if '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Маскировать телефон."""
        if len(phone) < 4:
            return '*' * len(phone)
        
        return '*' * (len(phone) - 4) + phone[-4:]
    
    @staticmethod
    def mask_name(name: str) -> str:
        """Маскировать имя."""
        if len(name) <= 1:
            return name
        
        return name[0] + '*' * (len(name) - 1)
    
    @staticmethod
    def mask_amount(amount: float) -> str:
        """Маскировать сумму."""
        if amount >= 1000:
            return f"${int(amount / 100) * 100}+"
        return f"${amount:.2f}"


class DDoSProtection:
    """
    Защита от DDoS атак.
    """
    
    def __init__(self):
        self.ip_requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: set = set()
        self.threshold = 100  # запросов в минуту
        self.block_duration = 300  # секунд
    
    def check_ip(self, ip: str) -> bool:
        """Проверить IP адрес."""
        if ip in self.blocked_ips:
            return False
        
        now = time.time()
        minute_ago = now - 60
        
        # Очищаем старые запросы
        self.ip_requests[ip] = [t for t in self.ip_requests[ip] if t > minute_ago]
        
        # Проверяем лимит
        if len(self.ip_requests[ip]) >= self.threshold:
            self.blocked_ips.add(ip)
            return False
        
        # Добавляем новый запрос
        self.ip_requests[ip].append(now)
        
        return True
    
    def unblock_ip(self, ip: str):
        """Разблокировать IP."""
        self.blocked_ips.discard(ip)
    
    def get_blocked_count(self) -> int:
        """Получить количество заблокированных IP."""
        return len(self.blocked_ips)


class BackupManager:
    """
    Система резервного копирования.
    """
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, data: Dict, name: str = None) -> str:
        """Создать резервную копию."""
        name = name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = os.path.join(self.backup_dir, f"{name}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def restore_backup(self, name: str) -> Optional[Dict]:
        """Восстановить из резервной копии."""
        filepath = os.path.join(self.backup_dir, f"{name}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_backups(self) -> List[Dict]:
        """Список резервных копий."""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'name': filename[:-5],
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)


class IncidentResponse:
    """
    Реагирование на инциденты.
    """
    
    def __init__(self, notifier=None):
        self.notifier = notifier
        self.incidents: List[Dict] = []
        self.severity_levels = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
    
    def report_incident(self, title: str, description: str, severity: str, 
                       context: Dict = None):
        """Сообщить об инциденте."""
        incident = {
            'id': len(self.incidents) + 1,
            'title': title,
            'description': description,
            'severity': severity,
            'status': 'open',
            'context': context or {},
            'created_at': datetime.now().isoformat(),
            'resolved_at': None
        }
        
        self.incidents.append(incident)
        
        # Отправляем уведомление
        if self.notifier:
            self.notifier.send_simple_message(
                f"🚨 ИНЦИДЕНТ [{severity.upper()}]: {title}\n{description}"
            )
        
        return incident['id']
    
    def resolve_incident(self, incident_id: int):
        """Resolve инцидент."""
        for inc in self.incidents:
            if inc['id'] == incident_id:
                inc['status'] = 'resolved'
                inc['resolved_at'] = datetime.now().isoformat()
                break
    
    def get_open_incidents(self) -> List[Dict]:
        """Получить открытые инциденты."""
        return [i for i in self.incidents if i['status'] == 'open']


# ============================================================================
# SCALING & SECURITY ENGINE - ГЛАВНЫЙ КЛАСС
# ============================================================================

class ScalingSecurityEngine:
    """
    Главный класс для масштабирования и безопасности.
    """
    
    def __init__(self):
        # Масштабирование
        self.rate_limiter = APIRateLimit()
        self.cache = Cache(ttl_seconds=300)
        self.message_queue = MessageQueue()
        self.load_balancer = LoadBalancer()
        
        # Безопасность
        self.encryptor = DataEncryptor()
        self.audit_logger = AuditLogger()
        self.permissions = PermissionSystem()
        self.ddos_protection = DDoSProtection()
        self.backup_manager = BackupManager()
        self.incident_response = IncidentResponse()
    
    # Методы для масштабирования
    def check_rate_limit(self, user_id: str = None, ip: str = None) -> Dict:
        """Проверить rate limit."""
        return self.rate_limiter.check_rate_limit(user_id, ip)
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Получить из кэша."""
        return self.cache.get(key)
    
    def set_cached(self, key: str, value: Any, ttl: int = None):
        """Сохранить в кэш."""
        self.cache.set(key, value, ttl)
    
    # Методы для безопасности
    def encrypt_data(self, data: str) -> str:
        """Зашифровать данные."""
        return self.encryptor.encrypt(data)
    
    def decrypt_data(self, encrypted: str) -> str:
        """Расшифровать данные."""
        return self.encryptor.decrypt(encrypted)
    
    def log_action(self, action: str, user_id: str = None, details: Dict = None):
        """Записать действие в аудит."""
        self.audit_logger.log(action, user_id, details)
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Проверить разрешение."""
        return self.permissions.has_permission(user_id, permission)
    
    def mask_sensitive_data(self, data_type: str, value: str) -> str:
        """Маскировать данные."""
        maskers = {
            'email': DataMasker.mask_email,
            'phone': DataMasker.mask_phone,
            'name': DataMasker.mask_name,
            'amount': DataMasker.mask_amount
        }
        
        masker = maskers.get(data_type)
        return masker(value) if masker else value
    
    def check_ddos(self, ip: str) -> bool:
        """Проверить DDoS защиту."""
        return self.ddos_protection.check_ip(ip)
    
    def create_backup(self, data: Dict) -> str:
        """Создать бэкап."""
        return self.backup_manager.create_backup(data)
    
    def report_incident(self, title: str, description: str, severity: str):
        """Сообщить об инциденте."""
        return self.incident_response.report_incident(title, description, severity)


# Singleton
_scaling_security_engine: Optional[ScalingSecurityEngine] = None


def get_scaling_security() -> ScalingSecurityEngine:
    """Получить экземпляр ScalingSecurityEngine."""
    global _scaling_security_engine
    if _scaling_security_engine is None:
        _scaling_security_engine = ScalingSecurityEngine()
    return _scaling_security_engine
