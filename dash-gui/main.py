"""Entry point. Run with: python main.py"""
import os
import sys
import tomllib
from pathlib import Path
from loguru import logger
from loguru_config import LoguruConfig

# Static widget — the software scene-graph renders identically and avoids the
# GPU backend failing when launched early at startup. Overridable via the env.
os.environ.setdefault("QT_QUICK_BACKEND", "software")

# Make the `src` layout importable without an install step.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
# Make shared project-root packages (e.g. utils) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from investment_widget.app import Application
from investment_widget.signal_tether import run_signal_tether 



def main() -> int:
    
    # Initialise the logger with the configuration from logging.yml
    with open('pyproject.toml', 'rb') as pp:
        logging_conf = tomllib.load(pp).get('tool', {}).get('logging', {}).get('config-file', None)
        if logging_conf:
            LoguruConfig.load(os.path.abspath(logging_conf))
        else:
            logger.warning("No logging configuration found in pyproject.toml. Using default logger configuration.")

    logger.info("dash-gui starting up")
    widget = Application()
    _signal_tether = run_signal_tether()
    exit_code = widget.run()
    logger.info("dash-gui shut down | exit_code={}", exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
