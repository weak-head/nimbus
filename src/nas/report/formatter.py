import datetime as dt
import math
from typing import Any


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
            return f"{kb} KB"

        # Megabytes
        mb = int(kb // 1024)
        if mb < 1024:
            return f"{_ceil(mb, kb)} MB"

        # Gigabytes
        gb = int(mb // 1024)
        if gb < 1024:
            return f"{_ceil(gb, mb)} GB"

        # Terabytes
        tb = int(gb // 1024)
        return f"{_ceil(tb, gb)} TB"

    def speed(self, bps: int) -> str:
        # bytes/second
        if bps < 1024:
            return f"{bps} bytes/second"

        # KB/s
        kbps = int(bps // 1024)
        if kbps < 1024:
            return f"{_ceil(kbps, bps)} KB/s"

        # MB/s
        mbps = int(kbps // 1024)
        if mbps < 1024:
            return f"{_ceil(mbps, kbps)} MB/s"

        # GB/s
        gbps = int(mbps // 1024)
        return f"{_ceil(gbps, mbps)} GB/s"

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


def _ceil(characteristic: int, mantissa: int) -> str:
    return f"{characteristic}.{math.ceil(int(mantissa % 1024) / 100)}"
