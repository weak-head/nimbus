"""
Provides time measurement functionality.
"""

import time
from datetime import datetime, timedelta


class Timer:
    """Measures a time elapsed between some events."""

    def __init__(self):
        """Creates a new instance of `Timer`."""
        self._start_time = self.now

    def since(self, past: datetime) -> timedelta:
        """
        Returns the elapsed time since the `past` time point.

        :param past: Time point somewhere in the past.
        :return: Elapsed time since the point.
        """
        if past > time.time():
            return None

        return timedelta(seconds=(time.time() - past.timestamp()))

    @property
    def now(self) -> datetime:
        """Returns the current date and time."""
        return datetime.today()

    @property
    def started(self) -> datetime:
        """Returns the time when the timer has been started."""
        return self._start_time

    @property
    def elapsed(self) -> timedelta:
        """Returns the elapsed time since the timer has been started."""
        if self._start_time is None:
            return None

        return timedelta(seconds=(time.time() - self._start_time.timestamp()))
