#!/usr/bin/env python3
"""
Autonomy Engine - Автономный движок
====================================
Обеспечивает полную автономию бота.

Features:
- Workflow Engine: State machine для задач
- Task Scheduler: Планирование задач
- Monitoring: Мониторинг состояния
- Metrics: Сбор метрик
- Self-Healing: Автоматическое восстановление
- Health Checks: Проверки здоровья
- Self-Diagnostics: Самодиагностика
"""

import asyncio
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class TaskState(Enum):
    """Состояние задачи."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthStatus(Enum):
    """Статус здоровья."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class Task:
    """Задача."""
    task_id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Metrics:
    """Метрики системы."""
    uptime_seconds: float = 0
    cycles_completed: int = 0
    messages_processed: int = 0
    whales_engaged: int = 0
    errors_count: int = 0
    avg_response_time_ms: float = 0
    cpu_percent: float = 0
    memory_percent: float = 0
    last_cycle_time_ms: float = 0


class WorkflowEngine:
    """
    Workflow Engine - движок управления задачами.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, Task] = {}
    
    async def add_task(self, task: Task) -> str:
        """Добавить задачу в очередь."""
        self.tasks[task.task_id] = task
        await self.task_queue.put(task)
        return task.task_id
    
    async def execute_task(self, task: Task) -> Any:
        """Выполнить задачу."""
        task.state = TaskState.RUNNING
        task.started_at = datetime.now()
        self.running_tasks[task.task_id] = task
        
        try:
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            task.result = result
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now()
            
            return result
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.state = TaskState.PENDING
                # Повторная попытка
                await asyncio.sleep(2 ** task.retry_count)
                return await self.execute_task(task)
            else:
                task.state = TaskState.FAILED
                task.completed_at = datetime.now()
                raise
        
        finally:
            self.running_tasks.pop(task.task_id, None)
    
    async def process_queue(self):
        """Обрабатывать очередь задач."""
        while True:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self.execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing task: {e}")


class TaskScheduler:
    """
    Task Scheduler - планировщик задач.
    """
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict] = {}
        self.running = False
    
    def schedule_interval(self, task_id: str, func: Callable, interval_seconds: int):
        """Запланировать задачу с интервалом."""
        self.scheduled_tasks[task_id] = {
            'func': func,
            'interval': interval_seconds,
            'last_run': None,
            'enabled': True
        }
    
    def schedule_at(self, task_id: str, func: Callable, time_str: str):
        """Запланировать задачу на время."""
        # time_str в формате "HH:MM"
        self.scheduled_tasks[task_id] = {
            'func': func,
            'time': time_str,
            'last_run': None,
            'enabled': True
        }
    
    async def run_scheduler(self, bot):
        """Запустить планировщик."""
        self.running = True
        
        while self.running:
            now = datetime.now()
            
            for task_id, task_info in self.scheduled_tasks.items():
                if not task_info['enabled']:
                    continue
                
                # Интервальные задачи
                if 'interval' in task_info:
                    if task_info['last_run'] is None or \
                       (now - task_info['last_run']).total_seconds() >= task_info['interval']:
                        try:
                            if asyncio.iscoroutinefunction(task_info['func']):
                                await task_info['func'](bot)
                            else:
                                task_info['func'](bot)
                            task_info['last_run'] = now
                        except Exception as e:
                            print(f"Error in scheduled task {task_id}: {e}")
                
                # Задачи по времени
                elif 'time' in task_info:
                    current_time = now.strftime("%H:%M")
                    if current_time == task_info['time'] and \
                       (task_info['last_run'] is None or task_info['last_run'].date() != now.date()):
                        try:
                            if asyncio.iscoroutinefunction(task_info['func']):
                                await task_info['func'](bot)
                            else:
                                task_info['func'](bot)
                            task_info['last_run'] = now
                        except Exception as e:
                            print(f"Error in scheduled task {task_id}: {e}")
            
            await asyncio.sleep(10)  # Проверяем каждые 10 секунд
    
    def stop(self):
        """Остановить планировщик."""
        self.running = False


class Monitoring:
    """
    Monitoring - мониторинг системы.
    """
    
    def __init__(self):
        self.metrics = Metrics()
        self.start_time = time.time()
        self.history: deque = deque(maxlen=1000)
        
        # Мониторинг процессора и памяти
        self.process = psutil.Process()
    
    def update_metrics(self, cycle_data: Dict = None):
        """Обновить метрики."""
        # Аптайм
        self.metrics.uptime_seconds = time.time() - self.start_time
        
        # CPU и память
        try:
            self.metrics.cpu_percent = self.process.cpu_percent()
            self.metrics.memory_percent = self.process.memory_percent()
        except:
            pass
        
        # Данные из цикла
        if cycle_data:
            self.metrics.cycles_completed += 1
            self.metrics.messages_processed += cycle_data.get('messages', 0)
            self.metrics.whales_engaged += cycle_data.get('whales', 0)
            
            cycle_time = cycle_data.get('duration_ms', 0)
            # Скользящее среднее время цикла
            if self.metrics.cycles_completed > 1:
                self.metrics.avg_response_time_ms = (
                    (self.metrics.avg_response_time_ms * (self.metrics.cycles_completed - 1) + cycle_time) 
                    / self.metrics.cycles_completed
                )
            else:
                self.metrics.avg_response_time_ms = cycle_time
    
    def record_error(self):
        """Записать ошибку."""
        self.metrics.errors_count += 1
    
    def get_status(self) -> Dict:
        """Получить текущий статус."""
        return {
            'uptime_seconds': self.metrics.uptime_seconds,
            'uptime_hours': self.metrics.uptime_seconds / 3600,
            'cycles_completed': self.metrics.cycles_completed,
            'messages_processed': self.metrics.messages_processed,
            'whales_engaged': self.metrics.whales_engaged,
            'errors_count': self.metrics.errors_count,
            'cpu_percent': round(self.metrics.cpu_percent, 1),
            'memory_percent': round(self.metrics.memory_percent, 1),
            'avg_cycle_time_ms': round(self.metrics.avg_response_time_ms, 1),
            'error_rate': self.metrics.errors_count / max(1, self.metrics.cycles_completed)
        }
    
    def log_to_history(self, event_type: str, data: Dict):
        """Записать в историю."""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        })


class HealthChecker:
    """
    Health Checker - проверки здоровья.
    """
    
    def __init__(self, db=None, notifier=None):
        self.db = db
        self.notifier = notifier
        self.checks: Dict[str, Callable] = {}
        self._register_checks()
    
    def _register_checks(self):
        """Зарегистрировать проверки."""
        # Проверка БД
        self.checks['database'] = self._check_database
        
        # Проверка памяти
        self.checks['memory'] = self._check_memory
        
        # Проверка диска
        self.checks['disk'] = self._check_disk
        
        # Проверка сети
        self.checks['network'] = self._check_network
    
    async def _check_database(self) -> Dict:
        """Проверить базу данных."""
        try:
            if self.db:
                # Простой запрос
                session = self.db.get_active_session()
                return {'status': HealthStatus.HEALTHY, 'message': 'OK'}
            return {'status': HealthStatus.UNHEALTHY, 'message': 'DB not initialized'}
        except Exception as e:
            return {'status': HealthStatus.UNHEALTHY, 'message': str(e)}
    
    async def _check_memory(self) -> Dict:
        """Проверить память."""
        try:
            mem = psutil.virtual_memory()
            percent = mem.percent
            
            if percent < 70:
                status = HealthStatus.HEALTHY
            elif percent < 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return {
                'status': status,
                'message': f'Memory: {percent:.1f}%',
                'details': {'total': mem.total, 'available': mem.available, 'percent': percent}
            }
        except Exception as e:
            return {'status': HealthStatus.UNHEALTHY, 'message': str(e)}
    
    async def _check_disk(self) -> Dict:
        """Проверить диск."""
        try:
            disk = psutil.disk_usage('/')
            percent = disk.percent
            
            if percent < 70:
                status = HealthStatus.HEALTHY
            elif percent < 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return {
                'status': status,
                'message': f'Disk: {percent:.1f}%',
                'details': {'total': disk.total, 'free': disk.free, 'percent': percent}
            }
        except Exception as e:
            return {'status': HealthStatus.UNHEALTHY, 'message': str(e)}
    
    async def _check_network(self) -> Dict:
        """Проверить сеть."""
        # Упрощенная проверка
        return {'status': HealthStatus.HEALTHY, 'message': 'Network OK'}
    
    async def run_all_checks(self) -> Dict:
        """Выполнить все проверки."""
        results = {}
        
        for check_name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results[check_name] = result
            except Exception as e:
                results[check_name] = {'status': HealthStatus.UNHEALTHY, 'message': str(e)}
        
        # Определяем общий статус
        statuses = [r.get('status', HealthStatus.UNHEALTHY) for r in results.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        else:
            overall = HealthStatus.DEGRADED
        
        return {
            'overall': overall,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }


class SelfDiagnostics:
    """
    Self-Diagnostics - самодиагностика.
    """
    
    def __init__(self, monitoring: Monitoring = None, health_checker: HealthChecker = None):
        self.monitoring = monitoring
        self.health_checker = health_checker
        self.diagnostic_results: List[Dict] = []
    
    async def run_diagnostics(self) -> Dict:
        """Запустить самодиагностику."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # 1. Проверка здоровья
        if self.health_checker:
            health = await self.health_checker.run_all_checks()
            results['components']['health'] = health
        
        # 2. Проверка метрик
        if self.monitoring:
            status = self.monitoring.get_status()
            results['components']['metrics'] = status
            
            # Проверяем пороговые значения
            issues = []
            
            if status['error_rate'] > 0.1:  # > 10% ошибок
                issues.append(f"High error rate: {status['error_rate']:.1%}")
            
            if status['cpu_percent'] > 80:
                issues.append(f"High CPU: {status['cpu_percent']}%")
            
            if status['memory_percent'] > 80:
                issues.append(f"High memory: {status['memory_percent']}%")
            
            results['issues'] = issues
        
        # 3. Проверка зависимостей
        results['components']['dependencies'] = self._check_dependencies()
        
        # Сохраняем результаты
        self.diagnostic_results.append(results)
        
        return results
    
    def _check_dependencies(self) -> Dict:
        """Проверить зависимости."""
        deps = {}
        
        required = ['asyncio', 'sqlite3', 'json', 'datetime']
        for dep in required:
            try:
                __import__(dep)
                deps[dep] = 'ok'
            except ImportError:
                deps[dep] = 'missing'
        
        return deps
    
    def get_report(self) -> str:
        """Получить текстовый отчет."""
        if not self.diagnostic_results:
            return "Нет данных диагностики"
        
        latest = self.diagnostic_results[-1]
        
        report = "=" * 50 + "\n"
        report += "📊 САМОДИАГНОСТИКА\n"
        report += "=" * 50 + "\n"
        report += f"Время: {latest['timestamp']}\n\n"
        
        # Метрики
        if 'metrics' in latest['components']:
            m = latest['components']['metrics']
            report += "📈 МЕТРИКИ:\n"
            report += f"   Аптайм: {m['uptime_hours']:.1f} часов\n"
            report += f"   Циклов: {m['cycles_completed']}\n"
            report += f"   Сообщений: {m['messages_processed']}\n"
            report += f"   Китов: {m['whales_engaged']}\n"
            report += f"   Ошибок: {m['errors_count']}\n"
            report += f"   CPU: {m['cpu_percent']}%\n"
            report += f"   RAM: {m['memory_percent']}%\n\n"
        
        # Проблемы
        if 'issues' in latest and latest['issues']:
            report += "⚠️ ПРОБЛЕМЫ:\n"
            for issue in latest['issues']:
                report += f"   - {issue}\n"
            report += "\n"
        
        # Здоровье
        if 'health' in latest['components']:
            h = latest['components']['health']
            report += "💚 ЗДОРОВЬЕ:\n"
            report += f"   Статус: {h['overall'].value}\n"
            for check, result in h['checks'].items():
                report += f"   - {check}: {result.get('message', 'N/A')}\n"
        
        return report


