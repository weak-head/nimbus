from datetime import datetime as dt
from datetime import timedelta as td

from nimbus.core.uploader import UploadStatus


class TestAwsUploader:
    pass


class TestUploadStatus:

    def test_status(self):
        us = UploadStatus("file", "key")
        assert us.status == UploadStatus.SUCCESS

        us.exception = Exception()
        assert us.status == UploadStatus.FAILED

    def test_success(self):
        us = UploadStatus("file", "key")
        us.size = 100
        us.started = dt.now()
        us.completed = dt.now()
        assert us.success

        us.completed = None
        assert not us.success

    def test_elapsed(self):
        us = UploadStatus("file", "key")

        us.started = dt.now()
        us.completed = us.started
        assert us.elapsed == td(seconds=1)

        us.started = dt(year=2024, month=1, day=1, hour=10, minute=30, second=0)
        us.completed = dt(year=2024, month=1, day=1, hour=11, minute=35, second=7)
        assert us.elapsed == td(hours=1, minutes=5, seconds=7)

    def test_speed(self):
        us = UploadStatus("file", "key")
        us.size = 60_000
        us.started = dt(year=2024, month=1, day=1, hour=10, minute=30, second=0)
        us.completed = dt(year=2024, month=1, day=1, hour=10, minute=31, second=0)
        assert us.speed == 1000

        us.size = 0
        assert us.speed == 0

        us.size = 100
        us.completed = None
        assert us.speed == 0
