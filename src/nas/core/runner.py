"""
Provides abstract base class `Runner` for all process runners,
and implements:
  - `SubprocessRunner` - Subprocess-based runner.
"""

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class Runner(ABC):
    """Allows executing commands and getting the execution result."""

    @abstractmethod
    def execute(self, cmd: list[str] | str, working_dir=None) -> CompletedProcess:
        """
        Execute a single command and return its result.

        :param cmd: A command to execute.
        :param working_dir: Working directory.
        :return: Completed process.
        """


class SubprocessRunner(Runner):
    """Execute commands using system subprocesses."""

    def execute(self, cmd: list[str] | str, working_dir=None) -> CompletedProcess:
        """
        Execute a single command and return its result.

        :param cmd: A command to execute.
        :param working_dir: Working directory.
        :return: Completed process.
        """

        # A command could be specified as a string separated by spaces,
        # or as an array of strings.
        if isinstance(cmd, str):
            cmd = cmd.split()

        result = CompletedProcess(cmd)
        result.working_dir = working_dir
        result.started = datetime.now()

        try:

            # Execute a command as a subprocess,
            # capturing STDOUT and STDERR output.
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                text=True,
                check=False,
                cwd=working_dir,
            )

            result.exit_code = process.returncode

            if process.stdout is not None:
                result.stdout = process.stdout.strip()

            if process.stderr is not None:
                result.stderr = process.stderr.strip()

        except (FileNotFoundError, subprocess.SubprocessError) as e:
            result.exception = e

        result.completed = datetime.now()
        return result


class CompletedProcess:
    """Result of a command execution."""

    SUCCESS = "success"
    """The process has successfully finished (exit code is 0)."""

    FAILED = "failed"
    """The process has finished with errors (exit code is not 0)."""

    EXCEPTION = "exception"
    """Unexpected exception has been generated."""

    def __init__(self, cmd: list[str]):
        """
        Creates a new instance of `CompletedProcess`, with empty values.

        :param cmd: A command, that has been executed.
        """

        self.cmd = cmd
        """The command, that has been executed as a process."""

        self.working_dir = None
        """Process working directory."""

        self.exit_code = None
        """Process exit code."""

        self.stdout = None
        """Process STDOUT output."""

        self.stderr = None
        """Process STDERR output."""

        self.exception = None
        """The generated exception, or `None`."""

        self.started = None
        """Process start time, as `datetime`."""

        self.completed = None
        """Process completion time, as `datetime`."""

    @property
    def status(self) -> str:
        """Process execution status."""
        if self.exception:
            return CompletedProcess.EXCEPTION
        if self.exit_code != 0:
            return CompletedProcess.FAILED
        return CompletedProcess.SUCCESS

    @property
    def successful(self) -> bool:
        """True, if the process has finished successfully."""
        return self.status == CompletedProcess.SUCCESS and self.cmd and self.started and self.completed

    @property
    def elapsed(self) -> timedelta:
        """Process elapsed time, as `timedelta`."""
        return self.completed - self.started
