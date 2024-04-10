from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from argparse import Namespace

from logdecorator import log_on_start

from nimbus.cmd.abstract import Command
from nimbus.factory.command import CommandFactory
from nimbus.report.reporter import Reporter


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

    @log_on_start(logging.DEBUG, "Start deployment up")
    def up(self, args: Namespace):
        self._execute(self._factory.create_up(), args.selectors)

    @log_on_start(logging.DEBUG, "Start deployment down")
    def down(self, args: Namespace):
        self._execute(self._factory.create_down(), args.selectors)

    @log_on_start(logging.DEBUG, "Start backup and upload")
    def backup(self, args: Namespace):
        self._execute(self._factory.create_backup(), args.selectors)

    def _execute(self, cmd: Command, args: list[str]):
        result = cmd.execute(args)

        if self._reporter:
            self._reporter.write(result)
