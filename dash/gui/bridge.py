from PyQt6.QtCore import QObject, Qt, pyqtProperty, pyqtSignal, pyqtSlot


class Bridge(QObject):
    dataChanged = pyqtSignal()
    summary_updated = pyqtSignal(list)

    def __init__(self, window=None):
        super().__init__()
        self._window = window
        self._investment_summary_label = "Investments"
        self._investment_summary_fields = [
            ("Current Value", "-"),
            ("Realized P/L", "-"),
            ("Total Cost", "-"),
            ("Unrealized P/L", "-"),
            ("Total Value", "-"),
            ("Free Cash", "-"),
        ]

        self.summary_updated.connect(self.update_investment_fields, Qt.ConnectionType.QueuedConnection)

    @pyqtProperty(str, notify=dataChanged)
    def investment_summary_label(self):
        return self._investment_summary_label

    def update_label(self, value):
        self._investment_summary_label = value
        self.dataChanged.emit()

    @pyqtProperty('QVariantList', notify=dataChanged)
    def investment_summary_fields(self):
        return [{"key": k, "value": v} for k, v in self._investment_summary_fields]

    @pyqtSlot(list)
    def update_investment_fields(self, value):
        self._investment_summary_fields = value
        self.dataChanged.emit()

    @pyqtSlot(int, int)
    def moveWindow(self, dx, dy):
        if self._window:
            pos = self._window.pos()
            self._window.move(pos.x() + dx, pos.y() + dy)
