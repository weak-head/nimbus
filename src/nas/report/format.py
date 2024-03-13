import datetime as dt
import math
from typing import Any, Callable, Iterator


class Formatter:
    """
    Formats data to human readable representation.
    """

    def __init__(
        self,
        datetime_fmt: str = "%Y-%m-%d %H:%M:%S",
        date_fmt: str = "%Y-%m-%d",
        time_fmt: str = "%H:%M:%S",
    ):
        self._datetime_fmt = datetime_fmt
        self._date_fmt = date_fmt
        self._time_fmt = time_fmt

    @property
    def profiles(self) -> tuple[str, ...]:
        return ("datetime", "date", "time", "size", "speed", "duration")

    def format(self, entry: Any, profile: str) -> str:
        match profile:

            case "datetime":
                if isinstance(entry, dt.datetime):
                    return self.datetime(entry)

            case "date":
                if isinstance(entry, dt.datetime):
                    return self.date(entry)

            case "time":
                if isinstance(entry, dt.datetime):
                    return self.time(entry)

            case "size":
                if isinstance(entry, int):
                    return self.size(entry)

            case "speed":
                if isinstance(entry, int):
                    return self.speed(entry)

            case "duration":
                if isinstance(entry, dt.timedelta):
                    return self.duration(entry)

        return str(entry)

    def size(self, size_bytes: int) -> str:
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

    def speed(self, bps: int) -> str:
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

    def duration(self, elapsed: dt.timedelta) -> str:
        data = {}
        data["days"], remaining = divmod(elapsed.total_seconds(), 86_400)
        data["hours"], remaining = divmod(remaining, 3_600)
        data["minutes"], data["seconds"] = divmod(remaining, 60)

        time_parts = ((name, round(value)) for name, value in data.items())

        # Convert time parts to string, adjusting suffixes when value is '1'.
        time_parts = [f"{value} {name[:-1] if value == 1 else name}" for name, value in time_parts if value > 0]

        return " ".join(time_parts) if time_parts else "< 1 second"

    def datetime(self, d: dt.datetime) -> str:
        return d.strftime(self._datetime_fmt)

    def date(self, d: dt.datetime) -> str:
        return d.strftime(self._date_fmt)

    def time(self, t: dt.datetime) -> str:
        return t.strftime(self._time_fmt)


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
        if amap not in handlers:
            yield from entries
            return
        amap = amap * len(entries[0])
    else:
        for a in amap:
            if a not in handlers:
                yield from entries
                return

    entries = [[field.strip() for field in entry] for entry in entries]

    max_field_len = [
        len(max(entries, key=lambda elem, fld=entry_field: len(elem[fld]))[entry_field])
        for entry_field in range(len(entries[0]))
    ]

    for entry in entries:
        yield [handlers[amap[field]](entry[field], max_field_len[field]) for field in range(len(entry))]
