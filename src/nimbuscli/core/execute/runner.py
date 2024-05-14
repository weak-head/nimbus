from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class Runner(ABC):
    """
    Defines an abstract command runner.
    All runners should follow the APIs defined by this class.
    """

    @abstractmethod
    def execute(self, cmd: list[str] | str, cwd=None, env=None) -> CompletedProcess:
        """
        Execute a command.

        :param cmd: A command to execute.
            There are several ways to specify the command:
                - As a string, where each argument is separated by spaces.
                - As a list of strings, where each entry is an independent argument.

        :param cwd: Current working directory.

        :param env: Modified environment.

        :return: Result of the command execution.
        """


class CompletedProcess:

    SUCCESS = "success"
    FAILED = "failed"
    EXCEPTION = "exception"

    def __init__(self, cmd: list[str], cwd: str, env: dict[str, str]):
        self.cmd: list[str] = cmd
        self.cwd: str = cwd
        self.env: dict[str, str] = env
        self.exitcode: int = None
        self.stdout: str = None
        self.stderr: str = None
        self.exception: Exception = None
        self.started: datetime = None
        self.completed: datetime = None

    @property
    def status(self) -> str:
        if self.exception:
            return CompletedProcess.EXCEPTION
        if self.exitcode != 0:
            return CompletedProcess.FAILED
        return CompletedProcess.SUCCESS

    @property
    def success(self) -> bool:
        return all(
            [
                self.status == CompletedProcess.SUCCESS,
                self.cmd,
                self.started,
                self.completed,
            ]
        )

    @property
    def elapsed(self) -> timedelta:
        if self.started is None or self.completed is None:
            return None
        if self.started > self.completed:
            return None
        return self.completed - self.started
