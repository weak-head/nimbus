from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from argparse import Namespace

from logdecorator import log_on_start

from nimbus.cmd.abstract import Command
from nimbus.factory.command import CommandFactory
from nimbus.factory.notification import NotifierFactory
from nimbus.factory.report import ReporterFactory


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
        self._command_fact: CommandFactory = None
        self._report_fact: ReporterFactory = None
        self._notify_fact: NotifierFactory = None

    def configure(
        self,
        command_fact: CommandFactory,
        reporter_fact: ReporterFactory,
        notifier_fact: NotifierFactory,
    ) -> None:
        self._command_fact = command_fact
        self._report_fact = reporter_fact
        self._notify_fact = notifier_fact

    def run_default(self, args: Namespace):
        args.func(args)

    @log_on_start(logging.DEBUG, "Start deployment up")
    def up(self, args: Namespace):
        self._execute(self._command_fact.create_up(), args.selectors)

    @log_on_start(logging.DEBUG, "Start deployment down")
    def down(self, args: Namespace):
        self._execute(self._command_fact.create_down(), args.selectors)

    @log_on_start(logging.DEBUG, "Start backup and upload")
    def backup(self, args: Namespace):
        self._execute(self._command_fact.create_backup(), args.selectors)

    def _execute(self, cmd: Command, args: list[str]):
        result = cmd.execute(args)

        if reporter := self._report_fact.create_reporter():
            reporter.write(result)

        if notifier := self._notify_fact.create_notifier():
            notifier.completed(result)
