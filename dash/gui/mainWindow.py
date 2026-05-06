import os

from loguru import logger
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QMainWindow

from .bridge import Bridge


class MainWindow(QMainWindow):
    def __init__(self):
        logger.debug("Initialising MainWindow")
        super().__init__()

        # Set main window properties
        logger.debug("Applying frameless + translucent window attributes")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create and configure the QML widget
        logger.debug("Creating QQuickWidget")
        self.qml_widget = QQuickWidget()
        self.qml_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.qml_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.qml_widget.setClearColor(Qt.GlobalColor.transparent)

        # Connect the bridge before loading QML
        logger.debug("Instantiating Bridge and registering context property")
        self.bridge = Bridge(window=self)
        self.qml_widget.rootContext().setContextProperty("bridge", self.bridge)

        qml_path = os.path.join(os.path.dirname(__file__), "qml", "application.qml")
        logger.info("Loading QML source: {}", qml_path)
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_path))

        errors = self.qml_widget.errors()
        if errors:
            for error in errors:
                logger.error("QML error: {}", error.toString())
        else:
            logger.info("QML loaded successfully")

        self.setCentralWidget(self.qml_widget)
        logger.info("MainWindow ready")
