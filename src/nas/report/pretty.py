from __future__ import annotations

import errno
from typing import Any, Callable

from nas.cmd.backup import BackupActionResult, UploadActionResult
from nas.core.archiver import ArchivalStatus
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadStatus
from nas.provider.abstract import DirectoryResource
from nas.report.writer import Writer


class PrettyPrinter:
    """
    Knows an internal structure of the core objects and outputs them to `Writer`.
    """

    def can_print(self, *parts) -> bool:
        types = tuple(self._types.keys())
        return any(issubclass(part, types) for part in parts)

    def print(self, writer: Writer, *parts, **rules) -> None:
        for part in parts:
            if type(part) in self._types:
                self._types[type(part)](writer, part)
            else:
                writer.entry(part, **rules)

    @property
    def _types(self) -> dict[type, Callable[[Writer, Any], None]]:
        return {
            CompletedProcess: self._process,
            UploadStatus: self._upload_status,
            ArchivalStatus: self._archive_status,
            BackupActionResult: self._backup_action_result,
            UploadActionResult: self._upload_action_result,
            DirectoryResource: self._directory_resource,
        }

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

    def _directory_resource(self, writer: Writer, resource: DirectoryResource) -> None:
        pass
