from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Generic, TypeVar

from nas.core.provider import Provider, Resource


class Command(ABC):
    """
    Defines an abstract command.
    All commands should follow the APIs defined by this class.
    """

    def __init__(self, name: str, provider: Provider) -> None:
        self._name: str = name
        self._provider: Provider = provider

    def execute(self, arguments: list[str]) -> ExecutionResult:
        result = ExecutionResult(self._name)
        result.arguments = arguments
        result.config = self._config()

        data = arguments
        for action in self._pipeline():
            data = action(data)
            result.actions.append(data)
            if not data.success:
                break

        result.completed = datetime.now()
        return result

    def _map_resources(self, arguments: list[str]) -> MappingResult:
        res = MappingResult()
        res.entries = self._provider.resolve(arguments)
        res.completed = datetime.now()
        return res

    @abstractmethod
    def _config(self) -> dict[str, Any]:
        """
        The command execution configuration outlines the parameters used for the command execution.
        It primarily serves reporting purposes.
        """

    @abstractmethod
    def _pipeline(self) -> list[Action]:
        """
        The command execution pipeline defines the logic for executing the command.
        It serves as a sequence of actions that guide the execution process.
        """


class ExecutionResult:
    """
    Result of a command execution.
    """

    def __init__(self, command: str, started: datetime = None) -> None:
        self.command: str = command
        self.arguments: list[str] = []
        self.config: dict[str, Any] = {}
        self.actions: list[ActionResult] = []
        self.started: datetime = started if started else datetime.now()
        self.completed: datetime = None

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started


class Action:
    """
    A single action in the command execution pipeline.
    """

    def __init__(self, func: Callable[[Any], ActionResult]) -> None:
        self._func = func

    def __call__(self, data: Any) -> ActionResult:
        return self._func(data)


T = TypeVar("T")


class ActionResult[T](Generic[T]):
    """
    Base class for all action results.
    """

    def __init__(self, started: datetime = None):
        self.entries: T = None
        self.started: datetime = started if started else datetime.now()
        self.completed: datetime = None
        self.success: bool = True

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started


class MappingResult(ActionResult[list[Resource]]):
    pass
