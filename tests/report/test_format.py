from datetime import datetime, timedelta

import pytest

import nas.report.format as fmt


@pytest.mark.parametrize(
    "size, readable_size",
    [
        (0, "0 bytes"),
        (174, "174 bytes"),
        (3820, "3.7 KB"),
        (4.5 * 1024, "4.5 KB"),
        (5 * 1024 * 1024, "5.0 MB"),
        (5.001 * 1024 * 1024, "5.0 MB"),
        (5.093 * 1024 * 1024, "5.0 MB"),
        (5.100 * 1024 * 1024, "5.0 MB"),
        (5.101 * 1024 * 1024, "5.1 MB"),
        (5.173 * 1024 * 1024, "5.1 MB"),
        (5.211 * 1024 * 1024, "5.2 MB"),
        (5.373 * 1024 * 1024, "5.3 MB"),
        (5.999 * 1024 * 1024, "5.9 MB"),
        (125_825_450, "119.9 MB"),
        (7 * 1024 * 1024 * 1024, "7.0 GB"),
        (7.331 * 1024 * 1024 * 1024, "7.3 GB"),
        (9.102 * 1024 * 1024 * 1024 * 1024, "9.1 TB"),
    ],
)
def test_size(size, readable_size):
    assert fmt.size(size) == readable_size


@pytest.mark.parametrize(
    "bytes_per_second, readable_speed",
    [
        (75, "75 B/s"),
        (75 * 1024, "75.0 KB/s"),
        (214.6 * 1024 * 1024, "214.5 MB/s"),
        (214.601 * 1024 * 1024, "214.6 MB/s"),
        (135.6 * 1024 * 1024, "135.5 MB/s"),
        (165.6 * 1024 * 1024 * 1024, "165.5 GB/s"),
    ],
)
def test_speed(bytes_per_second, readable_speed):
    assert fmt.speed(bytes_per_second) == readable_speed


@pytest.mark.parametrize(
    "duration, readable_duration",
    [
        (timedelta(), "< 01s"),
        (timedelta(microseconds=550), "< 01s"),
        (timedelta(seconds=1), "01s"),
        (timedelta(seconds=2), "02s"),
        (timedelta(seconds=29), "29s"),
        (timedelta(seconds=61), "01m 01s"),
        (timedelta(minutes=5, seconds=66), "06m 06s"),
        (timedelta(hours=4, minutes=0, seconds=5), "04h 00m 05s"),
        (timedelta(hours=23), "23h 00m 00s"),
        (timedelta(hours=23, minutes=33, seconds=15), "23h 33m 15s"),
        (timedelta(hours=48, minutes=5), "2d 00h 05m 00s"),
        (timedelta(hours=48, minutes=5, seconds=17), "2d 00h 05m 17s"),
        (timedelta(hours=49, minutes=59, seconds=17), "2d 01h 59m 17s"),
        (timedelta(hours=480, seconds=9), "20d 00h 00m 09s"),
    ],
)
def test_duration(duration, readable_duration):
    assert fmt.duration(duration) == readable_duration


@pytest.mark.parametrize(
    "datetime_fmt, dt, readable_dt",
    [
        (None, datetime(year=2004, month=8, day=3, hour=17, minute=33), "2004-08-03 17:33:00"),
        ("%Y-%m-%d %H:%M:%S", datetime(year=2004, month=8, day=3, hour=17, minute=33), "2004-08-03 17:33:00"),
        ("%Y/%m/%d_%H-%M-%S", datetime(year=2011, month=6, day=13, hour=1, minute=3, second=7), "2011/06/13_01-03-07"),
    ],
)
def test_date_time(datetime_fmt, dt, readable_dt):
    assert fmt.datetime(dt, fmt=datetime_fmt) == readable_dt


@pytest.mark.parametrize(
    "date_fmt, d, readable_d",
    [
        (None, datetime(year=2004, month=8, day=3), "2004-08-03"),
        ("%Y-%m-%d", datetime(year=2004, month=8, day=3), "2004-08-03"),
        ("%Y/%m/%d", datetime(year=2011, month=6, day=13), "2011/06/13"),
    ],
)
def test_date(date_fmt, d, readable_d):
    assert fmt.date(d, fmt=date_fmt) == readable_d


@pytest.mark.parametrize(
    "time_fmt, t, readable_t",
    [
        (None, datetime(year=2004, month=8, day=3, hour=17, minute=33, second=47), "17:33:47"),
        ("%H:%M:%S", datetime(year=2004, month=8, day=3, hour=17, minute=33, second=47), "17:33:47"),
        ("%H-%M-%S", datetime(year=2004, month=8, day=3, hour=1, minute=3, second=7), "01-03-07"),
    ],
)
def test_time(time_fmt, t, readable_t):
    assert fmt.time(t, fmt=time_fmt) == readable_t


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
            "rl",
            [
                ["     a111111", "b11  ", " c1"],
                ["a22 ", "  b2", "  c22 "],
                [" a333 ", "  b33333", "c333  "],
                ["a4", "     b4", " c444444  "],
            ],
            [
                ["     a111111", "b11  ", " c1"],
                ["a22 ", "  b2", "  c22 "],
                [" a333 ", "  b33333", "c333  "],
                ["a4", "     b4", " c444444  "],
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
    assert list(fmt.align(entries, alignment)) == aligned
