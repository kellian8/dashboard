
import tomllib
from pathlib import Path
from loguru import logger
from loguru_config import LoguruConfig


def load_logging_config(proj_config) -> None:
    # Initialise the logger with the configuration from logging.yml
    with open(proj_config, 'rb') as proj_f:
        logging_conf = tomllib.load(proj_f).get('tool', {}).get('logging', {}).get('config-file', None)
        if logging_conf:
            LoguruConfig.load(Path(logging_conf).resolve())
        else:
            logger.warning("No logging configuration found in pyproject.toml. Using default logger configuration.")