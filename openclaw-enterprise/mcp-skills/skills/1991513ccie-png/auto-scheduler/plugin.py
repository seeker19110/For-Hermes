#!/usr/bin/env python3
"""
Auto Scheduler Plugin
自动化任务调度器
"""

import os
import sys
import json
import argparse
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import uuid
from threading import Thread
import queue
import signal


class Task:
    """Task class for scheduled tasks"""
    
    def __init__(self, 
                 task_id: str = None,
                 name: str = None,
                 schedule: Dict = None,
                 command: str = None,
                 enabled: bool = True,
                 created_at: str = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name
        self.schedule = schedule or {"type": "once", "at": datetime.now().isoformat()}
        self.command = command
        self.enabled = enabled
        self.created_at = created_at or datetime.now().isoformat()
        self.status = "pending"
        self.last_run = None
        self.next_run = None
        self.retry_count = 0
        self.max_retries = 3
        self.results = []
        
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'name': self.name,
            'schedule': self.schedule,
            'command': self.command,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'status': self.status,
            'last_run': self.last_run,
            'next_run': self.next_run,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'results': self.results
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            task_id=data.get('task_id'),
            name=data.get('name'),
            schedule=data.get('schedule'),
            command=data.get('command'),
            enabled=data.get('enabled', True),
            created_at=data.get('created_at')
        )
        task.status = data.get('status', 'pending')
        task.last_run = data.get('last_run')
        task.next_run = data.get('next_run')
        task.retry_count = data.get('retry_count', 0)
        task.max_retries = data.get('max_retries', 3)
        task.results = data.get('results', [])
        return task


