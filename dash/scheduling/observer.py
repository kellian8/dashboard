import json
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from os import path

from loguru import logger
from pydantic import BaseModel

from ..config import FILES, TaskConfigs
from .taskStatus import TaskStatus


class TaskExecutionObserver(ABC, BaseModel):
    @abstractmethod
    def on_task_started(self, task: 'ScheduledTask') -> None:
        pass

    @abstractmethod
    def on_task_completed(self, task: 'ScheduledTask') -> None:
        pass

    @abstractmethod
    def on_task_failed(self, task: 'ScheduledTask', exception: Exception) -> None:
        pass


class LoggingObserver(TaskExecutionObserver):
    def on_task_started(self, task: 'ScheduledTask') -> None:
        thread_name = threading.current_thread().name
        logger.info("[{}] Task '{}' started", thread_name, task.task.get_name())

    def on_task_completed(self, task: 'ScheduledTask') -> None:
        thread_name = threading.current_thread().name
        logger.success("[{}] Task '{}' completed successfully", thread_name, task.task.get_name())

    def on_task_failed(self, task: 'ScheduledTask', exception: Exception) -> None:
        thread_name = threading.current_thread().name
        logger.error("[{}] Task '{}' failed", thread_name, task.task.get_name())
        logger.exception(exception)


class DataObserver(TaskExecutionObserver):
    store_path: str = path.join(FILES.temp_dir, 'store.json')
    _task_not_failed_or_cancelled = lambda s, t: (
        True if t.status != TaskStatus.CANCELLED or t.status != TaskStatus.FAILED else False
    )

    model_config = {"arbitrary_types_allowed": True}

    def on_task_started(self, task: 'ScheduledTask') -> None:
        pass

    def on_task_completed(self, task: 'ScheduledTask') -> None:
        # Route to the correct UI update callback based on the task's name
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            investment_data: List[tuple] = task.task.data
            logger.debug("Investment data:\n", investment_data)
            if self._task_not_failed_or_cancelled(task):
                store = dict()
                store["investment_fields"] = investment_data
                store["timestamp"] = datetime.isoformat(task._next_execution_time)

                with open(self.store_path, 'w+') as sf:
                    json.dump(store, sf)

            else:
                logger.warning("Task {} result was not saved as execution failed or cancelled", task.task.status)

    def on_task_failed(self, task: 'ScheduledTask', exception: Exception) -> None:
        # Prompt bridge to show stale data warning if the task fails
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            logger.info("unable to fetch investment summary, current store state unchanged")
