import errno
from typing import Any

from nas.core.archiver import ArchivalResult
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadResult
from nas.report.writer import Writer


class PrettyPrinter:
    """
    Pretty printer that outputs to log writer complex objects, such as:
        - `CompletedProcess`
        - `ArchivalResult`
        - `UploadResult`
    """

    def __init__(self, log: Writer):
        """
        Creates a new instance of `Pretty` and captures a log writter,
        that is used to pretty print complex objects.
        """
        self._log = log

    def can_print(self, value: Any) -> bool:
        return False

    def print(self, writer: Writer, value: Any, *columns):
        pass

    def process(self, proc: CompletedProcess, cmd=True, folder=True, stdout=True, vertical_indent=True) -> None:
        """
        Pretty print the `CompletedProcess` information.

        :param process: The instance of the `CompletedProcess` to print.
        :param cmd: Should `self.cmd` be written to the `Log`.
        :param folder: Should `self.folder` be written to the `Log`.
        :param stdout: Should `self.stdout` be written to the `Log`.
        :param vertical_indent: Should empty line be written in the end.
        :return: `self`.
        """

        if cmd:
            self._log.out("cmd:", (" ".join(proc.cmd)).strip())

        if folder:
            self._log.out("folder:", proc.cwd)

        self._log.out("status:", proc.status)
        self._log.out("started:", proc.started, format_as="datetime")
        self._log.out("completed:", proc.completed, format_as="datetime")
        self._log.out("elapsed:", proc.elapsed, format_as="duration")

        if proc.exit_code is not None and proc.exitcode != 0:
            self._log.out("exit code:", f"{proc.exitcode} ({errno.errorcode.get(proc.exitcode, 'unknown')})")

        if stdout and proc.stdout and proc.stdout.strip():
            log_output = self._log.section("stdout:")
            log_output.multiline(proc.stdout)

        if proc.stderr and proc.stderr.strip():
            log_output = self._log.section("stderr:")
            log_output.multiline(proc.stderr)

        if proc.exception:
            log_output = self._log.section("exception:")
            log_output.multiline(str(proc.exception))

        if vertical_indent:
            self._log.out()

    def archive(self, archive: ArchivalResult, vertical_indent=True) -> None:
        """
        Pretty print the `ArchivalResult` information.

        :param archive: The instance of `ArchivalResult` to pretty print.
        :param vertical_indent: Should empty line be written in the end.
        :return: `self`.
        """

        # Output underlying process info
        self.process(archive.proc, cmd=False, folder=False, vertical_indent=False)

        # Output archive-specific fields
        self._log.out("archive:", archive.archive)
        self._log.out("archive size:", archive.size, format_as="size")
        self._log.out("archival speed:", archive.speed, format_as="speed")

        if vertical_indent:
            self._log.out()

    def upload(self, upload: UploadResult, vertical_indent=True) -> None:
        """
        Pretty print the `UploadResult` information.

        :param upload: The instance of `UploadResult` to pretty print.
        :param vertical_indent: Should empty line be written in the end.
        :return: `self`.
        """

        self._log.out("status:", upload.status)
        self._log.out("started:", upload.started, format_as="datetime")
        self._log.out("completed:", upload.completed, format_as="datetime")
        self._log.out("elapsed:", upload.elapsed, format_as="duration")
        self._log.out("size:", upload.size, format_as="size")
        self._log.out("speed:", upload.speed, format_as="speed")

        if upload.exception:
            log_output = self._log.section("exception:")
            log_output.multiline(str(upload.exception))

        if vertical_indent:
            self._log.out()
