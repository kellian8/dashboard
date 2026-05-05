import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QMainWindow

from .bridge import Bridge


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set main window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create and configure the QML widget
        self.qml_widget = QQuickWidget()
        self.qml_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.qml_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.qml_widget.setClearColor(Qt.GlobalColor.transparent)

        # Connect the bridge before loading QML
        self.bridge = Bridge(window=self)
        self.qml_widget.rootContext().setContextProperty("bridge", self.bridge)

        qml_path = os.path.join(os.path.dirname(__file__), "qml", "application.qml")
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_path))

        self.setCentralWidget(self.qml_widget)
