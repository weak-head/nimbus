"""
Exposes structured Log writer, with support of sections and columns.
"""

from __future__ import annotations

import errno
import logging
from datetime import datetime, timedelta
from typing import Any

from nas.core.archiver import ArchivalResult
from nas.core.runner import CompletedProcess
from nas.core.uploader import UploadResult
from nas.utils.format import Formatter


class Log:
    """
    Log writer with support of:
        - indented nested sections
        - multiline messages
        - formatted columns

    Provides functionality to pretty-print execution results
    of operations defined in `nas.core` package.
    """

    def __init__(self, formatter: Formatter, indent=0, indent_size=4, indent_char=" ", column_width=40, parent=None):
        """
        Creates a new instance of `Log`.

        :param pretty: Pretty printer.
        :param formatter: Data formatter.
        :param indent: Line indent of each log entry.
        :param indent_size: Indent increase of a child logger.
        :param indent_char: Char that is used for indent.
        :param column_width: A width of each column.
        :param parent: Parent logger.
        """
        self._formatter = formatter
        self._indent = indent
        self._indent_size = indent_size
        self._indent_char = indent_char
        self._column_width = column_width
        self._parent = parent

    @property
    def pretty(self) -> Pretty:
        """
        Returns an instance of a pretty printer, that captures the current log instance and uses
        the current configuration for pretty print of complex objects.
        """
        return Pretty(self)

    def out(self, *columns, **rules) -> Log:
        """
        Write a message to the log file.
        The message could be composed as a set of values,
        with each value aligned left to the pre-configured column.

        :param columns: A set of values, that are composed as a single message.
        :keyword str format_as: Formatting rule.
        :return: `self`.
        """
        message = []
        message.append(self._indent_char * self._indent)
        offset = self._indent

        # Format and align left, to match the column width
        for entry in columns:

            # Format column value
            string_entry = self._format_entry(entry, rules.get("format_as", None))
            offset += len(string_entry)
            message.append(string_entry)

            # Fill the missing space, to align the next column
            align_size = self._column_width - (offset % self._column_width)
            message.append(self._indent_char * align_size)

            offset = 0

        logging.info("".join(message).rstrip())
        return self

    def multiline(self, msg: list[str] | str, as_list=False) -> Log:
        """
        Write a multi-line message to the log file.

        :param msg: Multi-line message, where each line is separated by `\\n` or list of strings.
        :param as_list: Should '- ' be added in front of each line.
        """

        if isinstance(msg, str):
            msg = msg.split("\n")

        for line in msg:
            if as_list:
                line = "- " + line
            self.out(line)

        return self

    def section(self, *columns) -> Log:
        """
        Create a new indented section.

        :param columns: A title of the created section.
        :return: An instance of the `Log`, with indented lines.
        """

        self.out(*columns)

        return Log(
            self._formatter,
            indent=self._indent + self._indent_size,
            indent_size=self._indent_size,
            indent_char=self._indent_char,
            column_width=self._column_width,
            parent=self,
        )

    def _format_entry(self, entry: Any, format_as: str = None) -> str:
        """
        Format log entry according to formatting rules.

        :param entry: A single entry to format.
        :param format_as: Formatting rule.
        :return: String representation of the formatted entry.
        """
        string_entry = str(entry)
        match format_as:

            case "datetime":
                if isinstance(entry, datetime):
                    string_entry = self._formatter.date_time(entry)

            case "date":
                if isinstance(entry, datetime):
                    string_entry = self._formatter.date(entry)

            case "time":
                if isinstance(entry, datetime):
                    string_entry = self._formatter.time(entry)

            case "size":
                if isinstance(entry, int):
                    string_entry = self._formatter.size(entry)

            case "speed":
                if isinstance(entry, int):
                    string_entry = self._formatter.speed(entry)

            case "duration":
                if isinstance(entry, timedelta):
                    string_entry = self._formatter.duration(entry)

        return string_entry


class Pretty:
    """
    Pretty printer that outputs to log writer complex objects, such as:
        - `CompletedProcess`
        - `ArchivalResult`
        - `UploadResult`
    """

    def __init__(self, log: Log):
        """
        Creates a new instance of `Pretty` and captures a log writter,
        that is used to pretty print complex objects.
        """
        self._log = log

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
            self._log.out("folder:", proc.working_dir)

        self._log.out("status:", proc.status)
        self._log.out("started:", proc.started, format_as="datetime")
        self._log.out("completed:", proc.completed, format_as="datetime")
        self._log.out("elapsed:", proc.elapsed, format_as="duration")

        if proc.exit_code is not None and proc.exit_code != 0:
            self._log.out("exit code:", f"{proc.exit_code} ({errno.errorcode.get(proc.exit_code, 'unknown')})")

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
        self._log.out("archive:", archive.archive_path)
        self._log.out("archive size:", archive.archive_size, format_as="size")
        self._log.out("archival speed:", archive.archival_speed, format_as="speed")

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
