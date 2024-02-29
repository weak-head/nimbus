from __future__ import annotations

import errno
import typing

from nas.core.archiver import ArchivalResult
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadResult

if typing.TYPE_CHECKING:
    from nas.report.writer import Writer


class PrettyPrinter:
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    @property
    def supported_types(self) -> tuple:
        return (CompletedProcess, UploadResult, ArchivalResult)

    def can_print(self, value: typing.Any) -> bool:
        return issubclass(value, self.supported_types)

    def print(self, writer: Writer, *parts, **rules) -> None:
        for part in parts:
            match part:
                case CompletedProcess():
                    self._process(writer, part)

                case UploadResult():
                    self._upload(writer, part)

                case ArchivalResult():
                    self._archive(writer, part)

    def _process(self, writer: Writer, proc: CompletedProcess, cmd=False, folder=False, break_after=True) -> None:
        if cmd:
            writer.entry("cmd:", (" ".join(proc.cmd)).strip())

        if folder:
            writer.entry("folder:", proc.cwd)

        writer.entry("status:", proc.status)
        writer.entry("started:", proc.started, formatter="datetime")
        writer.entry("completed:", proc.completed, formatter="datetime")
        writer.entry("elapsed:", proc.elapsed, formatter="duration")

        if proc.exitcode is not None and proc.exitcode != 0:
            decoded = errno.errorcode.get(proc.exitcode, "unknown")
            writer.entry("exit code:", f"{proc.exitcode} ({decoded})")

        if proc.stdout and proc.stdout.strip():
            stdout = writer.section("stdout:")
            stdout.entry(proc.stdout, layout="multiline")

        if proc.stderr and proc.stderr.strip():
            stderr = writer.section("stderr:")
            stderr.entry(proc.stderr, layout="multiline")

        if proc.exception:
            exc = writer.section("exception:")
            exc.entry(proc.exception, layout="multiline")

        if break_after:
            writer.entry()

    def _archive(self, writer: Writer, archive: ArchivalResult, break_after=True) -> None:
        self._process(writer, archive.proc, cmd=False, folder=False, break_after=False)

        writer.entry("archive:", archive.archive)
        writer.entry("archive size:", archive.size, formatter="size")
        writer.entry("archival speed:", archive.speed, formatter="speed")

        if break_after:
            writer.entry()

    def _upload(self, writer, upload: UploadResult, break_after=True) -> None:
        writer.entry("status:", upload.status)
        writer.entry("started:", upload.started, formatter="datetime")
        writer.entry("completed:", upload.completed, formatter="datetime")
        writer.entry("elapsed:", upload.elapsed, formatter="duration")
        writer.entry("size:", upload.size, formatter="size")
        writer.entry("speed:", upload.speed, formatter="speed")

        if upload.exception:
            exc = writer.section("exception:")
            exc.entry(upload.exception, layout="multiline")

        if break_after:
            writer.entry()
