from __future__ import annotations

from typing import Any

from nas.report.pretty import PrettyPrinter
from nas.report.writer import Writer


class Report:
    """Compose operation execution report."""

    def __init__(self, writer: Writer, pretty: PrettyPrinter):
        self._writer = writer
        self._pretty = pretty

    def entry(self, key: Any, *columns, **rules):
        # Try to pretty print the entry,
        # fallback to plain writer otherwise.
        if self._pretty.can_print(key):
            self._pretty.print(self._writer, key, *columns, **rules)
        else:
            self._writer.out(key, *columns, **rules)

    def multiline(self, msg: list[str] | str, as_list=False):
        self._writer.multiline(msg, as_list=as_list)

    def section(self, title: str) -> Report:
        return Report(self._writer.section(title), self._pretty)
