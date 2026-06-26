"""Composition root: builds every component and wires the signal flow.

    Poller --(AccountSummary)--> Application._on_summary
                                     |
                          SnapshotStore (persist + 24h baseline)
                                     |
                          build_view_model --> SummaryBridge --> QML
"""
from __future__ import annotations

import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

from .bridge import SummaryBridge
from .config import Config
from .data import ApiClient, SnapshotStore
from .domain import AccountSummary
from .paths import MAIN_QML
from .presentation import build_view_model
from .services import BottomPinner, Poller


class Application:
    def __init__(self) -> None:
        self._qt_app = QGuiApplication(sys.argv)

        self._config = Config.load()
        self._store = SnapshotStore()
        self._bridge = SummaryBridge()
        self._poller = Poller(
            ApiClient(self._config.endpoint_url),
            self._config.poll_interval_seconds,
        )

        self._engine = QQmlApplicationEngine()
        self._engine.rootContext().setContextProperty("bridge", self._bridge)
        self._engine.load(QUrl.fromLocalFile(str(MAIN_QML)))
        if not self._engine.rootObjects():
            raise RuntimeError(f"Failed to load QML: {MAIN_QML}")

        self._window = self._engine.rootObjects()[0]
        self._position_window()
        self._pinner = BottomPinner(self._window)

        self._poller.summaryReady.connect(self._on_summary)
        self._poller.fetchFailed.connect(self._on_error)

    def _position_window(self) -> None:
        pos = self._config.position
        self._window.setProperty("x", pos["x"])
        self._window.setProperty("y", pos["y"])

    def _on_summary(self, summary: AccountSummary) -> None:
        self._store.insert(summary.timestamp, summary.total_value)
        baseline = self._store.value_near_24h_ago()
        self._bridge.set_model(build_view_model(summary, baseline))

    def _on_error(self, message: str) -> None:
        self._bridge.show_error(message)

    def run(self) -> int:
        self._poller.start()
        return self._qt_app.exec()
