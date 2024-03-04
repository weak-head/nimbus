from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable

from nas.core.provider import Provider, Resources
from nas.report.writer import Writer

type ActionHandler = Callable[[Any], ActionInfo]


class Command(ABC):
    """
    Defines an abstract command.
    All commands should follow the APIs defined by this class.
    """

    def __init__(self, writer: Writer, provider: Provider):
        self._writer = writer
        self._provider = provider

    def execute(self, arguments: list[str]) -> None:
        """
        tbd
        """

        pi = self._build_pipeline(arguments)
        self._writer.entry(pi)

        if pi.resources.empty:
            return

        data = pi.resources
        for handler in pi.pipeline:
            data = handler(data)
            self._writer.entry(data)

    @abstractmethod
    def _build_pipeline(self, arguments: list[str]) -> PipelineInfo:
        """
        tbd
        """


class PipelineInfo:
    """
    tbd
    """

    def __init__(self, name: str):
        self.name: str = name
        self.pipeline: list[ActionHandler] = []
        self.config: dict[str, Any] = {}
        self.arguments: list[str] = []
        self.resources: Resources = []


class ActionInfo[T]:
    """
    Base class for all action results.
    """

    def __init__(self, started: datetime = None):
        self.entries: list[T] = []
        self.started: datetime = started
        self.completed: datetime = None

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started
