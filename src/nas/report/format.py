import datetime as dt
import math
from typing import Callable, Iterator


def size(size_bytes: int) -> str:
    # Bytes
    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    # Kilobytes
    kb = int(size_bytes // 1024)
    if kb < 1024:
        return f"{ceil(kb, size_bytes)} KB"

    # Megabytes
    mb = int(kb // 1024)
    if mb < 1024:
        return f"{ceil(mb, kb)} MB"

    # Gigabytes
    gb = int(mb // 1024)
    if gb < 1024:
        return f"{ceil(gb, mb)} GB"

    # Terabytes
    tb = int(gb // 1024)
    return f"{ceil(tb, gb)} TB"


def speed(bps: int) -> str:
    # bytes/second
    if bps < 1024:
        return f"{bps} B/s"

    # KB/s
    kbps = int(bps // 1024)
    if kbps < 1024:
        return f"{ceil(kbps, bps)} KB/s"

    # MB/s
    mbps = int(kbps // 1024)
    if mbps < 1024:
        return f"{ceil(mbps, kbps)} MB/s"

    # GB/s
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


def datetime(d: dt.datetime, fmt: str = None) -> str:
    return d.strftime(fmt if fmt else "%Y-%m-%d %H:%M:%S")


def date(d: dt.datetime, fmt: str = None) -> str:
    return d.strftime(fmt if fmt else "%Y-%m-%d")


def time(t: dt.datetime, fmt: str = None) -> str:
    return t.strftime(fmt if fmt else "%H:%M:%S")


def ceil(integral: int, fractional: int) -> str:
    return f"{integral}.{math.ceil(int(fractional % 1024) / 100):1d}"


def align(entries: list[list[str]], amap: str = "l") -> Iterator[list[str]]:
    """
    Ensure that all fields in each entry of the list are left, right or center-justified.
    It is assumed that every entry contains the same number of fields, all of which are of string type.
    """
    if not entries or not amap:
        yield from entries
        return

    handlers: dict[str, Callable[[str, int], str]] = {
        "l": lambda val, ln: val.ljust(ln),
        "r": lambda val, ln: val.rjust(ln),
        "c": lambda val, ln: val.center(ln),
    }

    if len(amap) == 1:
        amap = amap * len(entries[0])

    if any(a not in handlers for a in amap) or len(amap) < len(entries[0]):
        yield from entries
        return

    entries = [[field.strip() for field in entry] for entry in entries]

    max_field_len = [
        len(max(entries, key=lambda elem, fld=entry_field: len(elem[fld]))[entry_field])
        for entry_field in range(len(entries[0]))
    ]

    for entry in entries:
        yield [handlers[amap[field]](entry[field], max_field_len[field]) for field in range(len(entry))]
