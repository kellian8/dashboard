"""Initiate the application instance and load main window"""

import signal
import threading
from datetime import time
from os import environ, path
from typing import List

import cherrypy
from loguru import logger
from loguru_config import LoguruConfig

if environ.get("ENV") == "development":
    from dotenv import load_dotenv

    load_dotenv()

from dash.config import TaskConfigs
from dash.scheduling import (
    DataObserver,
    FetchSummaryTask,
    LoggingObserver,
    RecurringTimeSchedulingStrategy,
    Task,
)
from dash.server import run_server
from dash.services import InvestmentsService
from dash.services.schedulingService import TaskSchedulerService


def _stdout_filter(record):
    """Allow only DEBUG, INFO, and WARNING through to stdout."""
    return record["level"].no < 40  # 40 = ERROR


def main():
    # Load logging configuration from file
    LoguruConfig.load(path.join(path.dirname(__file__), "logging.yml"))
    logger.info("Application logger configured successfully and running")
    logger.info("Starting application!")

    logger.debug("base_url: {}", environ.get("TRADING212_BASE_URL"))
    scheduler: TaskSchedulerService = TaskSchedulerService.getInstance()
    scheduler.initialize(worker_count=2)

    investmentsService = InvestmentsService()

    scheduled_fetch_times: List[time] = TaskConfigs["FETCH_SUMMARY"].scheduled_times

    if len(scheduled_fetch_times) > 0:
        for t in scheduled_fetch_times:
            investment_summary_task: Task = FetchSummaryTask(
                investmentsService=investmentsService
            )
            investment_summary_task_schedule: SchedulingStrategy = (
                RecurringTimeSchedulingStrategy(time=t)
            )
            scheduler.schedule(
                task=investment_summary_task, strategy=investment_summary_task_schedule
            )
    else:
        logger.warn(
            "Unable to schedule {} task. Add schedule times to task config",
            TaskConfigs["FETCH_SUMMARY"].name,
        )

    # registering observers after QApplication setup so BridgeDataObserver
    # has access to the the active main window Bridge
    scheduler.addObserver(LoggingObserver())
    scheduler.addObserver(DataObserver())

    server_thread = threading.Thread(
        target=run_server, daemon=True, name="main-server-thread"
    )
    server_thread.start()

    shutdown_event = threading.Event()

    def _handle_application_shutdown(signum, frame):
        # Allows the graceful application exit on all shutdown signals.
        # Cherrypy bus process shutdown initiated first through its signal handler.
        # then main proc shutdown event triggered.
        logger.info("Received signal {}, shutting down...", signum)
        cherrypy.engine.exit()
        shutdown_event.set()

    signal.signal(signal.SIGTERM, _handle_application_shutdown)
    signal.signal(signal.SIGINT, _handle_application_shutdown)

    shutdown_event.wait()  # Shutdown event waits until defined signals
    scheduler.shutdown()
    logger.info("Application stopped")


if __name__ == "__main__":
    main()
