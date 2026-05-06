"""Initiate the application instance and load main window"""

import sys
from os import path

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from loguru_config import LoguruConfig
from PyQt6.QtWidgets import QApplication

from dash.gui.mainWindow import MainWindow

from ..scheduling.Observer import BridgeDataObserver


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

    # TODO: Start the scheduler, register observers and give tasks
    # Bridge data observer requires bridge update callbacks
    # Then on app.exit() shutdown scheduler

    # Ensure system can exit application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
