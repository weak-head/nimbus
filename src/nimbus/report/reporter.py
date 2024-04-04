from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import reduce

import nimbus.report.format as fmt
from nimbus.cmd.abstract import ExecutionResult
from nimbus.cmd.backup import (
    BackupActionResult,
    DirectoryMappingActionResult,
    UploadActionResult,
)
from nimbus.cmd.deploy import DeploymentActionResult
from nimbus.report.writer import Writer


class Reporter(ABC):

    @abstractmethod
    def write(self, result: ExecutionResult) -> None:
        pass


class CompositeReporter(Reporter):

    def __init__(self, reporters: list[Reporter]) -> None:
        self._reporters = reporters if reporters else []

    def write(self, result: ExecutionResult) -> None:
        for reporter in self._reporters:
            reporter.write(result)


class ReportWriter(Reporter):
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    def __init__(self, writer: Writer, details: bool = True) -> None:
        self._writer = writer
        self._write_details = details

    def write(self, result: ExecutionResult) -> None:
        self.header()
        self.summary(result)

        if self._write_details:
            self.details(result)

        self.footer()

    def header(self) -> None:
        self._writer.line("=" * 80)
        self._writer.line(f"== {fmt.datetime(datetime.now())}")

    def footer(self) -> None:
        self._writer.line("")
        self._writer.line("=" * 80)

    def summary(self, result: ExecutionResult) -> None:
        s = self._writer.section("Summary")
        s.row("Command", result.command)

        if result.arguments:
            s.row("Arguments", " ".join(result.arguments))

        for action in result.actions:
            match action:
                case DirectoryMappingActionResult():
                    self.summary_directory_mapping(s, action)
                case DeploymentActionResult():
                    self.summary_service_deployment(s, action)
                case _:
                    pass

        if result.config:
            for key, value in result.config.items():
                s.row(key, value)

        s.row("Started", fmt.datetime(result.started))
        s.row("Completed", fmt.datetime(result.completed))
        s.row("Elapsed", fmt.duration(result.elapsed))

        for action in result.actions:
            match action:
                case BackupActionResult():
                    self.summary_backup(s, result.config["Destination"], action)
                case UploadActionResult():
                    self.summary_upload(s, action)
                case DeploymentActionResult():
                    self.summary_deploy(s, action)
                case _:
                    pass

    def details(self, result: ExecutionResult) -> None:
        pass

    def summary_directory_mapping(self, w: Writer, result: DirectoryMappingActionResult) -> None:
        groups = sorted({backup.name for backup in result.entries})
        w.row("Groups", ", ".join(groups) if groups else "[none]")

    def summary_service_deployment(self, w: Writer, result: DeploymentActionResult) -> None:
        w.row(
            "Services",
            f"[ ∑ {len(result.entries)} | ✔ {len(result.successful)} | ✘ {len(result.failed)} ]",
        )

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
        if uploaded := sorted(
            (
                e.upload.key,
                fmt.size(e.upload.size),
                fmt.duration(e.upload.elapsed),
                fmt.speed(e.upload.speed),
            )
            for e in result.entries
            if e.success
        ):
            b = w.section(f"-- Successful uploads [ 📁 {fmt.size(result.total_size)} ] -- (ﾉ◕ヮ◕)ﾉ")
            b.list(
                [
                    f"{name} [ 📁 {size} | ⌚ {duration} | ⚡ {speed} ]"
                    for name, size, duration, speed in fmt.align(uploaded, "lrrr")
                ],
                style="number",
            )

        if failed := sorted(e.backup.archive.archive for e in result.entries if not e.success):
            b = w.section("-- Failed uploads -- ¯\\_(ツ)_/¯")
            b.list(failed, style="number")

    def summary_deploy(self, w: Writer, result: DeploymentActionResult) -> None:
        if processed := sorted((d.service, d.kind, fmt.duration(d.elapsed)) for d in result.successful):
            title = None
            match result.operation:
                case "Up":
                    title = "Successfully deployed"
                case "Down":
                    title = "Successfully stopped"

            elapsed = reduce(lambda a, b: a + b.elapsed, result.successful, timedelta())
            d = w.section(f"-- {title} [ ⌚ {fmt.duration(elapsed)} ] -- (ﾉ◕ヮ◕)ﾉ")
            d.list(
                [
                    f"{service} [ {fmt.srv_ch(kind)} {kind} | ⌚ {duration} ]"
                    for service, kind, duration in fmt.align(processed, "lrr")
                ],
                style="number",
            )

        if failed := sorted((d.service, d.kind) for d in result.failed):
            title = None
            match result.operation:
                case "Up":
                    title = "Failed to deploy"
                case "Down":
                    title = "Failed to stop"

            d = w.section(f"-- {title} -- ¯\\_(ツ)_/¯")
            d.list(
                [f"{service} [ {fmt.srv_ch(kind)} {kind} ]" for service, kind in fmt.align(failed, "lr")],
                style="number",
            )