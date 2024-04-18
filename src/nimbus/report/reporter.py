from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import reduce

from logdecorator import log_on_start

import nimbus.report.format as fmt
from nimbus.cmd.abstract import ExecutionResult
from nimbus.cmd.backup import (
    BackupActionResult,
    DirectoryMappingActionResult,
    UploadActionResult,
)
from nimbus.cmd.deploy import (
    CreateServicesActionResult,
    DeploymentActionResult,
    ServiceMappingActionResult,
)
from nimbus.report.writer import Writer


class Reporter(ABC):

    @abstractmethod
    def write(self, result: ExecutionResult) -> None:
        pass


class CompositeReporter(Reporter):

    def __init__(self, reporters: list[Reporter]) -> None:
        self._reporters = reporters if reporters else []

    def __repr__(self) -> str:
        params = [repr(r) for r in self._reporters]
        return "CompositeReporter(" + ", ".join(params) + ")"

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

    def __repr__(self) -> str:
        params = [
            f"writer='{self._writer!r}'",
            f"details='{self._write_details}'",
        ]
        return "ReportWriter(" + ", ".join(params) + ")"

    @log_on_start(logging.INFO, "Writing report to: [{self._writer!r}]")
    def write(self, result: ExecutionResult) -> None:
        self.header()
        self.summary(result)

        if self._write_details:
            self.details(result)

        self.footer()

    def header(self) -> None:
        self._writer.line("=" * 100)
        self._writer.line(f"== {fmt.datetime(datetime.now())}")

    def footer(self) -> None:
        self._writer.line("")
        self._writer.line("=" * 100)

    def summary(self, result: ExecutionResult) -> None:
        s = self._writer.section(f"{fmt.ch('summary')} Summary")
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

        s.row("Started", f"{fmt.ch('time')} {fmt.datetime(result.started)}")
        s.row("Completed", f"{fmt.ch('time')} {fmt.datetime(result.completed)}")
        s.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(result.elapsed)}")

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
        s = self._writer.section(f"{fmt.ch('details')} Details")

        for action in result.actions:
            match action:
                case DirectoryMappingActionResult():
                    self.details_directory_mapping(s, action)
                case BackupActionResult():
                    self.details_backup(s, action)
                case UploadActionResult():
                    self.details_upload(s, action)
                case ServiceMappingActionResult():
                    self.details_service_mapping(s, action)
                case CreateServicesActionResult():
                    self.details_create_services(s, action)
                case DeploymentActionResult():
                    self.details_deployment(s, action)
                case _:
                    pass

    def summary_directory_mapping(self, w: Writer, result: DirectoryMappingActionResult) -> None:
        groups = sorted({backup.name for backup in result.entries})
        w.row("Groups", ", ".join(groups) if groups else "[none]")

    def summary_service_deployment(self, w: Writer, result: DeploymentActionResult) -> None:
        w.row(
            "Services",
            f"[ {fmt.ch('total')} {len(result.entries)} "
            f"| {fmt.ch('ok')} {len(result.successful)} "
            f"| {fmt.ch('nok')} {len(result.failed)} ]",
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
            b = w.section(
                f"{fmt.ch('success')} Successful backups "
                f"[ {fmt.ch('size')} {fmt.size(result.total_size)} ] -- (ﾉ◕ヮ◕)ﾉ",
            )
            b.list(
                [
                    f"{fmt.ch('archive')} {name} [ {fmt.ch('size')} {size} "
                    f"| {fmt.ch('duration')} {duration} "
                    f"| {fmt.ch('speed')} {speed} ]"
                    for name, size, duration, speed in fmt.align(created, "lrrr")
                ],
                style="number",
            )

        if failed := sorted(f"{fmt.ch('folder')} {b.folder}" for b in result.entries if not b.success):
            b = w.section(f"{fmt.ch('failure')} Failed backups -- ¯\\_(ツ)_/¯")
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
            b = w.section(
                f"{fmt.ch('success')} Successful uploads "
                f"[ {fmt.ch('size')} {fmt.size(result.total_size)} ] -- (ﾉ◕ヮ◕)ﾉ"
            )
            b.list(
                [
                    f"{fmt.ch('archive')} {name} [ {fmt.ch('size')} {size} "
                    f"| {fmt.ch('duration')} {duration} "
                    f"| {fmt.ch('speed')} {speed} ]"
                    for name, size, duration, speed in fmt.align(uploaded, "lrrr")
                ],
                style="number",
            )

        if failed := sorted(
            f"{fmt.ch('archive')} {e.backup.archive.archive}" for e in result.entries if not e.success
        ):
            b = w.section(f"{fmt.ch('failure')} Failed uploads -- ¯\\_(ツ)_/¯")
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
            d = w.section(f"{fmt.ch('success')} {title} [ {fmt.ch('duration')} {fmt.duration(elapsed)} ] -- (ﾉ◕ヮ◕)ﾉ")
            d.list(
                [
                    f"{fmt.ch(kind)} {service} [ {fmt.ch('duration')} {duration} ]"
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

            d = w.section(f"{fmt.ch('failure')} {title} -- ¯\\_(ツ)_/¯")
            d.list(
                [f"{fmt.ch(kind)} {service}" for service, kind in fmt.align(failed, "lr")],
                style="number",
            )

    def details_directory_mapping(self, w: Writer, result: DirectoryMappingActionResult):
        d = w.section(f"{fmt.ch('mapping')} Mapped Directories")
        d.row("Success", f"{fmt.ch('success') if result.success else fmt.ch('failure')} {result.success}")
        d.row("Started", f"{fmt.ch('time')} {fmt.datetime(result.started)}")
        d.row("Completed", f"{fmt.ch('time')} {fmt.datetime(result.completed)}")
        d.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(result.elapsed)}")

        for group in sorted(result.entries, key=lambda e: e.name):
            g = d.section(f"Group [{group.name}]:")
            g.list((f"{fmt.ch('folder')} {v}" for v in sorted(group.directories)))

    def details_backup(self, w: Writer, result: BackupActionResult):
        d = w.section(f"{fmt.ch('backup')} Backup")
        d.row("Success", f"{fmt.ch('success') if result.success else fmt.ch('failure')} {result.success}")
        d.row("Total Size", f"{fmt.ch('size')} {fmt.size(result.total_size)}")
        d.row("Started", f"{fmt.ch('time')} {fmt.datetime(result.started)}")
        d.row("Completed", f"{fmt.ch('time')} {fmt.datetime(result.completed)}")
        d.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(result.elapsed)}")

        total_backups = len(result.entries)
        for ix, entry in enumerate(sorted(result.entries, key=lambda e: (e.group, e.folder))):
            b = d.section(f"[{ix+1}/{total_backups}] [{entry.group}] {fmt.ch('folder')} {entry.folder}")
            b.row("Success", f"{fmt.ch('success') if entry.success else fmt.ch('failure')} {entry.success}")
            b.row("Started", f"{fmt.ch('time')} {fmt.datetime(entry.archive.proc.started)}")
            b.row("Completed", f"{fmt.ch('time')} {fmt.datetime(entry.archive.proc.completed)}")
            b.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(entry.archive.proc.elapsed)}")

            if entry.archive.proc.success:
                b.row("Size", f"{fmt.ch('size')} {fmt.size(entry.archive.size)}")
                b.row("Speed", f"{fmt.ch('speed')} {fmt.speed(entry.archive.speed)}")
                b.row("Archive", f"{fmt.ch('archive')} {entry.archive.archive}")
            else:
                if entry.archive.proc.exitcode:
                    b.row("Exit Code", entry.archive.proc.exitcode)

                if entry.archive.proc.stdout:
                    s = b.section("Std Out")
                    s.list(entry.archive.proc.stdout.split("\n"))

                if entry.archive.proc.stdout:
                    s = b.section("Std Err")
                    s.list(entry.archive.proc.stderr.split("\n"))

                if entry.archive.proc.exception:
                    ex = b.section(f"{fmt.ch('exception')} Exception")
                    ex.list(fmt.wrap(str(entry.archive.proc.exception)))

    def details_upload(self, w: Writer, result: UploadActionResult):
        d = w.section(f"{fmt.ch('upload')} Upload")
        d.row("Success", f"{fmt.ch('success') if result.success else fmt.ch('failure')} {result.success}")
        d.row("Total Size", f"{fmt.ch('size')} {fmt.size(result.total_size)}")
        d.row("Started", f"{fmt.ch('time')} {fmt.datetime(result.started)}")
        d.row("Completed", f"{fmt.ch('time')} {fmt.datetime(result.completed)}")
        d.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(result.elapsed)}")

        total_uploads = len(result.entries)
        for ix, entry in enumerate(sorted(result.entries, key=lambda e: e.upload.key)):
            b = d.section(f"[{ix+1}/{total_uploads}] {fmt.ch('archive')} {entry.upload.key}")
            b.row("Success", f"{fmt.ch('success') if entry.success else fmt.ch('failure')} {entry.success}")
            b.row("Started", f"{fmt.ch('time')} {fmt.datetime(entry.upload.started)}")
            b.row("Completed", f"{fmt.ch('time')} {fmt.datetime(entry.upload.completed)}")
            b.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(entry.upload.elapsed)}")

            if entry.success:
                b.row("Size", f"{fmt.ch('size')} {fmt.size(entry.upload.size)}")
                b.row("Speed", f"{fmt.ch('speed')} {fmt.speed(entry.upload.speed)}")
                b.row("Archive", f"{fmt.ch('archive')} {entry.upload.filepath}")
            else:
                if entry.upload.exception:
                    ex = b.section(f"{fmt.ch('exception')} Exception")
                    ex.list(fmt.wrap(str(entry.upload.exception)))

            if entry.progress:
                progress = sorted(
                    (
                        fmt.datetime(e.timestamp),
                        fmt.progress(e.progress),
                        fmt.speed(e.speed),
                        fmt.duration(e.elapsed),
                    )
                    for e in entry.progress
                )
                p = b.section(f"{fmt.ch('outgoing')} Upload Progress")
                p.list(
                    [
                        f"{fmt.ch('time')} {ts} | {prog}% | {fmt.ch('speed')} {speed} | {fmt.ch('duration')} {dur}"
                        for ts, prog, speed, dur in fmt.align(progress, "rrrr")
                    ]
                )

    def details_service_mapping(self, w: Writer, result: ServiceMappingActionResult):
        s = w.section(f"{fmt.ch('mapping')} Mapped Services")
        s.row("Success", f"{fmt.ch('success') if result.success else fmt.ch('failure')} {result.success}")
        s.row("Started", f"{fmt.ch('time')} {fmt.datetime(result.started)}")
        s.row("Completed", f"{fmt.ch('time')} {fmt.datetime(result.completed)}")
        s.row("Elapsed", f"{fmt.ch('duration')} {fmt.duration(result.elapsed)}")

        mapping = sorted((e.name, e.directory, e.kind) for e in result.entries)
        g = s.section(f"{fmt.ch('service')} Services")
        g.list(
            [
                f"{fmt.ch(kind)} {name} | {fmt.ch('folder')} {directory}"
                for name, directory, kind in fmt.align(mapping, "llr")
            ],
        )

    def details_create_services(self, w: Writer, result: CreateServicesActionResult):
        pass

    def details_deployment(self, w: Writer, result: DeploymentActionResult):
        pass
