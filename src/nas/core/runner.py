from __future__ import annotations

import os
import subprocess
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


class SubprocessRunner(Runner):
    """
    Executes a command as a subprocess.
    """

    def execute(self, cmd: list[str] | str, cwd=None, env=None) -> CompletedProcess:
        if isinstance(cmd, str):
            cmd = cmd.split()

        env = {**os.environ, **env} if env else os.environ
        result = CompletedProcess(cmd, cwd, env)
        result.started = datetime.now()

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=cwd, env=env)
            result.exitcode = process.returncode

            if process.stdout is not None:
                result.stdout = process.stdout.strip()

            if process.stderr is not None:
                result.stderr = process.stderr.strip()

        except (FileNotFoundError, subprocess.SubprocessError) as e:
            result.exception = e

        result.completed = datetime.now()
        return result


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
        return self.status == CompletedProcess.SUCCESS and self.cmd and self.started and self.completed

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started
