from __future__ import annotations

import errno
from abc import ABC, abstractmethod
from datetime import datetime

from nas.cmd.abstract import ExecutionResult
from nas.cmd.backup import BackupActionResult, UploadActionResult
from nas.core.archiver import ArchivalStatus
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadStatus
from nas.report.writer import Writer


class Reporter(ABC):

    @abstractmethod
    def write(self, result: ExecutionResult) -> None:
        pass


class ReportWriter(Reporter):
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    def __init__(self, writer: Writer) -> None:
        self._writer = writer

    def write(self, result: ExecutionResult) -> None:
        self.header()

        self.space()
        self.summary(result)

        self.space()
        self.details(result)

        self.footer()

    def space(self) -> None:
        self._writer.entry("")

    def header(self) -> None:
        self._writer.entry("=" * 80)
        self._writer.entry(f'== {datetime.today().strftime("%Y-%m-%d %H:%M:%S")}')

    def footer(self) -> None:
        self._writer.entry("=" * 80)

    def summary(self, result: ExecutionResult) -> None:
        s = self._writer.section("Summary")
        s.entry("Command", result.command)
        s.entry("Arguments", (" ".join(result.arguments)).strip())

        if result.config:
            cfg = s.section("Configuration")
            for key, value in result.config.items():
                cfg.entry(key, value)

        s.entry("Started", result.started, formatter="datetime")
        s.entry("Completed", result.completed, formatter="datetime")
        s.entry("Elapsed", result.elapsed, formatter="duration")

    def details(self, result: ExecutionResult) -> None:
        pass

    def _process(self, writer: Writer, proc: CompletedProcess, cmd=False, cwd=False, break_after=True) -> None:
        if cmd:
            writer.entry("Cmd", (" ".join(proc.cmd)).strip())

        if cwd:
            writer.entry("Cwd", proc.cwd)

        writer.entry("Status", proc.status)
        writer.entry("Started", proc.started, formatter="datetime")
        writer.entry("Completed", proc.completed, formatter="datetime")
        writer.entry("Elapsed", proc.elapsed, formatter="duration")

        if proc.exitcode is not None and proc.exitcode != 0:
            decoded = errno.errorcode.get(proc.exitcode, "unknown")
            writer.entry("Exit code", f"{proc.exitcode} ({decoded})")

        if proc.stdout and proc.stdout.strip():
            stdout = writer.section("StdOut")
            stdout.entry(proc.stdout, layout="multiline")

        if proc.stderr and proc.stderr.strip():
            stderr = writer.section("StdErr")
            stderr.entry(proc.stderr, layout="multiline")

        if proc.exception:
            exc = writer.section("Exception")
            exc.entry(proc.exception, layout="multiline")

        if break_after:
            writer.entry()

    def _archive_status(self, writer: Writer, archive: ArchivalStatus, break_after=True) -> None:
        self._process(writer, archive.proc, break_after=False)

        writer.entry("Archive", archive.archive)
        writer.entry("Archive size", archive.size, formatter="size")
        writer.entry("Archival speed", archive.speed, formatter="speed")

        if break_after:
            writer.entry()

    def _upload_status(self, writer: Writer, upload: UploadStatus, break_after=True) -> None:
        writer.entry("Status", upload.status)
        writer.entry("Started", upload.started, formatter="datetime")
        writer.entry("Completed", upload.completed, formatter="datetime")
        writer.entry("Elapsed", upload.elapsed, formatter="duration")
        writer.entry("Size", upload.size, formatter="size")
        writer.entry("Speed", upload.speed, formatter="speed")

        if upload.exception:
            exc = writer.section("Exception")
            exc.entry(upload.exception, layout="multiline")

        if break_after:
            writer.entry()

    def _backup_action_result(self, writer: Writer, backups: BackupActionResult) -> None:
        pass

    def _upload_action_result(self, writer: Writer, uploads: UploadActionResult) -> None:
        pass
