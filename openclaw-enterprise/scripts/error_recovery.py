#!/usr/bin/env python3
"""
Error Recovery - Восстановление после ошибок
============================================
Автоматическое восстановление после сбоев.

Features:
- Отслеживание состояния
- Ретрай логика
- Circuit breaker pattern
- Graceful degradation
"""

import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Уровень серьезности ошибки."""
    LOW = "low"           # Не критично, продолжаем работу
    MEDIUM = "medium"     # Требует внимания
    HIGH = "high"        # Критично, но можно восстановить
    CRITICAL = "critical"  # Требует полной остановки


class RecoveryStrategy(Enum):
    """Стратегия восстановления."""
    RETRY = "retry"                      # Повторить операцию
    SKIP = "skip"                        # Пропустить операцию
    FALLBACK = "fallback"                # Использовать запасной вариант
    ESCALATE = "escalate"                # Эскалировать (уведомить админа)
    STOP = "stop"                        # Остановить бота


@dataclass
class ErrorRecord:
    """Запись об ошибке."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)
    stack_trace: Optional[str] = None
    resolved: bool = False


@dataclass
class CircuitBreakerState:
    """Состояние circuit breaker."""
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    next_attempt: Optional[datetime] = None


class CircuitBreaker:
    """
    Circuit Breaker паттерн.
    Защита от каскадных отказов.
    """
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 half_open_max_calls: int = 3):
        """
        Инициализация.
        
        Args:
            failure_threshold: Количество ошибок для открытия circuit
            recovery_timeout: Время восстановления в секундах
            half_open_max_calls: Максимум вызовов в полуоткрытом состоянии
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = CircuitBreakerState()
        self._half_open_calls = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнить функцию через circuit breaker.
        
        Args:
            func: Функция для выполнения
            *args, **kwargs: Аргументы функции
            
        Returns:
            Результат функции
            
        Raises:
            Exception: Если circuit открыт
        """
        # Проверяем состояние
        if self.state.state == "open":
            if self.state.next_attempt and datetime.now() >= self.state.next_attempt:
                # Переходим в half_open
                self.state.state = "half_open"
                self._half_open_calls = 0
                logger.info("🔄 CircuitBreaker: переход в half_open состояние")
            else:
                raise Exception("CircuitBreaker: circuit открыт, слишком много ошибок")
        
        try:
            result = func(*args, **kwargs)
            
            # Успешный вызов
            if self.state.state == "half_open":
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    # Закрываем circuit
                    self.state.state = "closed"
                    self.state.failures = 0
                    logger.info("✅ CircuitBreaker: circuit закрыт")
            
            return result
            
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_failure(self):
        """Записать ошибку."""
        self.state.failures += 1
        self.state.last_failure_time = datetime.now()
        
        if self.state.failures >= self.failure_threshold:
            self.state.state = "open"
            self.state.next_attempt = datetime.now() + timedelta(seconds=self.recovery_timeout)
            logger.warning(f"⚠️ CircuitBreaker: circuit открыт! failures={self.state.failures}")
    
    def reset(self):
        """Сбросить circuit breaker."""
        self.state = CircuitBreakerState()
        logger.info("🔄 CircuitBreaker: сброшен")


