"""Initiate the application instance and load main window"""

import signal
import sys
import threading
import tomllib
from pathlib import Path

# Make shared project-root packages (e.g. utils) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import time
from os import environ, mkdir, path

import cherrypy
from dotenv import load_dotenv
from loguru import logger

logger.info("Loading environment variables for application process")
load_dotenv()

from dash.config import ROOT_DIR, TaskConfigs
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
    load_logging_config(Path(__file__).resolve().parent / "pyproject.toml")
    logger.info("Application logger configured successfully and running")
    logger.info("Starting application!")

    # Create the 'temp' dir on start up if not found (for example on first run)
    app_temp_dir = path.normpath(path.join(ROOT_DIR, 'dash/temp'))
    if not path.isdir(app_temp_dir):
        logger.info("No temp dir found on start up. Creation 'temp' directory at source root")
        mkdir(app_temp_dir)

    scheduler: TaskSchedulerService = TaskSchedulerService.getInstance()
    scheduler.initialize(worker_count=2)
    investmentsService = InvestmentsService()

    jsonStore = JsonPersistenceClient(store_path=path.normpath(path.join(ROOT_DIR, environ.get('JSON_STORE_PATH'))))

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

    server_thread = threading.Thread(target=run_server, daemon=True, name="main-server-thread")
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
