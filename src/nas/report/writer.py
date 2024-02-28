"""
Exposes structured Log writer, with support of sections and columns.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from nas.report.format import Formatter


class Writer(ABC):
    """
    Defines an abstract writer.
    All writers should follow the APIs defined by this class.
    """

    @abstractmethod
    def out(self, *columns, **rules) -> None:
        """
        Write a message to the log file.
        The message could be composed as a set of values,
        with each value aligned left to the pre-configured column.

        :param columns: A set of values, that are composed as a single message.
        :keyword str format_as: Formatting rule.
        """

    @abstractmethod
    def multiline(self, msg: list[str] | str, as_list=False) -> None:
        """
        Write a multi-line message to the log file.

        :param msg: Multi-line message, where each line is separated by `\\n` or list of strings.
        :param as_list: Should '- ' be added in front of each line.
        """

    @abstractmethod
    def section(self, title: str) -> Writer:
        """
        Create a new indented section.

        :param columns: A title of the created section.
        :return: An instance of the `Log`, with indented lines.
        """


class LogWriter(Writer):
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

    # @property
    # def pretty(self) -> PrettyPrinter:
    #     """
    #     Returns an instance of a pretty printer, that captures the current log instance and uses
    #     the current configuration for pretty print of complex objects.
    #     """
    #     return PrettyPrinter(self)

    def out(self, *columns, **rules):
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

    def multiline(self, msg: list[str] | str, as_list=False):
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

    def section(self, *columns) -> LogWriter:
        """
        Create a new indented section.

        :param columns: A title of the created section.
        :return: An instance of the `Log`, with indented lines.
        """

        self.out(*columns)

        return LogWriter(
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
