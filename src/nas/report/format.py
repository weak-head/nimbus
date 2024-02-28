"""
Exposes functionality to format, convert and pretty print.
"""

import math
from datetime import datetime, timedelta


class Formatter:
    """
    Provides functionality to format, convert and pretty print
    to human readable representation:
        - Data size
        - Transfer speed
        - Duration
        - Date and time
    """

    def __init__(
        self,
        date_time_format: str = "%Y-%m-%d %H:%M:%S",
        date_format: str = "%Y-%m-%d",
        time_format: str = "%H:%M:%S",
    ):
        """
        tbd

        :param date_time_format: tbd
        :param date_format: tbd
        :param time_format: tbd
        """
        self._date_time_format = date_time_format
        self._date_format = date_format
        self._time_format = time_format

    def size(self, size_bytes: int):
        """
        Format the data size, to a human readable representation.
        The typical formatted output:
            - 640 bytes
            - 15 KB
            - 5.33 MB
            - 312.7 GB
            - 1.92 TB

        :param size_bytes: Size in bytes to format to bytes, KB, MB, GB or TB.
        :return: String representation of the data size.
        """
        # In bytes
        if size_bytes < 1024:
            return f"{size_bytes} bytes"

        # In KB
        size_kbytes = int(size_bytes // 1024)
        if size_kbytes < 1024:
            return f"{size_kbytes} KB"

        # In MB
        size_mbytes = int(size_kbytes // 1024)
        if size_mbytes < 1024:
            return f"{size_mbytes}.{math.ceil(int(size_kbytes % 1024) / 100)} MB"

        # In GB
        size_gbytes = int(size_mbytes // 1024)
        if size_gbytes < 1024:
            return f"{size_gbytes}.{math.ceil(int(size_mbytes % 1024) / 100)} GB"

        # In TB
        size_tbytes = int(size_gbytes // 1024)
        return f"{size_tbytes}.{math.ceil(int(size_gbytes % 1024) / 100)} TB"

    def speed(self, bps: int):
        """
        Calculate and format the data transfer speed.
        The typical formatted output:
            - 17 bytes/second
            - 33 KB/s
            - 15.437 MB/s
            - 2.39 GB/s

        :param bps: Bytes per second.
        :return: String representation of the transfer speed.
        """

        # In bytes/second
        if bps < 1024:
            return f"{bps} bytes/second"

        # In KB/s
        kbps = int(bps // 1024)
        if kbps < 1024:
            return f"{kbps}.{math.ceil(int(bps % 1024) / 100)} KB/s"

        # In MB/s
        mbps = int(kbps // 1024)
        if mbps < 1024:
            return f"{mbps}.{math.ceil(int(kbps % 1024) / 100)} MB/s"

        # In GB/s
        gbps = int(mbps // 1024)
        return f"{gbps}.{math.ceil(int(mbps % 1024) / 100)} GB/s"

    def duration(self, elapsed: timedelta):
        """
        Formats duration to human readable representation.

        :param elapsed: The duration to format.
        :return: Human readable representation of the duration.
        """
        data = {}
        data["days"], remaining = divmod(elapsed.total_seconds(), 86_400)
        data["hours"], remaining = divmod(remaining, 3_600)
        data["minutes"], data["seconds"] = divmod(remaining, 60)

        time_parts = ((name, round(value)) for name, value in data.items())

        # Remove 's' suffixes, when value is '1'
        time_parts = [f"{value} {name[:-1] if value == 1 else name}" for name, value in time_parts if value > 0]

        return " ".join(time_parts) if time_parts else "less than one second"

    def date_time(self, dt: datetime):
        """
        Format the provided `datetime` as human readable date and time.

        :param dt: Datetime to format as human-readable date and time.
        :return: Human readable representation of the provided date and time.
        """
        return dt.strftime(self._date_time_format)

    def date(self, d: datetime):
        """
        Format the provided `datetime` as human readable date.

        :param d: Datetime to format as human-readable date.
        :return: Human readable representation of the provided date.
        """
        return d.strftime(self._date_format)

    def time(self, t: datetime):
        """
        Format the provided `datetime` as human readable time.

        :param t: Datetime to format as human-readable time.
        :return: Human readable representation of the provided time.
        """
        return t.strftime(self._time_format)
