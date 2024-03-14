from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

import nas.report.format as fmt
from nas.cmd.abstract import ExecutionResult
from nas.cmd.backup import (
    BackupActionResult,
    DirectoryMappingActionResult,
    UploadActionResult,
)
from nas.cmd.deploy import DeploymentActionResult
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
        self.summary(result)
        self.details(result)
        self.footer()

    def header(self) -> None:
        self._writer.line("=" * 120)
        self._writer.line(f"== {fmt.datetime(datetime.now())}")

    def footer(self) -> None:
        self._writer.line("")
        self._writer.line("=" * 120)

    def summary(self, result: ExecutionResult) -> None:
        s = self._writer.section("Summary")
        s.row("Command", result.command)

        if result.arguments:
            s.row("Arguments", " ".join(result.arguments))

        for action in result.actions:
            if issubclass(type(action), DirectoryMappingActionResult):
                self.summary_directory_mapping(s, action)

        if result.config:
            for key, value in result.config.items():
                s.row(key, value)

        s.row("Started", fmt.datetime(result.started))
        s.row("Completed", fmt.datetime(result.completed))
        s.row("Elapsed", fmt.duration(result.elapsed))

        for action in result.actions:
            if issubclass(type(action), BackupActionResult):
                self.summary_backup(s, result.config["Destination"], action)
            elif issubclass(type(action), UploadActionResult):
                self.summary_upload(s, action)
            elif issubclass(type(action), DeploymentActionResult):
                self.summary_deploy(s, action)

    def details(self, result: ExecutionResult) -> None:
        pass

    def summary_directory_mapping(self, w: Writer, result: DirectoryMappingActionResult) -> None:
        groups = sorted({backup.name for backup in result.entries})
        w.row("Groups", ", ".join(groups) if groups else "[none]")

    def summary_backup(self, w: Writer, base: str, result: BackupActionResult) -> None:
        if created := sorted(
            (
                b.archive.archive.replace(base, "")[1:],
                fmt.size(b.archive.size),
                fmt.duration(b.archive.proc.elapsed),
                fmt.speed(b.archive.speed),
            )
            for b in result.entries
            if b.success
        ):
            b = w.section(f"-- Successful backups [ 📁 {fmt.size(result.total_size)} ] -- (ﾉ◕ヮ◕)ﾉ")
            b.list(
                [
                    f"{name} [ 📁 {size} | ⌚ {duration} | ⚡ {speed} ]"
                    for name, size, duration, speed in fmt.align(created, "lrrr")
                ],
                style="number",
            )

        if failed := sorted(b.folder for b in result.entries if not b.success):
            b = w.section("-- Failed backups -- ¯\\_(ツ)_/¯")
            b.list(failed, style="number")

    def summary_upload(self, w: Writer, result: UploadActionResult) -> None:
        pass

    def summary_deploy(self, w: Writer, result: DeploymentActionResult) -> None:
        pass
