from __future__ import annotations

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from logdecorator import log_on_end, log_on_error, log_on_start


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


class ProcessRunner(Runner):
    """
    Executes a command.
    """

    def execute(self, cmd: list[str] | str, cwd=None, env=None) -> CompletedProcess:
        if isinstance(cmd, str):
            cmd = cmd.split()

        env = {**os.environ, **env} if env else os.environ
        result = CompletedProcess(cmd, cwd, env)
        result.started = datetime.now()

        try:
            process = self._run(cmd, cwd, env)
            result.exitcode = process.returncode

            if process.stdout is not None:
                result.stdout = process.stdout.strip()

            if process.stderr is not None:
                result.stderr = process.stderr.strip()

        except Exception as e:  # pylint: disable=broad-exception-caught
            result.exception = e

        result.completed = datetime.now()
        return result

    @abstractmethod
    def _run(self, cmd: list[str], cwd: str, env: dict[str, str]):
        """
        Execute a command using a processes runner.
        """


class SubprocessRunner(ProcessRunner):
    """
    Executes a command as a subprocess.
    """

    def __repr__(self) -> str:
        return "SubprocessRunner()"

    @log_on_start(logging.DEBUG, "Execute {cmd!s}; cwd: {cwd!s}")
    @log_on_end(logging.DEBUG, "Exit code: {result.returncode!s}")
    @log_on_error(logging.ERROR, "Failed to execute: {e!r}", on_exceptions=Exception)
    def _run(self, cmd: list[str], cwd: str, env: dict[str, str]):
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
            env=env,
        )


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
