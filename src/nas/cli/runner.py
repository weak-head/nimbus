from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace

from nas.cmd.abstract import Command
from nas.factory.command import CommandFactory
from nas.report.reporter import Reporter


class Runner(ABC):

    @abstractmethod
    def up(self, args: Namespace):
        pass

    @abstractmethod
    def down(self, args: Namespace):
        pass

    @abstractmethod
    def backup(self, args: Namespace):
        pass


class CommandRunner(Runner):

    def __init__(self) -> None:
        self._factory: CommandFactory = None
        self._reporter: Reporter = None

    def run_default(self, args: Namespace):
        args.func(args)

    def set_factory(self, factory: CommandFactory) -> None:
        self._factory = factory

    def set_reporter(self, reporter: Reporter) -> None:
        self._reporter = reporter

    def up(self, args: Namespace):
        self._execute(self._factory.create_up(), args.selectors)

    def down(self, args: Namespace):
        self._execute(self._factory.create_down(), args.selectors)

    def backup(self, args: Namespace):
        self._execute(self._factory.create_backup(), args.selectors)

    def _execute(self, cmd: Command, args: list[str]):
        result = cmd.execute(args)

        if self._reporter:
            self._reporter.write(result)
