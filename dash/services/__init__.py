from typing import Protocol

from dash.services.investmentsService import InvestmentsService
from dash.services.persistenceClient import JsonPersistenceClient


class StoreLike(Protocol):
    def update(self, fields: list, table_name: str) -> None: ...
    def get_from_table(self, table_name: str) -> tuple: ...


__all__ = ["InvestmentsService", "JsonPersistenceClient", "StoreLike"]
