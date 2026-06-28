"""Background polling of the endpoint on a fixed interval.

A ``QTimer`` ticks every ``interval_seconds``; each tick runs one HTTP fetch on
a worker ``QThread`` so the UI thread never blocks. Results are surfaced as Qt
signals carrying a domain ``AccountSummary`` (or an error string).
"""
from __future__ import annotations

from loguru import logger
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal

from ..data import AccountSummary
from .api_client import ApiClient


class _FetchWorker(QThread):
    succeeded = pyqtSignal(object)  # AccountSummary
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, client: ApiClient, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._client = client

    def run(self) -> None:
        logger.debug("Fetch worker started")
        try:
            summary = AccountSummary.from_json(self._client.fetch())
            logger.debug("Fetch worker succeeded")
            self.succeeded.emit(summary)
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI as text
            logger.opt(exception=True).warning("Fetch worker failed: {}", exc)
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class Poller(QObject):
    summaryReady = pyqtSignal(object)  # AccountSummary
    fetchFailed = pyqtSignal(str)

    def __init__(self, client: ApiClient, interval_seconds: int,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._client = client
        self._worker: _FetchWorker | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(interval_seconds * 1000)
        self._timer.timeout.connect(self._tick)

        logger.debug("Poller configured with interval={}s", interval_seconds)

    def start(self) -> None:
        logger.info("Poller starting")
        self._tick()          # fetch immediately on launch
        self._timer.start()

    def _tick(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            logger.warning("Tick skipped — previous fetch still in flight")
            return

        logger.debug("Tick: spawning fetch worker")
        self._worker = _FetchWorker(self._client, self)
        self._worker.succeeded.connect(self.summaryReady)
        self._worker.failed.connect(self.fetchFailed)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()