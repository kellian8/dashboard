import heapq
import threading
from typing import List, Optional

from PyQt6.QtCore import QThreadPool


class TaskSchedulerService(BaseModel):
    # Class-level lock for singleton initialization
    _instance: Optional['TaskSchedulerService'] = None
    _instance_lock = threading.Lock()

    def __init__(self):
        self._task_queue: list = []  # Min-heap via heapq, ordered by execution time
        self._condition = threading.Condition()  # Combines lock + wait/notify coordination
        self._observers: List[TaskExecutionObserver] = []
        self._observers_lock = threading.Lock()  # Protects the observers list
        self._workers: List[threading.Thread] = []
        self._running: bool = False
        self._sequence_counter: int = 0

    # implement scheduler methods - reference: https://algomaster.io/learn/lld/design-task-scheduler
