from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from loguru import logger
from pydantic import BaseModel, PrivateAttr

from ..config import TaskConfigs
from ..services.investmentsService import InvestmentsService
from ..services.persistenceClient import JsonPersistenceClient


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
        """Get the latest summary data from the investments service."""
        try:
            summary_data = self.investmentsService.get_summary()
            if summary_data is not None:
                # Extract the nested investments object; default to empty dict if missing
                self._data = self.flatten_summary(summary_data)

        except Exception as e:
            raise e

    @property
    def data(self) -> Optional[List[Tuple[str, str]]]:
        return self._data
    
    def flatten_summary(self, summary_data: Dict) -> List[Tuple[str, str]]:
        """Flatten the nested summary dict into a list of key-value pairs."""
        investments = summary_data.get("investments", {})
        cash = summary_data.get("cash", {})

        return [
            ("Current Value", investments.get("currentValue")),
            ("Realized P/L", investments.get("realizedProfitLoss")),
            ("Total Cost", investments.get("totalCost")),
            ("Unrealized P/L", investments.get("unrealizedProfitLoss")),
            # totalValue and free cash live at the top level of the response
            ("Total Value", summary_data.get("totalValue")) ,
            ("Free Cash", cash.get("availableToTrade")),
        ]


class UpdateGuiSummaryTask(Task):
    model_config = {"arbitrary_types_allowed": True}

    store: JsonPersistenceClient
    investmentsService: InvestmentsService
    _name: str = PrivateAttr(default_factory=lambda: TaskConfigs["UPDATE_GUI_SUMMARY"].name)

    def get_name(self) -> str:
        return self._name

    def execute(self) -> None:
        """Get the latest summary data from the store and push it to the widget."""
        ts, investment_data = self.store.get_from_table('investments')
        if ts is not None and investment_data is not None:
            # Construct a summary dict to send to the widget.
            summary = {
                "timestamp": ts,
                "investments": investment_data
            }

            success = self.investmentsService.push_summary_to_gui(summary)
            if success:
                logger.success("Gui summary updated to latest!")
            else:
                raise RuntimeError("Failed to push summary to gui.")

