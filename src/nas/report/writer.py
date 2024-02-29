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
        Write a message following the specified rules. The message can be a single
        part or composed of several parts. If the message is composed of several parts,
        each message part would be aligned and formatted according to the provided formatting rules.
        If no specific rules are given, default formatting rules will be applied.

        :param parts: One or more message parts that logically form a complete entry.

        :param rules: Message formatting and processing rules.
            These rules are used by the `Writer` to format the entire message or
            individual message parts (if the message is provided as a several parts).
            You can specify the following rules:

                - formatter: Determines formatting options for each message part.
                    The specified formatter is applied to each message part.
                    Message part is converted to a string, if the formatter cannot be applied.
                    You can provide the following formatter values:
                        * default
                        * datetime
                        * date
                        * time
                        * size
                        * speed
                        * duration

                - layout: Defines the layout of the entire massage or individual message parts.
                    Each concrete 'Writer` implementation could have it's own meaning
                    and interpretation of the layout rule. Refer to the actual implementation
                    of a particular `Writer` for the details of the layout formatting.
                    You can provide the following layout values:
                        * default
                        * multiline
                        * list
        """

    @abstractmethod
    def section(self, title: str) -> Writer:
        """
        Creates a new `Writer` that represents a nested section and serves
        as a logical grouping for message entries. All message entries written
        using the created `Writer` will be grouped under the corresponding section.
        These sections can be nested within each other for better organization.

        :param title: A title of the section.
        :return: A new instance of `Writer`, that is designated to the created section.
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
        if self._pretty.can_print(*parts):
            self._pretty.print(self._writer, *parts, **rules)
        else:
            self._writer.entry(*parts, **rules)

    def section(self, title: str) -> PrettyWriter:
        return PrettyWriter(
            self._writer.section(title),
            self._pretty,
        )
