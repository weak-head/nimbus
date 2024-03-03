from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from nas.core.provider import Provider, Resources
from nas.report.writer import Writer


class Command(ABC):
    """
    Defines an abstract command.
    All commands should follow the APIs defined by this class.
    """

    def __init__(self, writer: Writer, provider: Provider):
        self._writer = writer
        self._provider = provider

    def execute(self, patterns: list[str]) -> None:
        """
        tbd
        """

        writer = self._writer.section("Command")
        writer.entry(self.info())

        if patterns:
            writer.section("Patterns").entry(*patterns, layout="list")

        resources = self._provider.resolve(patterns)
        if resources.empty:
            writer.entry("Warning", "No resolved resources, terminating the command execution.")
            return

        section = writer.section("Resources")
        for resource in resources.items:
            section.entry(resource)
        writer.entry()

        self._execute(resources)

    @abstractmethod
    def info(self) -> CommandInfo:
        """
        tbd
        """

    @abstractmethod
    def _execute(self, resources: Resources) -> None:
        """
        tbd
        """


class CommandInfo:
    def __init__(self, name: str, parameters: dict[str, Any]):
        self.name = name
        self.parameters = parameters
