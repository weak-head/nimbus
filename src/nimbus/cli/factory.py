from __future__ import annotations

import logging
from argparse import Namespace

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbus.cli.runner import CommandRunner, Runner
from nimbus.cmd import Command, CommandFactory
from nimbus.notify import NotifierFactory
from nimbus.report import ReporterFactory


class RunnerFactory:

    def __init__(
        self,
        command_fact: CommandFactory,
        reporter_fact: ReporterFactory,
        notifier_fact: NotifierFactory,
    ) -> None:
        self._command_fact = command_fact
        self._report_fact = reporter_fact
        self._notify_fact = notifier_fact

    @log_on_start(logging.DEBUG, "Building command runner")
    @log_on_end(logging.DEBUG, "Created command runner: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create command runner: {e!r}", on_exceptions=Exception)
    def create_runner(self, ns: Namespace) -> Runner:
        return CommandRunner(
            self._build_command(ns),
            self._report_fact.create_reporter(),
            self._notify_fact.create_notifier(),
        )

    def _build_command(self, ns: Namespace) -> Command:
        match ns.command:
            case "up":
                return self._command_fact.create_up(ns.selectors)
            case "down":
                return self._command_fact.create_down(ns.selectors)
            case "backup":
                return self._command_fact.create_backup(ns.selectors)
        raise ValueError("unknown command")
