"""Initiate the application instance and load main window"""

import sys
from datetime import time
from os import path
from typing import List

from loguru import logger
from loguru_config import LoguruConfig
from PyQt6.QtWidgets import QApplication

from dash.config import TaskConfigs
from dash.gui.mainWindow import MainWindow
from dash.scheduling import (
    BridgeDataObserver,
    FetchSummaryTask,
    LoggingObserver,
    RecurringTimeSchedulingStrategy,
    Task,
)
from dash.services import InvestmentsService
from dash.services.schedulingService import TaskSchedulerService

if os.environ.get("ENV") == "development":
    from dotenv import load_dotenv

    load_dotenv()


def _stdout_filter(record):
    """Allow only DEBUG, INFO, and WARNING through to stdout."""
    return record["level"].no < 40  # 40 = ERROR


def main():
    # Load logging configuration from file
    LoguruConfig.load(path.join(path.dirname(__file__), 'logging.yml'))
    logger.info("Application logger configured successfully and running")
    logger.info("Starting application!")

    scheduler: TaskSchedulerService = TaskSchedulerService.getInstance()
    scheduler.initialize(worker_count=2)

    investmentsService = InvestmentsService()

    scheduled_fetch_times: List[time] = TaskConfigs["FETCH_SUMMARY"].scheduled_times

    if len(scheduled_fetch_times) > 0:
        for t in scheduled_fetch_times:
            investment_summary_task: Task = FetchSummaryTask(investmentsService=investmentsService)
            investment_summary_task_schedule: SchedulingStrategy = RecurringTimeSchedulingStrategy(time=t)
            scheduler.schedule(task=investment_summary_task, strategy=investment_summary_task_schedule)
    else:
        logger.warn(
            "Unable to schedule {} task. Add schedule times to task config",
            TaskConfigs["FETCH_SUMMARY"].name,
        )

    # Set up main PyQt6 application context and starting MainWindow
    # component
    logger.info("Setting up main PyQt6 application with sys.argv")
    app = QApplication(sys.argv)
    logger.info("Loading MainWindow (QWidget)")
    window = MainWindow()

    # registering observers after QApplication setup so BridgeDataObserver
    # has access to the the active main window Bridge
    scheduler.addObserver(LoggingObserver())
    bridgeDataObserver = BridgeDataObserver(updateInvestmentsQSignal=window.bridge.summary_updated)
    scheduler.addObserver(bridgeDataObserver)

    window.show()

    # Ensure system can exit application
    app.aboutToQuit.connect(scheduler.shutdown)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
