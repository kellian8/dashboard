from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, PrivateAttr

from ..config import TaskConfigs
from ..services.investmentsService import InvestmentsService


class Task(ABC, BaseModel):
    @abstractmethod
    def get_name(self) -> str:
        """Return human readable name of the task"""
        pass

    @abstractmethod
    def execute(self) -> None:
        """Execute the prescribed function of the task"""
        pass


class FetchSummaryTask(Task):
    model_config = {"arbitrary_types_allowed": True}

    investmentsService: InvestmentsService
    _name: str = PrivateAttr(default_factory=lambda: TaskConfigs["FETCH_SUMMARY"].name)
    _data: Optional[List[Tuple[str, str]]] = PrivateAttr(default=None)

    def get_name(self) -> str:
        return self._name

    def execute(self) -> None:
        # get_summary returns the already-flattened List[Dict] ready for the bridge,
        # or None if the request failed.
        summary_data = self.investmentsService.get_summary()

        result = None
        if summary_data is not None:
            # Extract the nested investments object; default to empty dict if missing
            investments = summary_data.get("investments", {})
            cash = summary_data.get("cash", {})

            # Flatten the relevant properties into a list of key/value dicts.
            # Excludes: id, currency
            fmt = self.investmentsService.format_price
            result = [
                ("Current Value", fmt(investments.get("currentValue"))),
                ("Realized P/L", fmt(investments.get("realizedProfitLoss"))),
                ("Total Cost", fmt(investments.get("totalCost"))),
                ("Unrealized P/L", fmt(investments.get("unrealizedProfitLoss"))),
                # totalValue and free cash live at the top level of the response
                ("Total Value", fmt(summary_data.get("totalValue"))),
                ("Free Cash", fmt(cash.get("availableToTrade"))),
            ]

        self._data = result

    @property
    def data(self) -> Optional[List[Tuple[str, str]]]:
        return self._data
