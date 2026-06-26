"""The bridge between Python and QML.

QML binds to a single ``model`` property (a map). Whenever Python pushes a new
view model, ``modelChanged`` fires and every QML binding re-evaluates. This is
the only object exposed to the QML context, so the UI has exactly one surface
to talk to.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

from ..presentation import empty_view_model
from ..presentation.view_model import error_patch


class SummaryBridge(QObject):
    modelChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._model: dict = empty_view_model()

    @pyqtProperty("QVariantMap", notify=modelChanged)
    def model(self) -> dict:
        return self._model

    def set_model(self, model: dict) -> None:
        self._model = model
        self.modelChanged.emit()

    def show_error(self, message: str) -> None:
        self._model = error_patch(self._model, message)
        self.modelChanged.emit()
