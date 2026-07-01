"""Initiate the application instance and load main window"""

import signal
import sys
import threading
from pathlib import Path

# Make shared project-root packages (e.g. utils) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import time
from os import mkdir, getenv

import cherrypy
from loguru import logger

if Path(__file__).resolve().parent.parent.joinpath(".env").exists():
    from dotenv import load_dotenv
    load_dotenv()

from dash.config import TaskConfigs
from dash.paths import DB_PATH, LOGGING_CONFIG_PATH
from dash.scheduling import (
    DataObserver,
    FetchSummaryTask,
    UpdateGuiSummaryTask,
    LoggingObserver,
    OneTimeSchedulingStrategy,
    RecurringSchedulingStrategy,
    RecurringTimeSchedulingStrategy,
)
from dash.server import run_server
from dash.services import InvestmentsService, JsonPersistenceClient
from dash.services.schedulingService import TaskSchedulerService

from logging_conf import load_logging_config

_STRATEGY_BUILDERS = {
    "recurring_time": lambda s: RecurringTimeSchedulingStrategy(time=s.time),
    "interval": lambda s: RecurringSchedulingStrategy(interval=s.interval),
    "one_time": lambda s: OneTimeSchedulingStrategy(execution_time=s.execution_time),
}

_TASK_MAP = {
    "fetch_investment_summary": FetchSummaryTask,
    "update_gui_summary": UpdateGuiSummaryTask,
}

def main():
    # Load logging configuration from file
    load_logging_config(LOGGING_CONFIG_PATH) # app/project.toml or pyproject.toml
    logger.info("Starting application")

    scheduler: TaskSchedulerService = TaskSchedulerService.getInstance()
    scheduler.initialize(worker_count=2)
    investmentsService = InvestmentsService()

    jsonStore = JsonPersistenceClient(store_path=DB_PATH)

    config = TaskConfigs["FETCH_SUMMARY"]
    if config.schedules:
        for sched in config.schedules:
            scheduler.schedule(
                task=FetchSummaryTask(investmentsService=investmentsService),
                strategy=_STRATEGY_BUILDERS[sched.type](sched),
                callback=_TASK_MAP[config.callback](store=jsonStore, investmentsService=investmentsService),
            )
    else:
        logger.warning(
            "No schedules configured for task '{}'. Add entries to TaskConfigs.",
            config.name,
        )

    scheduler.addObserver(LoggingObserver())
    # Pass persistance client as store object param
    scheduler.addObserver(DataObserver(jsonStore))

    shutdown_event = threading.Event()

    # Hook into CherryPy's own stop event so Ctrl+C (which CherryPy intercepts)
    # still triggers a clean application shutdown.
    cherrypy.engine.subscribe('stop', lambda: (server_thread.join(timeout=5), shutdown_event.set()))

    # SIGTERM is not claimed by CherryPy, so handle it directly.
    def _handle_sigterm(signum, frame):
        logger.info("Received signal {}, shutting down...", signum)
        cherrypy.engine.exit()

    signal.signal(signal.SIGTERM, _handle_sigterm)

    server_thread = threading.Thread(
        target=run_server,
        daemon=True, 
        name="main-server-thread",
        kwargs={"store_client": jsonStore},
    )
    server_thread.start()

    try:
        shutdown_event.wait()
    except KeyboardInterrupt:
        logger.info("Shutdown signal received, shutting down...")
        cherrypy.engine.exit()
    finally:
        server_thread.join(timeout=5)
        scheduler.shutdown()
        logger.info("Application stopped")


if __name__ == "__main__":
    main()
