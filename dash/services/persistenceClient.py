import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List


class JsonPersistenceClient:
    # currently a path to a temp json string
    store_path: str | os.PathLike
    # prevent multiple threads accessing the store at the same time
    _store_lock = threading.Lock()

    def __init__(self, store_path: str | os.PathLike):
        if not isinstance(store_path, os.PathLike) and not isinstance(store_path, str):
            raise TypeError(f"Store_path must be a path like object or str. Recieve a {type(store_path)}")
        self.store_path = store_path

    def update(self, fields: List[tuple], table_name: str) -> None:
        with self._store_lock:
            if os.path.isfile(self.store_path) and os.path.getsize(self.store_path) > 0:
                with open(self.store_path, 'r+') as sf:
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
                if table_name in ('investments'):
                    # ensure the table exists in the store, then unpack and update fields.
                    # Raise exception if check fails on invalid table name
                    store[table_name] = dict()
                    store = self._populate_fields_from_tuples(store, fields, table_name)
                else:
                    raise RuntimeError(
                        "Persistence Error - Table does not exist in store. Check for invalid table name or json store is set up correctly"
                    )
                # Write fresh store json object
                with open(self.store_path, 'w+') as sf:
                    if store is not None:
                        json.dump(store, sf)

    def _populate_fields_from_tuples(
        self, store: Dict[str | Any], fields: List[tuple], table: str
    ) -> Dict[str | Any] | None:
        if fields is None:
            return None
        for field, value in fields:
            store[table][field] = value if value is not None else store[table][field]
            store[f'{table}_timestamp'] = datetime.now(timezone.utc).isoformat()
        return store

    def get_from_table(self, table_name: str) -> Dict[str | Any]:
        with self._store_lock:
            if os.path.isfile(self.store_path):
                with open(self.store_path, 'r') as sf:
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
            # otherwise throw an error flagging non-existent store file
            else:
                raise RuntimeError("Persistence Error - store file does not exists.")
