from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot


class Bridge(QObject):
    dataChanged = pyqtSignal()

    def __init__(self, window=None):
        super().__init__()
        self._window = window
        self._label = "Investments"
        self._fields = [
            ("Total Inv.", "$10,000"),
            ("Returns", "$1,500"),
            ("Growth", "15%"),
            ("Dividends", "$200"),
            ("Net Profit", "$1,300"),
            ("Loss", "$0"),
            ("Tax", "$300"),
            ("Balance", "$8,700"),
        ]

    @pyqtProperty(str, notify=dataChanged)
    def label(self):
        return self._label

    def update_label(self, value):
        self._label = value
        self.dataChanged.emit()

    @pyqtProperty('QVariantList', notify=dataChanged)
    def fields(self):
        return [{"key": k, "value": v} for k, v in self._fields]

    def update_fields(self, value):
        self._fields = value
        self.dataChanged.emit()

    @pyqtSlot(int, int)
    def moveWindow(self, dx, dy):
        if self._window:
            pos = self._window.pos()
            self._window.move(pos.x() + dx, pos.y() + dy)
