"""Keeps the frameless window pinned to the bottom of the Z-order on Windows.

``Qt.WindowStaysOnBottomHint`` covers the common case, but some shells restack
windows on focus changes. Re-issuing ``SetWindowPos(HWND_BOTTOM, …)`` on a short
timer keeps the widget sitting on the desktop beneath everything else.
"""
from __future__ import annotations

import ctypes

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QWindow

_HWND_BOTTOM = 1
# SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
_SWP_FLAGS = 0x0001 | 0x0002 | 0x0010
_REPIN_INTERVAL_MS = 500


class BottomPinner(QObject):
    def __init__(self, window: QWindow, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._window = window

        self._timer = QTimer(self)
        self._timer.setInterval(_REPIN_INTERVAL_MS)
        self._timer.timeout.connect(self._pin)
        self._timer.start()
        self._pin()

    def _pin(self) -> None:
        hwnd = int(self._window.winId())
        ctypes.windll.user32.SetWindowPos(
            hwnd, _HWND_BOTTOM, 0, 0, 0, 0, _SWP_FLAGS
        )
