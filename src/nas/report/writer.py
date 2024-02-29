from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from nas.report.format import Formatter
from nas.report.pretty import PrettyPrinter


class Writer(ABC):
    """
    Defines an abstract message writer.
    All writers should follow the APIs defined by this class.
    """

    @abstractmethod
    def entry(self, *parts, **rules) -> None:
        """
        Write a message. If the message is provided as a several message parts,
        the message parts are aligned and formatted according to the provided rules.
        If no rules are provided, the default formatting rules are used.

        :param parts: One or several values of any type that logically compose
            a single message entry and should be written as a whole.

        :param rules: Message formatting and processing rules.
            These rules are used by the `Writer` to format the entire message or
            a particular part of the message (if the message is provided as a several parts).
            You can specify the following rules:

                - formatter: Defines the message formatting options. The formatter
                    is applied to each message part independently.
                    You can provide the following values:
                        * default
                        * datetime
                        * date
                        * time
                        * size
                        * speed
                        * duration

                - layout: Defines the layout of the massage or individual message parts.
                    You can provide the following values:
                        * default
                        * multiline
                        * list
        """

    @abstractmethod
    def section(self, title: str) -> Writer:
        """
        Create a new section.

        :param title: A title of the section.
        :return: `Writer` that writes messages to the created section.
        """


class LogWriter(Writer):
    """
    Writer that uses `logging` package.
    """

    def __init__(
        self,
        formatter: Formatter,
        indent: int = 0,
        indent_size: int = 4,
        indent_char: str = " ",
        column_width: int = 40,
        parent: LogWriter = None,
    ):
        self._formatter: Formatter = formatter
        self._indent: int = indent
        self._indent_size: int = indent_size
        self._indent_char: str = indent_char
        self._column_width: int = column_width
        self._parent: LogWriter = parent

    def entry(self, *parts, **rules):
        # Layout rules completely alter the
        # message layout for this writer.
        match rules.get("layout", "default"):
            case "default":
                self._entry(*parts, **rules)
            case "multiline":
                for part in parts:
                    for msg in part.split("\n"):
                        self._entry(msg, **rules)
            case "list":
                rules["_prepend"] = "- "
                for part in parts:
                    self._entry(part, **rules)

    def _entry(self, *parts, **rules):
        message = []
        message.append(self._indent_char * self._indent)
        offset = self._indent

        prepend = rules.get("_prepend", "")
        formatter = rules.get("formatter", "default")

        # Format and align each message part,
        # to match the configured width
        for entry in parts:
            string_entry = prepend + self._formatter.format(entry, formatter)
            offset += len(string_entry)
            message.append(string_entry)

            # Fill the missing space, to align the next column
            align_size = self._column_width - (offset % self._column_width)
            message.append(self._indent_char * align_size)

            offset = 0

        logging.info("".join(message).rstrip())

    def section(self, title: str) -> LogWriter:
        self.entry(title)

        return LogWriter(
            self._formatter,
            indent=self._indent + self._indent_size,
            indent_size=self._indent_size,
            indent_char=self._indent_char,
            column_width=self._column_width,
            parent=self,
        )


class PrettyWriter(Writer):
    """
    Writer decorator that uses `PrettyPrinter` to write prettified messages.
    """

    def __init__(self, writer: Writer, pretty: PrettyPrinter):
        self._writer = writer
        self._pretty = pretty

    def entry(self, *parts, **rules):
        # Try to pretty print the entry,
        # fallback to the decorated writer on failure.
        if self._pretty.can_print(parts[0]):
            self._pretty.print(self._writer, *parts, **rules)
        else:
            self._writer.entry(*parts, **rules)

    def section(self, title: str) -> PrettyWriter:
        return PrettyWriter(
            self._writer.section(title),
            self._pretty,
        )