class JobScheduler:
    """Auto Scheduler - 自动化任务调度器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.Queue()
        self.running = False
        self._load_tasks()
        
    def _default_config(self) -> Dict:
        return {
            'data_dir': '~/.clawhub/scheduler',
            'max_retries': 3,
            'retry_delay': 60,
            'default_schedule': {'type': 'once'},
            'log_level': 'INFO',
            'timezone': 'Asia/Shanghai'
        }
    
    def _load_tasks(self):
        """Load tasks from storage"""
        data_dir = Path(self.config['data_dir']).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        
        tasks_file = data_dir / 'tasks.json'
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                data = json.load(f)
                for task_id, task_data in data.items():
                    self.tasks[task_id] = Task.from_dict(task_data)
    
    def _save_tasks(self):
        """Save tasks to storage"""
        data_dir = Path(self.config['data_dir']).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        
        tasks_file = data_dir / 'tasks.json'
        data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        with open(tasks_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_task(self,
                    name: str = None,
                    command: str = None,
                    schedule: Dict = None,
                    enabled: bool = True) -> Task:
        """Create a new task"""
        task = Task(
            name=name,
            command=command,
            schedule=schedule or self.config['default_schedule'],
            enabled=enabled
        )
        self.tasks[task.task_id] = task
        self._save_tasks()
        return task
    
    def update_task(self, task_id: str, **kwargs) -> Task:
        """Update an existing task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self._save_tasks()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, enabled: bool = None, status: str = None) -> List[Task]:
        """List tasks with optional filters"""
        tasks = list(self.tasks.values())
        if enabled is not None:
            tasks = [t for t in tasks if t.enabled == enabled]
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks
    
    def enable_task(self, task_id: str) -> Task:
        """Enable a task"""
        return self.update_task(task_id, enabled=True)
    
    def disable_task(self, task_id: str) -> Task:
        """Disable a task"""
        return self.update_task(task_id, enabled=False)
    
    def run_task(self, task_id: str, blocking: bool = False) -> Dict:
        """Run a task immediately"""
        task = self.get_task(task_id)
        if not task:
            return {'error': f"Task {task_id} not found"}
        
        if not task.enabled:
            return {'error': f"Task {task_id} is disabled"}
        
        task.status = 'running'
        self._save_tasks()
        
        start_time = datetime.now()
        result = {'task_id': task_id, 'started_at': start_time.isoformat()}
        
        try:
            # Execute command
            if task.command:
                import subprocess
                result['output'] = subprocess.check_output(
                    task.command, 
                    shell=True, 
                    stderr=subprocess.STDOUT,
                    timeout=3600
                ).decode('utf-8')
                result['exit_code'] = 0
                task.status = 'completed'
            else:
                result['output'] = "No command specified"
                result['exit_code'] = 1
                task.status = 'failed'
        except subprocess.CalledProcessError as e:
            result['error'] = str(e)
            result['exit_code'] = e.returncode
            task.status = 'failed'
        except Exception as e:
            result['error'] = str(e)
            result['exit_code'] = 1
            task.status = 'failed'
        
        task.last_run = datetime.now().isoformat()
        task.retry_count = 0
        
        # Calculate next run
        if task.schedule.get('type') == 'recurring':
            interval = task.schedule.get('interval', 3600)
            task.next_run = (datetime.now() + timedelta(seconds=interval)).isoformat()
        else:
            task.next_run = None
        
        task.results.append(result.copy())
        self._save_tasks()
        
        return result
    
    def start_scheduler(self, blocking: bool = True):
        """Start the scheduler loop"""
        self.running = True
        print(f"[{datetime.now().isoformat()}] Scheduler started")
        
        # Schedule recurring tasks
        for task in self.tasks.values():
            if task.enabled and task.schedule.get('type') == 'recurring':
                interval = task.schedule.get('interval', 3600)
                schedule.every(interval).seconds.do(self._run_task_safe, task.task_id)
                print(f"Scheduled recurring task: {task.name} (every {interval}s)")
        
        if blocking:
            try:
                while self.running:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nScheduler stopped")
                self.stop_scheduler()
        else:
            # Run in background thread
            self._scheduler_thread = Thread(target=self._run_scheduler_loop, daemon=True)
            self._scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the scheduler loop"""
        self.running = False
    
    def _run_scheduler_loop(self):
        """Background scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _run_task_safe(self, task_id: str):
        """Run task with error handling"""
        try:
            self.run_task(task_id, blocking=False)
        except Exception as e:
            task = self.get_task(task_id)
            if task:
                task.status = 'failed'
                task.retry_count += 1
                if task.retry_count < task.max_retries:
                    delay = task.schedule.get('retry_delay', self.config['retry_delay'])
                    print(f"Task {task_id} failed, retrying in {delay}s (attempt {task.retry_count + 1}/{task.max_retries})")
                else:
                    print(f"Task {task_id} failed after {task.max_retries} retries")
                self._save_tasks()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Auto Scheduler - 自动化任务调度器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawsched create --name "Daily Report" --command "python report.py" --schedule '{"type": "recurring", "interval": 86400}'
  clawsched list --enabled true
  clawsched run <task_id>
  clawsched delete <task_id>
  clawsched start
  clawsched stop
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('--name', '-n', required=True, help='Task name')
    create_parser.add_argument('--command', '-c', required=True, help='Command to execute')
    create_parser.add_argument('--schedule', '-s', default='{"type": "once"}', help='Schedule JSON')
    create_parser.add_argument('--enabled', '-e', action='store_true', help='Enable task')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('--name', '-n', help='New name')
    update_parser.add_argument('--command', '-c', help='New command')
    update_parser.add_argument('--schedule', '-s', help='New schedule JSON')
    update_parser.add_argument('--enabled', '-e', type=bool, help='Enable/disable task')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', help='Task ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--enabled', type=bool, help='Filter by enabled status')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a task immediately')
    run_parser.add_argument('task_id', help='Task ID')
    run_parser.add_argument('--blocking', '-b', action='store_true', help='Run blocking mode')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the scheduler')
    start_parser.add_argument('--background', '-d', action='store_true', help='Run in background')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the scheduler')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show scheduler status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    scheduler = JobScheduler()
    
    if args.command == 'create':
        try:
            schedule_dict = json.loads(args.schedule)
        except json.JSONDecodeError:
            print("Error: Invalid schedule JSON")
            sys.exit(1)
        
        task = scheduler.create_task(
            name=args.name,
            command=args.command,
            schedule=schedule_dict,
            enabled=args.enabled
        )
        print(f"Task created: {task.task_id}")
        print(json.dumps(task.to_dict(), indent=2, default=str))
        
    elif args.command == 'update':
        task = scheduler.update_task(args.task_id, **{k: v for k, v in vars(args).items() if k not in ['command', 'task_id']})
        print(f"Task updated: {task.task_id}")
        print(json.dumps(task.to_dict(), indent=2, default=str))
        
    elif args.command == 'delete':
        if scheduler.delete_task(args.task_id):
            print(f"Task deleted: {args.task_id}")
        else:
            print(f"Task not found: {args.task_id}")
            sys.exit(1)
            
    elif args.command == 'list':
        tasks = scheduler.list_tasks(
            enabled=args.enabled,
            status=args.status
        )
        
        if args.json:
            print(json.dumps([t.to_dict() for t in tasks], indent=2, default=str))
        else:
            for task in tasks:
                status_icon = "✅" if task.enabled else "❌"
                print(f"{status_icon} [{task.task_id}] {task.name} - {task.status}")
                print(f"   Command: {task.command[:100]}...")
                print(f"   Next run: {task.next_run}")
                print()
                
    elif args.command == 'run':
        result = scheduler.run_task(args.task_id, blocking=args.blocking)
        print(json.dumps(result, indent=2, default=str))
        
    elif args.command == 'start':
        scheduler.start_scheduler(blocking=not args.background)
        
    elif args.command == 'stop':
        scheduler.stop_scheduler()
        print("Scheduler stopped")
        
    elif args.command == 'status':
        tasks = scheduler.list_tasks()
        enabled_tasks = [t for t in tasks if t.enabled]
        print(f"Tasks: {len(tasks)} total, {len(enabled_tasks)} enabled")
        print(f"Running: {scheduler.running}")


if __name__ == '__main__':
    main()
