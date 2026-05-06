from ABC import ABC, abstractmethod
from pydantic import BaseModel


class Task(ABC, BaseModel):
    @abstractmethod
    def get_name():
        """Return human readable name of the task"""
        pass

    @abstractmethod
    def run():
        """Execute the prescribed function of the task"""
        pass
