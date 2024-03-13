from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath


class Writer(ABC):
    """
    Defines an abstract message writer.
    All writers should follow the APIs defined by this class.
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

    @abstractmethod
    def line(self, msg: str) -> None:
        """
        Write a message. The content can be a single line of text or span multiple lines,
        each separated by a newline character. If the message consists of several lines,
        ensure that each line adheres to the expected formatting guidelines set by the writer.

        :param msg: A text that span one or multiple lines.
        """

    @abstractmethod
    def row(self, columns: list[str]) -> None:
        """
        Create a row consisting of multiple columns. Each column is aligned
        according to the formatting guidelines specified by the writer.

        :param columns: Several columns that logically form a complete row.
        """

    @abstractmethod
    def list(self, entries: list[str], style: str = None) -> None:
        """
        Outputs a list of strings, which can be formatted as either
        a numbered list or a bullet list. Ensure that the alignment
        adheres to the specified formatting guidelines provided by the writer.

        :param entries: A list containing one or more strings for output.

        :param style: The presentation style of the list.
            You can specify the following values:
                - bullet
                - number
        """


class TextWriter(Writer):
    """
    Writer that outputs a plain text file.
    """

    def __init__(
        self,
        file: FileDescriptorOrPath,
        indent: int = 0,
        indent_size: int = 4,
        indent_char: str = " ",
        column_width: int = 40,
    ):
        self._file: FileDescriptorOrPath = file
        self._indent: int = indent
        self._indent_size: int = indent_size
        self._indent_char: str = indent_char
        self._column_width: int = column_width

    def section(self, title: str) -> TextWriter:
        self.line(title)

        return TextWriter(
            self._file,
            indent=self._indent + self._indent_size,
            indent_size=self._indent_size,
            indent_char=self._indent_char,
            column_width=self._column_width,
        )

    def line(self, msg: str) -> None:
        for single_line in msg.split("\n"):
            self._entry([single_line])

    def row(self, *columns) -> None:
        self._entry(columns)

    def list(self, entries: list[str], style: str = None) -> None:
        prepend = ""
        for ix, entry in enumerate(entries):
            match style:
                case "bullet":
                    prepend = "- "
                case "number":
                    prepend = f"{ix+1}. " if len(entries) < 10 else f"{ix+1:02d}. "
            self._entry([prepend + entry])

    def _entry(self, parts: list[str]):
        message = []
        message.append(self._indent_char * self._indent)
        offset = self._indent

        # Format and align each message part,
        # to match the configured width
        for entry in parts:
            str_entry = str(entry)
            offset += len(str_entry)
            message.append(str_entry)

            # Fill the missing space, to align the next column
            align_size = self._column_width - (offset % self._column_width)
            message.append(self._indent_char * align_size)

            offset = 0

        with open(self._file, mode="a", encoding="utf-8") as file:
            file.write("".join(message).rstrip() + "\n")
