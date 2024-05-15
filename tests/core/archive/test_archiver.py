from datetime import datetime, timedelta

import pytest
from mock import PropertyMock, patch

from nimbuscli.core.archive.archiver import ArchivalStatus


class TestArchivalStatus:

    @pytest.mark.parametrize("directory", [True, False])
    @pytest.mark.parametrize("archive", [True, False])
    @pytest.mark.parametrize("exists", [True, False])
    @pytest.mark.parametrize("started", [datetime(2024, 1, 1, 10, 30, 00), None])
    @pytest.mark.parametrize("completed", [datetime(2024, 1, 1, 10, 35, 10), None])
    def test_success(self, directory, archive, exists, started, completed):
        patcher = patch("os.path.exists")
        mock_exists = patcher.start()
        mock_exists.return_value = exists

        fdr = "directory" if directory else None
        arc = "archive" if archive else None

        a = ArchivalStatus(fdr, arc)
        a.started = started
        a.completed = completed

        assert a.success == all([directory, archive, exists, started, completed])

    def test_success_with_exception(self):
        patcher = patch("os.path.exists")
        mock_exists = patcher.start()
        mock_exists.return_value = True

        a = ArchivalStatus("dir", "arc")
        a.started = datetime(2024, 1, 1, 10, 30, 00)
        a.completed = datetime(2024, 1, 1, 10, 32, 00)
        assert a.success

        a.exception = Exception()
        assert not a.success

    @patch("os.stat")
    @patch("os.path.exists")
    def test_size(self, mock_exists, mock_osstat):
        type(mock_osstat.return_value).st_size = PropertyMock(return_value=100)
        mock_exists.return_value = True

        a = ArchivalStatus("dir", "arc")
        a.started = datetime(2024, 1, 1, 10, 30, 00)
        a.completed = datetime(2024, 1, 1, 10, 35, 00)

        assert a.size == 100

        mock_exists.return_value = False
        assert a.size is None

    @patch("os.stat")
    @patch("os.path.exists")
    def test_speed(self, mock_exists, mock_osstat):
        type(mock_osstat.return_value).st_size = PropertyMock(return_value=6_600)
        mock_exists.return_value = True

        a = ArchivalStatus("dir", "arc")
        a.started = datetime(2024, 1, 1, 10, 30, 00)
        a.completed = datetime(2024, 1, 1, 10, 31, 00)

        assert a.speed == 110
        assert a.elapsed == timedelta(minutes=1)

        mock_exists.return_value = False
        assert a.speed == 0
        assert a.elapsed == timedelta(minutes=1)

        mock_exists.return_value = True
        a.completed = None
        assert a.speed == 0
        assert a.elapsed is None

    @patch("os.stat")
    @patch("os.path.exists")
    def test_elapsed(self, mock_exists, mock_osstat):
        type(mock_osstat.return_value).st_size = PropertyMock(return_value=100)
        mock_exists.return_value = False

        a = ArchivalStatus("dir", "arc")

        a.started = datetime(2024, 1, 1, 10, 30, 00)
        a.completed = datetime(2024, 1, 1, 10, 35, 00)
        assert a.elapsed == timedelta(minutes=5)

        a.completed = None
        assert a.elapsed is None

        a.started = None
        a.completed = datetime(2024, 1, 1, 10, 35, 00)
        assert a.elapsed is None
