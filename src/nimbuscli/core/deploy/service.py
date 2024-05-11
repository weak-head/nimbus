from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from functools import reduce

from nimbuscli.core.execute import CompletedProcess


class Service(ABC):
    """
    Defines an abstract service.
    All services should follow the APIs defined by this class.
    """

    def __init__(self, name: str):
        self._name: str = name

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """
        Service name.
        """
        return self._name

    @abstractmethod
    def start(self) -> OperationStatus:
        """
        Start the service.
        """

    @abstractmethod
    def stop(self) -> OperationStatus:
        """
        Stop the service.
        """


class OperationStatus:
    """
    The outcome of the service operation.
    """

    def __init__(self, service: str, operation: str, kind: str):
        self.service: str = service
        self.operation: str = operation
        self.kind: str = kind
        self.processes: list[CompletedProcess] = []

    @property
    def success(self) -> bool:
        return all(proc.success for proc in self.processes)

    @property
    def elapsed(self) -> timedelta:
        return reduce(lambda a, b: a + b.elapsed, self.processes, timedelta(seconds=0))