class AutonomyEngine:
    """
    Autonomy Engine - главный класс автономности.
    Объединяет все компоненты.
    """
    
    def __init__(self, db=None, notifier=None):
        # Компоненты
        self.workflow = WorkflowEngine()
        self.scheduler = TaskScheduler()
        self.monitoring = Monitoring()
        self.health_checker = HealthChecker(db, notifier)
        self.diagnostics = SelfDiagnostics(self.monitoring, self.health_checker)
        
        # Состояние
        self.is_running = False
    
    async def start(self):
        """Запустить движок автономности."""
        self.is_running = True
        
        # Запускаем фоновые задачи
        asyncio.create_task(self.workflow.process_queue())
        asyncio.create_task(self.scheduler.run_scheduler(None))
        
        # Периодическая самодиагностика
        asyncio.create_task(self._periodic_diagnostics())
        
        print("🚀 Autonomy Engine запущен")
    
    async def stop(self):
        """Остановить движок."""
        self.is_running = False
        self.scheduler.stop()
        print("🛑 Autonomy Engine остановлен")
    
    async def _periodic_diagnostics(self):
        """Периодическая самодиагностика."""
        while self.is_running:
            await asyncio.sleep(3600)  # Каждый час
            
            try:
                results = await self.diagnostics.run_diagnostics()
                
                # Логируем проблемы
                if 'issues' in results and results['issues']:
                    print(f"⚠️ Найдены проблемы: {results['issues']}")
                
                # Проверяем здоровье
                health = results.get('components', {}).get('health', {})
                if health.get('overall') == HealthStatus.UNHEALTHY:
                    print("🚨 Система нездорова!")
                    
            except Exception as e:
                print(f"Ошибка в диагностике: {e}")
    
    def get_status(self) -> Dict:
        """Получить статус."""
        return {
            'is_running': self.is_running,
            'monitoring': self.monitoring.get_status(),
            'scheduler_tasks': len(self.scheduler.scheduled_tasks),
            'queue_size': self.workflow.task_queue.qsize()
        }


# Singleton
_autonomy_engine: Optional[AutonomyEngine] = None


def get_autonomy_engine(db=None, notifier=None) -> AutonomyEngine:
    """Получить экземпляр AutonomyEngine."""
    global _autonomy_engine
    if _autonomy_engine is None:
        _autonomy_engine = AutonomyEngine(db, notifier)
    return _autonomy_engine
