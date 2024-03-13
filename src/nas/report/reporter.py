from __future__ import annotations

import errno
from abc import ABC, abstractmethod
from datetime import datetime

from nas.cmd.abstract import ExecutionResult
from nas.cmd.backup import BackupActionResult, UploadActionResult
from nas.cmd.deploy import DeploymentActionResult
from nas.core.archiver import ArchivalStatus
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadStatus
from nas.report.format import Formatter, align
from nas.report.writer import Writer


class Reporter(ABC):

    @abstractmethod
    def write(self, result: ExecutionResult) -> None:
        pass


class ReportWriter(Reporter):
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    def __init__(self, writer: Writer, formatter: Formatter) -> None:
        self._writer = writer
        self._formatter = formatter

    def write(self, result: ExecutionResult) -> None:
        self.header()
        self.summary(result)
        self.details(result)
        self.footer()

    def header(self) -> None:
        self._writer.line("=" * 120)
        self._writer.line(f"== {self._formatter.datetime(datetime.now())}")

    def footer(self) -> None:
        self._writer.line("")
        self._writer.line("=" * 120)

    def summary(self, result: ExecutionResult) -> None:
        s = self._writer.section("Summary")
        s.row("Command", result.command)
        s.row("Started", self._formatter.datetime(result.started))
        s.row("Completed", self._formatter.datetime(result.completed))
        s.row("Elapsed", self._formatter.duration(result.elapsed))

        if result.arguments:
            arg = s.section("Arguments")
            arg.list(result.arguments, style="bullet")

        if result.config:
            cfg = s.section("Configuration")
            for key, value in result.config.items():
                cfg.row(key, value)

        for action in result.actions:
            if issubclass(type(action), BackupActionResult):
                self.summary_backups(s, result.config["Destination"], action)
            elif issubclass(type(action), UploadActionResult):
                self.summary_upload(s, action)
            elif issubclass(type(action), DeploymentActionResult):
                self.summary_deploy(s, action)

    def summary_backups(self, w: Writer, base: str, result: BackupActionResult) -> None:
        if created := sorted(
            (
                b.archive.archive.replace(base, "")[1:],
                self._formatter.size(b.archive.size),
                self._formatter.duration(b.archive.proc.elapsed),
                self._formatter.speed(b.archive.speed),
            )
            for b in result.entries
            if b.success
        ):
            total_size = self._formatter.size(sum(b.archive.size for b in result.entries if b.success))
            b = w.section(f"-- Successful backups [ 📁 {total_size} ] -- (ﾉ◕ヮ◕)ﾉ")

            created = [f"{name} [ 📁 {size} | ⌚ {dur} | ⚡ {sp} ]" for name, size, dur, sp in align(created, "lrrr")]
            b.list(created, style="number")

        if failed := sorted(b.folder for b in result.entries if not b.success):
            b = w.section("-- Failed backups -- ¯\\_(ツ)_/¯")
            b.list(failed, style="number")

    def summary_upload(self, w: Writer, result: UploadActionResult) -> None:
        pass

    def summary_deploy(self, w: Writer, result: DeploymentActionResult) -> None:
        pass

    def details(self, result: ExecutionResult) -> None:
        pass

    def _process(self, writer: Writer, proc: CompletedProcess, cmd=False, cwd=False, break_after=True) -> None:
        if cmd:
            writer.entry("Cmd", (" ".join(proc.cmd)).strip())

        if cwd:
            writer.entry("Cwd", proc.cwd)

        writer.entry("Status", proc.status)
        writer.entry("Started", self._formatter.datetime(proc.started))
        writer.entry("Completed", self._formatter.datetime(proc.completed))
        writer.entry("Elapsed", self._formatter.duration(proc.elapsed))

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
