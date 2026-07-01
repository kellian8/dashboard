import json
import threading

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

from loguru import logger
from ..constants import TIMEZONE


class JsonPersistenceClient:
    # currently a path to a temp json string
    _store_db: str | Path
    # prevent multiple threads accessing the store at the same time
    _store_lock = threading.Lock()

    def __init__(self, store_path: str | Path):
        if isinstance(store_path, str):
            store_path = Path(store_path)
        elif not isinstance(store_path, Path):
            raise TypeError("store_path must be a str or Path object")
        
        # Otherwise, store_path is a Path object, so we can use it directly
        self._store_db = store_path
        logger.info("Initialized local store client: {}", self._store_db)

    def update(self, fields: List[tuple], table_name: str) -> None:
        with self._store_lock:
            if not self._is_empty_store():
                with open(self._store_db, 'r+') as sf:
                    store = json.load(sf)

                    if store.get(table_name) is not None:
                        # ensure the table exists in the store, then unpack and update fields.
                        # Raise exception if check fails on invalid table name
                        store = self._populate_fields_from_tuples(store, fields, table_name)
                    else:
                        raise RuntimeError(
                            "Persistence Error - Table does not exist in store. Check for invalid table name or json store is set up correctly"
                        )

                    # Write complete json update object to file
                    if store is not None:
                        sf.seek(0)
                        sf.truncate()
                        json.dump(store, sf)
            else:
                # Create the store object, and populate with 'fields' if json file does not already exists
                store = dict()
                if table_name in ['investments']:
                    # ensure the table exists in the store, then unpack and update fields.
                    # Raise exception if check fails on invalid table name
                    store[table_name] = dict()
                    store = self._populate_fields_from_tuples(store, fields, table_name)
                else:
                    raise RuntimeError(
                        "Persistence Error - Table does not exist in store. Check for invalid table name or json store is set up correctly"
                    )
                # Write fresh store json object
                with open(self._store_db, 'w+') as sf:
                    if store is not None:
                        sf.seek(0)
                        sf.truncate(0)
                        json.dump(store, sf)

    def _populate_fields_from_tuples(
        self, store: Dict[str, Any], fields: List[tuple], table: str
    ) -> Dict[str, Any] | None:
        if fields is None:
            return None
        for field, value in fields:
            store[table][field] = value if value is not None else store[table][field]
            store[f'{table}_timestamp'] = datetime.now(ZoneInfo(TIMEZONE)).isoformat()
        return store

    def get_from_table(self, table_name: str) -> Dict[str, Any]:
        with self._store_lock:
            if not self._is_empty_store():
                with open(self._store_db, 'r') as sf:
                    store = json.load(sf)
                    # check that the table exists in the store if so return.
                    # If not throw an error
                    table_data = store.get(table_name)
                    if table_data is not None:
                        ts = store.get(f'{table_name}_timestamp')
                        return ts, table_data
                    else:
                        raise RuntimeError(
                            "Persistence Error - Table does not exist in store. Check for invalid table name or json store is set up correctly"
                        )

    def _is_empty_store(self) -> bool:
        if self._store_db.is_file() and self._store_db.stat().st_size > 0:
            with open(self._store_db, 'r') as sf:
                store = json.load(sf)
                return not bool(store)
        return True