class ErrorRecoveryManager:
    """
    Менеджер восстановления после ошибок.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        """
        Инициализация.
        
        Args:
            max_retries: Максимум попыток
            retry_delay: Задержка между попытками в секундах
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_history: List[ErrorRecord] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Circuit breakers для разных сервисов
        self._init_circuit_breakers()
    
    def _init_circuit_breakers(self):
        """Инициализировать circuit breakers."""
        self.circuit_breakers = {
            'loyalfans': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
            'telegram': CircuitBreaker(failure_threshold=3, recovery_timeout=30),
            'database': CircuitBreaker(failure_threshold=3, recovery_timeout=120),
            'mem0': CircuitBreaker(failure_threshold=3, recovery_timeout=60),
        }
    
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Получить circuit breaker для сервиса."""
        return self.circuit_breakers.get(service)
    
    def record_error(self, error_type: str, message: str, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Dict = None) -> ErrorRecord:
        """
        Записать ошибку.
        
        Args:
            error_type: Тип ошибки
            message: Сообщение
            severity: Серьезность
            context: Контекст
            
        Returns:
            Запись об ошибке
        """
        record = ErrorRecord(
            error_type=error_type,
            error_message=message,
            severity=severity,
            context=context or {},
            stack_trace=traceback.format_exc()
        )
        
        self.error_history.append(record)
        
        # Логируем
        log_method = {
            ErrorSeverity.LOW: logger.info,
            ErrorSeverity.MEDIUM: logger.warning,
            ErrorSeverity.HIGH: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(severity, logger.error)
        
        log_method(f"❌ [{error_type}] {message}")
        
        return record
    
    def get_recovery_strategy(self, error: Exception, context: Dict = None) -> RecoveryStrategy:
        """
        Определить стратегию восстановления.
        
        Args:
            error: Исключение
            context: Контекст ошибки
            
        Returns:
            Стратегия восстановления
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Ошибки сети
        if any(x in error_msg for x in ['timeout', 'connection', 'network', 'ssl']):
            return RecoveryStrategy.RETRY
        
        # Ошибки авторизации
        if any(x in error_msg for x in ['auth', 'login', 'unauthorized', 'forbidden']):
            return RecoveryStrategy.ESCALATE
        
        # Ошибки rate limit
        if 'rate limit' in error_msg or 'too many requests' in error_msg:
            return RecoveryStrategy.RETRY  # С задержкой
        
        # Ошибки БД
        if 'database' in error_type.lower() or 'sqlite' in error_type.lower():
            return RecoveryStrategy.FALLBACK
        
        # Ошибки валидации
        if 'validation' in error_msg or 'invalid' in error_msg:
            return RecoveryStrategy.SKIP
        
        # По умолчанию - retry
        return RecoveryStrategy.RETRY
    
    async def execute_with_retry(self, func: Callable, 
                                  *args,
                                  context: Dict = None,
                                  **kwargs) -> Any:
        """
        Выполнить функцию с ретраем.
        
        Args:
            func: Функция для выполнения
            *args, **kwargs: Аргументы
            context: Контекст для логирования
            
        Returns:
            Результат функции
            
        Raises:
            Exception: Если все попытки исчерпаны
        """
        last_error = None
        context = context or {}
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Выполняем функцию
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"✅ Успех после {attempt} попытки")
                
                return result
                
            except Exception as e:
                last_error = e
                strategy = self.get_recovery_strategy(e, context)
                
                logger.warning(f"⚠️ Попытка {attempt}/{self.max_retries} неудачна: {e}")
                logger.warning(f"   Стратегия восстановления: {strategy.value}")
                
                # Записываем ошибку
                severity = ErrorSeverity.HIGH if attempt == self.max_retries else ErrorSeverity.MEDIUM
                self.record_error(
                    type(e).__name__,
                    str(e),
                    severity,
                    {**context, 'attempt': attempt}
                )
                
                # Обрабатываем стратегию
                if strategy == RecoveryStrategy.SKIP:
                    logger.warning("⏭️ Пропускаем операцию")
                    return None
                
                if strategy == RecoveryStrategy.ESCALATE:
                    logger.critical("🚨 Эскалируем ошибку!")
                    self._send_alert(e, context)
                    raise
                
                if attempt < self.max_retries:
                    # Ждем перед следующей попыткой
                    delay = self.retry_delay * attempt  # Экспоненциальная задержка
                    logger.info(f"   😴 Жду {delay} сек перед следующей попыткой...")
                    await asyncio.sleep(delay)
        
        # Все попытки исчерпаны
        logger.critical(f"❌ Все {self.max_retries} попыток исчерпаны!")
        raise last_error
    
    def _send_alert(self, error: Exception, context: Dict):
        """
        Отправить алерт админу.
        
        Args:
            error: Исключение
            context: Контекст
        """
        # Здесь можно интегрировать с TelegramNotifier
        logger.critical(f"🚨 ALERT: {error}")
        logger.critical(f"   Context: {context}")
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """
        Получить сводку ошибок.
        
        Args:
            hours: За какой период (в часах)
            
        Returns:
            Сводка ошибок
        """
        since = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [e for e in self.error_history if e.timestamp >= since]
        
        # Группируем по типу
        by_type = {}
        by_severity = {s.value: 0 for s in ErrorSeverity}
        
        for error in recent_errors:
            by_type[error.error_type] = by_type.get(error.error_type, 0) + 1
            by_severity[error.severity.value] += 1
        
        return {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'by_type': by_type,
            'by_severity': by_severity,
            'unresolved': len([e for e in recent_errors if not e.resolved])
        }
    
    def clear_old_errors(self, days: int = 7):
        """Очистить старые записи об ошибках."""
        cutoff = datetime.now() - timedelta(days=days)
        self.error_history = [e for e in self.error_history if e.timestamp >= cutoff]
        logger.info(f"🧹 Очищены ошибки старше {days} дней")


# ============================================================================
# ДЕКОРАТОРЫ ДЛЯ АВТОМАТИЧЕСКОГО ВОССТАНОВЛЕНИЯ
# ============================================================================

def with_retry(max_retries: int = 3, retry_delay: int = 5):
    """
    Декоратор для автоматического ретрая.
    
    Usage:
        @with_retry(max_retries=5)
        async def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            manager = ErrorRecoveryManager(max_retries=max_retries, retry_delay=retry_delay)
            return await manager.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


def with_circuit_breaker(service: str, failure_threshold: int = 5):
    """
    Декоратор для circuit breaker.
    
    Usage:
        @with_circuit_breaker('loyalfans')
        async def call_loyalfans():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем circuit breaker из глобального менеджера
            # Это упрощение - в реальном коде нужно получить его иначе
            cb = CircuitBreaker(failure_threshold=failure_threshold)
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ============================================================================

_recovery_manager: Optional[ErrorRecoveryManager] = None


def get_recovery_manager() -> ErrorRecoveryManager:
    """Получить экземпляр ErrorRecoveryManager."""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = ErrorRecoveryManager()
    return _recovery_manager
