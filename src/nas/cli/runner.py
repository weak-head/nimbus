from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace

from nas.cmd.abstract import Command
from nas.factory.command import CommandFactory


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

    def run_default(self, args: Namespace):
        args.func(args)

    def set_factory(self, factory: CommandFactory) -> None:
        self._factory = factory

    def up(self, args: Namespace):
        self._execute(self._factory.create_up(), args)

    def down(self, args: Namespace):
        self._execute(self._factory.create_down(), args)

    def backup(self, args: Namespace):
        self._execute(self._factory.create_backup(), args)

    def _execute(self, cmd: Command, args: Namespace):
        cmd.execute(args)
