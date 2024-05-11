from datetime import timedelta as td

import pytest

from nimbuscli.core.deploy.service import OperationStatus


class MockProc:

    def __init__(self, s=None, e=None):
        self._success = s
        self._elapsed = e

    @property
    def success(self):
        return self._success

    @property
    def elapsed(self):
        return self._elapsed


class TestOperationStatus:

    @pytest.mark.parametrize(
        "statuses",
        [
            [True],
            [False],
            [True, True, True],
            [True, False, True, False],
            [False, False, False],
        ],
    )
    def test_success(self, statuses):
        operation = OperationStatus("", "", "")
        for s in statuses:
            operation.processes.append(MockProc(s=s))

        assert operation.success == all(statuses)

    @pytest.mark.parametrize(
        ["durations", "expected"],
        [
            [
                [td(minutes=10)],
                td(minutes=10),
            ],
            [
                [td(minutes=10)] * 1000,
                td(minutes=10_000),
            ],
            [
                [td(minutes=10), td(minutes=3)],
                td(minutes=13),
            ],
            [
                [td(hours=1), td(minutes=10), td(seconds=3)],
                td(hours=1, minutes=10, seconds=3),
            ],
            [
                [td(minutes=17), td(minutes=10), td(seconds=3)],
                td(minutes=27, seconds=3),
            ],
        ],
    )
    def test_elapsed(self, durations, expected):
        operation = OperationStatus("", "", "")
        for d in durations:
            operation.processes.append(MockProc(e=d))

        assert operation.elapsed == expected
