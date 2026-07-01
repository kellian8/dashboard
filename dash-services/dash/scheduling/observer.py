import threading
from abc import ABC, abstractmethod
from typing import List

from loguru import logger
from pydantic import BaseModel, PrivateAttr

from ..config import TaskConfigs
from ..services import StoreLike
from .scheduledTask import ScheduledTask


class TaskExecutionObserver(ABC, BaseModel):
    @abstractmethod
    def on_task_started(self, task: ScheduledTask) -> None:
        pass

    @abstractmethod
    def on_task_completed(self, task: ScheduledTask) -> None:
        pass

    @abstractmethod
    def on_task_failed(self, task: ScheduledTask, exception: Exception) -> None:
        pass


class LoggingObserver(TaskExecutionObserver):
    def on_task_started(self, task: ScheduledTask) -> None:
        thread_name = threading.current_thread().name
        logger.info("[{}] Task '{}' started", thread_name, task.task.get_name())

    def on_task_completed(self, task: ScheduledTask) -> None:
        thread_name = threading.current_thread().name
        logger.success("[{}] Task '{}' completed successfully", thread_name, task.task.get_name())

    def on_task_failed(self, task: ScheduledTask, exception: Exception) -> None:
        thread_name = threading.current_thread().name
        logger.error("[{}] Task '{}' failed", thread_name, task.task.get_name())
        logger.exception(exception)


class DataObserver(TaskExecutionObserver):
    # TODO: create store Object with method to persist result (like 'self.store.update({investment_fields: <some date>})')
    _store: StoreLike = PrivateAttr()
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, store: StoreLike):
        # duck typing to validate store service that then add instatiate it as store property
        if hasattr(store, 'update') and hasattr(store, 'get_from_table'):
            self._store = store
        else:
            raise TypeError("Data observer couldn't be instantiated. Must provide a valid store client")

    def on_task_started(self, task: ScheduledTask) -> None:
        pass

    def on_task_completed(self, task: ScheduledTask) -> None:
        # Route to the correct UI update callback based on the task's name
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            investment_data: List[tuple] = task.task.data
            try:
                self._store.update(investment_data, 'investments')
                logger.info("Investment data updated successfully in the store")
            except Exception as e:
                logger.error("Failed updating store: {}", e)
                raise
    def on_task_failed(self, task: ScheduledTask, exception: Exception) -> None:
        # Prompt bridge to show stale data warning if the task fails
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            logger.info("unable to fetch investment summary, current store state unchanged")
