from datetime import datetime, timedelta

import pytest

from nas.report.format import Formatter, align


@pytest.mark.parametrize(
    "size, readable_size",
    [
        (0, "0 bytes"),
        (174, "174 bytes"),
        (3820, "3.8 KB"),
        (4.5 * 1024, "4.6 KB"),
        (5 * 1024 * 1024, "5.0 MB"),
        (5.093 * 1024 * 1024, "5.1 MB"),
        (5.211 * 1024 * 1024, "5.3 MB"),
        (5.373 * 1024 * 1024, "5.4 MB"),
        (7 * 1024 * 1024 * 1024, "7.0 GB"),
        (7.331 * 1024 * 1024 * 1024, "7.4 GB"),
        (9.102 * 1024 * 1024 * 1024 * 1024, "9.2 TB"),
    ],
)
def test_size(size, readable_size):
    assert Formatter().size(size) == readable_size


@pytest.mark.parametrize(
    "bytes_per_second, readable_speed",
    [
        (75, "75 B/s"),
        (75 * 1024, "75.0 KB/s"),
        (214.6 * 1024 * 1024, "214.7 MB/s"),
        (135.6 * 1024 * 1024, "135.7 MB/s"),
        (165.6 * 1024 * 1024 * 1024, "165.7 GB/s"),
    ],
)
def test_speed(bytes_per_second, readable_speed):
    assert Formatter().speed(bytes_per_second) == readable_speed


@pytest.mark.parametrize(
    "duration, readable_duration",
    [
        (timedelta(), "< 1 second"),
        (timedelta(microseconds=550), "< 1 second"),
        (timedelta(seconds=1), "1 second"),
        (timedelta(seconds=2), "2 seconds"),
        (timedelta(seconds=29), "29 seconds"),
        (timedelta(seconds=61), "1 minute 1 second"),
        (timedelta(minutes=5, seconds=66), "6 minutes 6 seconds"),
        (timedelta(hours=4, minutes=0, seconds=5), "4 hours 5 seconds"),
        (timedelta(hours=48, minutes=5), "2 days 5 minutes"),
        (timedelta(hours=48, minutes=5, seconds=17), "2 days 5 minutes 17 seconds"),
    ],
)
def test_duration(duration, readable_duration):
    assert Formatter().duration(duration) == readable_duration


@pytest.mark.parametrize(
    "datetime_fmt, dt, readable_dt",
    [
        ("%Y-%m-%d %H:%M:%S", datetime(year=2004, month=8, day=3, hour=17, minute=33), "2004-08-03 17:33:00"),
        ("%Y/%m/%d_%H-%M-%S", datetime(year=2011, month=6, day=13, hour=1, minute=3, second=7), "2011/06/13_01-03-07"),
    ],
)
def test_date_time(datetime_fmt, dt, readable_dt):
    assert Formatter(datetime_fmt=datetime_fmt).datetime(dt) == readable_dt


@pytest.mark.parametrize(
    "date_fmt, d, readable_d",
    [
        ("%Y-%m-%d", datetime(year=2004, month=8, day=3), "2004-08-03"),
        ("%Y/%m/%d", datetime(year=2011, month=6, day=13), "2011/06/13"),
    ],
)
def test_date(date_fmt, d, readable_d):
    assert Formatter(date_fmt=date_fmt).date(d) == readable_d


@pytest.mark.parametrize(
    "time_fmt, t, readable_t",
    [
        ("%H:%M:%S", datetime(year=2004, month=8, day=3, hour=17, minute=33, second=47), "17:33:47"),
        ("%H-%M-%S", datetime(year=2004, month=8, day=3, hour=1, minute=3, second=7), "01-03-07"),
    ],
)
def test_time(time_fmt, t, readable_t):
    assert Formatter(time_fmt=time_fmt).time(t) == readable_t


@pytest.mark.parametrize(
    "alignment, entries, aligned",
    [
        ("l", [], []),
        ("", [], []),
        (
            "",
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
        ),
        (
            None,
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
        ),
        (
            "non-existing-value",
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
            [
                [" a1", "b1  ", "  c1"],
                ["a2 ", "  b2", "c2  "],
            ],
        ),
        (
            "l",
            [
                [" a1", "b11  ", "  c1"],
                ["a22 ", "  b2", "c233  "],
                [" a333 ", "  b3   ", "c333  "],
            ],
            [
                ["a1  ", "b11", "c1  "],
                ["a22 ", "b2 ", "c233"],
                ["a333", "b3 ", "c333"],
            ],
        ),
        (
            "r",
            [
                [" a1", "b11  ", "  c1"],
                ["a22 ", "  b2", "c233  "],
            ],
            [
                [" a1", "b11", "  c1"],
                ["a22", " b2", "c233"],
            ],
        ),
        (
            "rlc",
            [
                ["     a111111", "b11  ", " c1"],
                ["a22 ", "  b2", "  c22 "],
                [" a333 ", "  b33333", "c333  "],
                ["a4", "     b4", " c444444  "],
            ],
            [
                ["a111111", "b11   ", "   c1  "],
                ["    a22", "b2    ", "  c22  "],
                ["   a333", "b33333", "  c333 "],
                ["     a4", "b4    ", "c444444"],
            ],
        ),
    ],
)
def test_align(alignment, entries, aligned):
    assert list(align(entries, alignment)) == aligned
