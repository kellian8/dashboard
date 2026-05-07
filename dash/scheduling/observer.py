import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional

from loguru import logger
from pydantic import BaseModel
from PyQt6.QtCore import pyqtBoundSignal

from ..config import TaskConfigs


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


class BridgeDataObserver(TaskExecutionObserver):
    updateInvestmentsQSignal: pyqtBoundSignal = None
    alertStaleData: Optional[pyqtBoundSignal] = None

    model_config = {"arbitrary_types_allowed": True}

    def on_task_started(self, task: 'ScheduledTask') -> None:
        pass

    def on_task_completed(self, task: 'ScheduledTask') -> None:
        # Route to the correct UI update callback based on the task's name
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            if self.updateInvestmentsQSignal is not None:
                self.updateInvestmentsQSignal.emit(task.task.data)
            else:
                logger.warning("BridgeDataObserver: _updateInvestmentsQSignal callback is not set")

    def on_task_failed(self, task: 'ScheduledTask', exception: Exception) -> None:
        # Prompt bridge to show stale data warning if the task fails
        if task.task.get_name() == TaskConfigs['FETCH_SUMMARY'].name:
            if self.alertStaleData is not None:
                self.alertStaleData()
            else:
                logger.warning("BridgeDataObserver: _alertStaleData callback is not set")
