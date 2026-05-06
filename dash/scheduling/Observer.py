import threading
from abc import ABC, abstractmethod

from loguru import logger
from pydantic import BaseModel


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
    _updateInvestmentsUI: function
    _alertStaleData: function

    def on_task_started(self, task: 'ScheduledTask') -> None:
        pass

    def on_task_completed(self, task: 'ScheduledTask', data: Dict[str, Any]) -> None:
        # Checking the data structure is compatible with qml enumeration
        # passing the date to bridge through callback depending on task name
        if isinstance(data, Dict):
            thread_name = threading.current_thread().name
            if 'investments_summary_getter' in thread_name:
                self._updateInvestmentsUI(data)
        else:
            TypeError("Date for QML bridge insertion must be of type List<Dict>")

    def on_task_failed(self, task: 'ScheduledTask', exception: Exception) -> None:
        # Prompt bridge to show stale data warning if tasks fail
        if 'investments_summary_getter' in thread_name:
            self._warnStaleData()
