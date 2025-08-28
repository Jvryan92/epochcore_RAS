"""Advanced task scheduling for agents."""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Union
import croniter


class AgentScheduler:
    """Scheduler for managing agent task execution."""

    def __init__(self):
        """Initialize the scheduler."""
        self.tasks: Dict[str, Dict] = {}
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def add_task(
        self,
        name: str,
        func: Callable,
        schedule: Union[str, int, timedelta],
        args: tuple = (),
        kwargs: dict = None
    ):
        """Add a task to the scheduler.

        Args:
            name: Task name
            func: Function to execute
            schedule: Cron expression, interval in seconds, or timedelta
            args: Function arguments
            kwargs: Function keyword arguments
        """
        self.tasks[name] = {
            'func': func,
            'schedule': schedule,
            'args': args,
            'kwargs': kwargs or {},
            'last_run': None,
            'next_run': None,
            '_task': None
        }

    async def _run_task(self, name: str):
        """Run a scheduled task.

        Args:
            name: Task name
        """
        task = self.tasks[name]
        while self._running:
            try:
                now = datetime.now()
                
                # Calculate next run time
                if isinstance(task['schedule'], (int, float)):
                    next_run = now + timedelta(seconds=task['schedule'])
                elif isinstance(task['schedule'], timedelta):
                    next_run = now + task['schedule']
                else:  # Cron expression
                    cron = croniter.croniter(task['schedule'], now)
                    next_run = cron.get_next(datetime)

                task['next_run'] = next_run
                
                # Wait until next run time
                wait_seconds = (next_run - now).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)

                # Execute task
                if asyncio.iscoroutinefunction(task['func']):
                    await task['func'](*task['args'], **task['kwargs'])
                else:
                    task['func'](*task['args'], **task['kwargs'])

                task['last_run'] = datetime.now()

            except Exception as e:
                print(f"Error in task {name}: {e}")
                await asyncio.sleep(1)  # Prevent tight error loop

    def start(self):
        """Start the scheduler."""
        self._running = True
        self._loop = asyncio.get_event_loop()
        
        for name in self.tasks:
            task = self.tasks[name]
            task['_task'] = self._loop.create_task(self._run_task(name))

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._loop:
            for task in self.tasks.values():
                if task['_task']:
                    task['_task'].cancel()

    def get_task_status(self) -> List[Dict]:
        """Get status of all tasks.

        Returns:
            List of task status dictionaries
        """
        status = []
        for name, task in self.tasks.items():
            status.append({
                'name': name,
                'last_run': task['last_run'],
                'next_run': task['next_run'],
                'schedule': task['schedule'],
                'running': task['_task'] is not None and not task['_task'].done()
            })
        return status
