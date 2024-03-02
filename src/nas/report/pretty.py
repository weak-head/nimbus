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
    def supported_types(self) -> tuple[type, ...]:
        return (CompletedProcess, UploadResult, ArchivalResult)

    def can_print(self, *parts) -> bool:
        return any(issubclass(part, self.supported_types) for part in parts)

    def print(self, writer: Writer, *parts, **rules) -> None:
        for part in parts:
            match part:
                case CompletedProcess():
                    self._process(writer, part)
                case UploadResult():
                    self._upload(writer, part)
                case ArchivalResult():
                    self._archive(writer, part)
                case _:
                    writer.entry(part, **rules)

    def _process(self, writer: Writer, proc: CompletedProcess, cmd=False, cwd=False, break_after=True) -> None:
        if cmd:
            writer.entry("Cmd:", (" ".join(proc.cmd)).strip())

        if cwd:
            writer.entry("Cwd:", proc.cwd)

        writer.entry("Status:", proc.status)
        writer.entry("Started:", proc.started, formatter="datetime")
        writer.entry("Completed:", proc.completed, formatter="datetime")
        writer.entry("Elapsed:", proc.elapsed, formatter="duration")

        if proc.exitcode is not None and proc.exitcode != 0:
            decoded = errno.errorcode.get(proc.exitcode, "unknown")
            writer.entry("Exit code:", f"{proc.exitcode} ({decoded})")

        if proc.stdout and proc.stdout.strip():
            stdout = writer.section("StdOut:")
            stdout.entry(proc.stdout, layout="multiline")

        if proc.stderr and proc.stderr.strip():
            stderr = writer.section("StdErr:")
            stderr.entry(proc.stderr, layout="multiline")

        if proc.exception:
            exc = writer.section("Exception:")
            exc.entry(proc.exception, layout="multiline")

        if break_after:
            writer.entry()

    def _archive(self, writer: Writer, archive: ArchivalResult, break_after=True) -> None:
        self._process(writer, archive.proc, break_after=False)

        writer.entry("Archive:", archive.archive)
        writer.entry("Archive size:", archive.size, formatter="size")
        writer.entry("Archival speed:", archive.speed, formatter="speed")

        if break_after:
            writer.entry()

    def _upload(self, writer: Writer, upload: UploadResult, break_after=True) -> None:
        writer.entry("Status:", upload.status)
        writer.entry("Started:", upload.started, formatter="datetime")
        writer.entry("Completed:", upload.completed, formatter="datetime")
        writer.entry("Elapsed:", upload.elapsed, formatter="duration")
        writer.entry("Size:", upload.size, formatter="size")
        writer.entry("Speed:", upload.speed, formatter="speed")

        if upload.exception:
            exc = writer.section("Exception:")
            exc.entry(upload.exception, layout="multiline")

        if break_after:
            writer.entry()
