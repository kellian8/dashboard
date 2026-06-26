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
from loguru_config import LoguruConfig

logger.info("Loading environment variables for application process")
load_dotenv()

from dash.config import ROOT_DIR, TaskConfigs
from dash.scheduling import (
    DataObserver,
    FetchSummaryTask,
    LoggingObserver,
    OneTimeSchedulingStrategy,
    RecurringSchedulingStrategy,
    RecurringTimeSchedulingStrategy,
)
from dash.server import run_server
from dash.services import InvestmentsService, JsonPersistenceClient
from dash.services.schedulingService import TaskSchedulerService

_STRATEGY_BUILDERS = {
    "recurring_time": lambda s: RecurringTimeSchedulingStrategy(time=s.time),
    "interval": lambda s: RecurringSchedulingStrategy(interval=s.interval),
    "one_time": lambda s: OneTimeSchedulingStrategy(execution_time=s.execution_time),
}

def initialise_logger():
    """Initialise the logger with the configuration from logging.yml"""
    with open('pyproject.toml', 'rb') as pp:
        logging_conf = tomllib.load(pp).get('tool', {}).get('logging', {}).get('config-file', None)
        if logging_conf:
            LoguruConfig.load(path.abspath(logging_conf))
        else:
            logger.warning("No logging configuration found in pyproject.toml. Using default logger configuration.")


def main():
    # Load logging configuration from file
    initialise_logger()
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

    config = TaskConfigs["FETCH_SUMMARY"]
    if config.schedules:
        for sched in config.schedules:
            scheduler.schedule(
                task=FetchSummaryTask(investmentsService=investmentsService),
                strategy=_STRATEGY_BUILDERS[sched.type](sched),
            )
    else:
        logger.warning(
            "No schedules configured for task '{}'. Add entries to TaskConfigs.",
            config.name,
        )

    # registering observers after QApplication setup so BridgeDataObserver
    # has access to the the active main window Bridge
    scheduler.addObserver(LoggingObserver())
    # Pass persistance client as store object param
    jsonStore = JsonPersistenceClient(store_path=path.normpath(path.join(ROOT_DIR, environ.get('JSON_STORE_PATH'))))
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
