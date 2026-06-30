"""Background polling of the endpoint on a fixed interval.

A ``QTimer`` ticks every ``interval_seconds``; each tick runs one HTTP fetch on
a worker ``QThread`` so the UI thread never blocks. Results are surfaced as Qt
signals carrying a domain ``AccountSummary`` (or an error string).
"""
from __future__ import annotations

import threading

from loguru import logger
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ..data import AccountSummary
from .api_client import ApiClient


class FetchSummaryWorker(QThread):
    succeeded = pyqtSignal(object)  # AccountSummary
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, client: ApiClient, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._client = client
        self.setObjectName("Fetch_summary_worker")

    def run(self) -> None:
        threading.current_thread().name = QThread.currentThread().objectName()
        logger.debug("Fetch worker started")
        try:
            summary = AccountSummary.from_dict(self._client.fetch())
            logger.debug("Fetch worker succeeded")
            self.succeeded.emit(summary)
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI as text
            logger.opt(exception=True).warning("Fetch worker failed: {}", exc)
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()