from __future__ import annotations

import logging
import os
import subprocess
from abc import abstractmethod
from datetime import datetime

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbuscli.core.execute.runner import CompletedProcess, Runner


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
    @log_on_end(logging.DEBUG, "StdErr: {result.stderr!r}")
    @log_on_end(logging.DEBUG, "StdOut: {result.stdout!r}")
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
