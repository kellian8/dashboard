
from os import getenv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if getenv('ENV') == 'development':
    ROOT_DIR = PROJECT_ROOT.parent
else:
    ROOT_DIR = PROJECT_ROOT

LOGGING_CONFIG_PATH = ROOT_DIR / 'logging.yml'
DB_PATH = PROJECT_ROOT / 'store.json'