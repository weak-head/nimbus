from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class Command(ABC):
    """
    Defines an abstract command.
    All commands should follow the APIs defined by this class.
    """

    def __init__(self, name: str, arguments: list[str] = None) -> None:
        """
        Creates a command with a given name. A first action in the pipeline
        would be executed with the provided arguments.
        """
        self._name: str = name
        self._args: list[str] = arguments

    def execute(self) -> ExecutionResult:
        result = ExecutionResult(self._name)
        result.arguments = self._args
        result.config = self._config()

        data = self._args
        for action in self._pipeline():
            data = action(data)
            result.actions.append(data)
            if not data.success:
                break

        result.completed = datetime.now()
        return result

    @abstractmethod
    def _config(self) -> dict[str, Any]:
        """
        The command execution configuration outlines
        the parameters used for the command execution.
        It primarily serves reporting purposes.
        """

    @abstractmethod
    def _pipeline(self) -> list[Action]:
        """
        The command execution pipeline defines the logic
        for executing the command. It serves as a sequence of
        actions that guide the execution process.
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

    @property
    def success(self) -> bool:
        return all(a.success for a in self.actions)


class Action:
    """
    A single action in the command execution pipeline.
    """

    def __init__(self, func: Callable[[Any], ActionResult]) -> None:
        self._func = func

    def __call__(self, data: Any) -> ActionResult:
        started = datetime.now()
        ar = self._func(data)
        ar.started = started
        ar.completed = datetime.now()
        return ar

    def __repr__(self) -> str:
        return self._func.__name__


class ActionResult(Generic[T]):
    """
    Base class for all action results.
    """

    def __init__(self, entries: T = None):
        self.entries: T = entries
        self.started: datetime = None
        self.completed: datetime = None

    def __str__(self) -> str:
        return "[" + ", ".join(str(entry) for entry in self.entries) + "]"

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started

    @property
    def success(self) -> bool:
        return True
