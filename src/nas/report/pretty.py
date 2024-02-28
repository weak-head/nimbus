import errno
from typing import Any

from nas.core.archiver import ArchivalResult
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadResult
from nas.report.writer import Writer


class PrettyPrinter:
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    @property
    def supported_types(self) -> tuple:
        return (CompletedProcess, UploadResult, ArchivalResult)

    def can_print(self, value: Any) -> bool:
        return issubclass(value, self.supported_types)

    def print(self, writer: Writer, value: Any, *columns, **rules) -> None:
        match value:
            case CompletedProcess():
                self._process(writer, value)

            case UploadResult():
                self._upload(writer, value)

            case ArchivalResult():
                self._archive(writer, value)

    def _process(self, writer: Writer, proc: CompletedProcess, cmd=False, folder=False, break_after=True) -> None:
        if cmd:
            writer.out("cmd:", (" ".join(proc.cmd)).strip())

        if folder:
            writer.out("folder:", proc.cwd)

        writer.out("status:", proc.status)
        writer.out("started:", proc.started, format_as="datetime")
        writer.out("completed:", proc.completed, format_as="datetime")
        writer.out("elapsed:", proc.elapsed, format_as="duration")

        if proc.exitcode is not None and proc.exitcode != 0:
            decoded = errno.errorcode.get(proc.exitcode, "unknown")
            writer.out("exit code:", f"{proc.exitcode} ({decoded})")

        if proc.stdout and proc.stdout.strip():
            stdout = writer.section("stdout:")
            stdout.multiline(proc.stdout)

        if proc.stderr and proc.stderr.strip():
            stderr = writer.section("stderr:")
            stderr.multiline(proc.stderr)

        if proc.exception:
            exc = writer.section("exception:")
            exc.multiline(str(proc.exception))

        if break_after:
            writer.out()

    def _archive(self, writer: Writer, archive: ArchivalResult, break_after=True) -> None:
        self._process(writer, archive.proc, cmd=False, folder=False, break_after=False)

        writer.out("archive:", archive.archive)
        writer.out("archive size:", archive.size, format_as="size")
        writer.out("archival speed:", archive.speed, format_as="speed")

        if break_after:
            writer.out()

    def _upload(self, writer: Writer, upload: UploadResult, break_after=True) -> None:
        writer.out("status:", upload.status)
        writer.out("started:", upload.started, format_as="datetime")
        writer.out("completed:", upload.completed, format_as="datetime")
        writer.out("elapsed:", upload.elapsed, format_as="duration")
        writer.out("size:", upload.size, format_as="size")
        writer.out("speed:", upload.speed, format_as="speed")

        if upload.exception:
            exc = writer.section("exception:")
            exc.multiline(str(upload.exception))

        if break_after:
            writer.out()
