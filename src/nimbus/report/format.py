import datetime as dt
import math
import textwrap
from typing import Callable, Iterator


def size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    kb = int(size_bytes // 1024)
    if kb < 1024:
        return f"{ceil(kb, size_bytes)} KB"

    mb = int(kb // 1024)
    if mb < 1024:
        return f"{ceil(mb, kb)} MB"

    gb = int(mb // 1024)
    if gb < 1024:
        return f"{ceil(gb, mb)} GB"

    tb = int(gb // 1024)
    return f"{ceil(tb, gb)} TB"


def speed(bps: int) -> str:
    if bps < 1024:
        return f"{bps} B/s"

    kbps = int(bps // 1024)
    if kbps < 1024:
        return f"{ceil(kbps, bps)} KB/s"

    mbps = int(kbps // 1024)
    if mbps < 1024:
        return f"{ceil(mbps, kbps)} MB/s"

    gbps = int(mbps // 1024)
    return f"{ceil(gbps, mbps)} GB/s"


def duration(elapsed: dt.timedelta) -> str:
    data = {}
    data["d"], remaining = divmod(elapsed.total_seconds(), 86_400)
    data["h"], remaining = divmod(remaining, 3_600)
    data["m"], data["s"] = divmod(remaining, 60)

    data = {k: round(v) for k, v in data.items()}
    for n in "dhms":
        if data[n] != 0:
            break
        del data[n]

    time_parts = [f"{v}{k}" if k == "d" else f"{v:02d}{k}" for k, v in data.items()]
    return " ".join(time_parts) if time_parts else "< 01s"


def progress(percentage: int) -> str:
    return str(percentage)


def datetime(d: dt.datetime, fmt: str = None) -> str:
    return d.strftime(fmt if fmt else "%Y-%m-%d %H:%M:%S")


def date(d: dt.datetime, fmt: str = None) -> str:
    return d.strftime(fmt if fmt else "%Y-%m-%d")


def time(t: dt.datetime, fmt: str = None) -> str:
    return t.strftime(fmt if fmt else "%H:%M:%S")


def ceil(major: int, minor: int) -> str:
    return f"{major}.{math.floor(((minor % 1024) / 1024) * 100) // 10}"


def align(entries: list[list[str]], alignment: str = "l") -> Iterator[list[str]]:
    """
    Ensure that all fields in each entry of the list are left, right,
    or center-justified. It is assumed that every entry contains the
    same number of fields, all of which are of string type.
    The alignment can be specified at either the field-level or the entry-level.
    When alignment is specified at the field-level, alignment instructions
    should be provided independently for each field.
    For entry-level alignment, it is applied uniformly to all fields within the entry.

    :param entries: A list with entries each containing one or several fields.
        Each entry in the list should contain the same number of fields,
        all of which are of string type.

    :param alignment: Specifies the alignment for the entry.
        - If a single character is used, it sets the alignment for all
          fields (entry-level).
        - When using a string of characters, each character corresponds
          to the alignment of the respective field (field-level).
        You can use the following alignment values:
            * 'l' - left alignment (text positioned along the left edge of its container).
            * 'r' - right alignment (text positioned along the right edge of its container).
            * 'c' - center alignment (text equidistant from both the left and right edges of the container).
    """
    if not entries or not alignment:
        yield from entries
        return

    handlers: dict[str, Callable[[str, int], str]] = {
        "l": lambda val, ln: val.ljust(ln),
        "r": lambda val, ln: val.rjust(ln),
        "c": lambda val, ln: val.center(ln),
    }

    if len(alignment) == 1:
        alignment = alignment * len(entries[0])

    if any(a not in handlers for a in alignment) or len(alignment) < len(entries[0]):
        yield from entries
        return

    entries = [[field.strip() for field in entry] for entry in entries]

    max_field_len = [
        len(max(entries, key=lambda elem, fld=entry_field: len(elem[fld]))[entry_field])
        for entry_field in range(len(entries[0]))
    ]

    for entry in entries:
        yield [handlers[alignment[field]](entry[field], max_field_len[field]) for field in range(len(entry))]


def wrap(line: str, width: int = 100):
    return textwrap.wrap(line, width)


def ch(kind: str) -> str:
    """
    Given a character kind, this function maps it
    to the corresponding Unicode character representation.
    """
    m = {
        # -- Reporting --
        "summary": "📄️",  # 📋
        "details": "🔍",
        "cloud": "☁️",
        "folder": "📁",
        "mapping": "🗺️",
        "backup": "💼",  # 🗂️ 📀 💿 💾 🗜️ 🗃️ 💼 ⚙️ 🔨 🔧
        "upload": "⬆️",
        "download": "⬇️",
        "exception": "⚠️",  # 🛑 ❗
        "outgoing": "📤",
        "incoming": "📥",
        "chart": "📈",  # 📉
        "service": "⚙️",
        # -- Services --
        "docker": "🐳",
        "docker-compose": "🐳",
        # -- Files --
        "link": "🔗",
        "archive": "📦",
        "save": "💾",
        "attachment": "📎",
        # -- Status --
        "total": "∑",
        "ok": "✓",
        "nok": "✗",
        "success": "👍",  # ✅ 🎉 💪 🌟 👏
        "failure": "❌",  # 👎
        # -- Security --
        "lock": "🔒",
        "lock-open": "🔓",
        "key": "🔑",
        "key-old": "🗝️",
        # -- Metrics --
        "time": "🗓️",
        # "time": "⌚",
        "duration": "⌛",
        "size": "⚖️",  # 📏
        "speed": "🚀",
    }
    return m.get(kind, kind)
