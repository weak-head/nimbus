import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_error, log_on_start

from nimbus.cmd.abstract import Command
from nimbus.notification.abstract import Notifier
from nimbus.report.reporter import Reporter


class Runner(ABC):

    @abstractmethod
    def execute(self):
        pass


class CommandRunner(Runner):

    def __init__(self, cmd: Command, reporter: Reporter, notifier: Notifier) -> None:
        self._cmd = cmd
        self._reporter = reporter
        self._notifier = notifier

    def __repr__(self) -> str:
        params = [
            f"cmd='{self._cmd}'",
            f"reporter='{self._reporter}'",
            f"notifier='{self._notifier}'",
        ]
        return "CommandRunner(" + ", ".join(params) + ")"

    @log_on_start(logging.DEBUG, "Executing the command")
    @log_on_error(logging.ERROR, "Failed to execute the command: {e!r}", on_exceptions=Exception)
    def execute(self):
        result = self._cmd.execute()

        reports: list[str] = []
        if self._reporter:
            self._reporter.write(result)
            reports = self._reporter.reports

        if self._notifier:
            self._notifier.completed(result, reports)
