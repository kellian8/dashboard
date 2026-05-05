"""Initiate the application instance and load main window"""

import sys
from os import path

from loguru import logger
from loguru_config import LoguruConfig
from PyQt6.QtWidgets import QApplication

from dash.gui.mainWindow import MainWindow


def _stdout_filter(record):
    """Allow only DEBUG, INFO, and WARNING through to stdout."""
    return record["level"].no < 40  # 40 = ERROR


def main():
    # Load logging configuration from file
    LoguruConfig.load(path.join(path.dirname(__file__), 'logging.yml'))
    logger.info("Application logger configured successfully and running")
    logger.info("Starting application!")

    # Set up main PyQt6 application context and starting MainWindow
    # component
    logger.info("Setting up main PyQt6 application with sys.argv")
    app = QApplication(sys.argv)
    logger.info("Loading MainWindow (QWidget)")
    window = MainWindow()
    window.show()

    # Ensure system can exit application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
