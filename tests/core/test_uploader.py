from datetime import datetime as dt
from datetime import timedelta as td

import pytest
from mock import Mock, PropertyMock, patch

from nimbuscli.core import AwsUploader, UploadProgress, UploadStatus
from tests.helpers import MockDateTime


class MockOnProgress:

    def __init__(self):
        self.reported: list[UploadProgress] = []

    def __call__(self, progress: UploadProgress):
        self.reported.append(progress)


class TestAwsUploaderCallbackAdapter:

    @pytest.mark.parametrize(
        ["filesize", "upbytes", "reported"],
        [
            [
                100,
                [1, 2, 3, 3, 5, 16, 15, 1, 54],
                [14, 30, 45, 100],
            ],
            [
                100,
                [25, 1, 4, 1, 1, 1, 1, 1, 65],
                [25, 35, 100],
            ],
            [
                100,
                [1] * 100,
                [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ],
            [
                100,
                [1] * 300,
                [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ],
            [
                100,
                [17] + ([1] * 83),
                [17, 27, 37, 47, 57, 67, 77, 87, 97, 100],
            ],
            [
                100,
                [17, 9, 9, 25],
                [17, 35, 60],
            ],
        ],
    )
    @patch("os.stat")
    @patch("nimbuscli.core.uploader.datetime", MockDateTime)
    def test_onprogress(self, mock_osstat, filesize, upbytes, reported):
        type(mock_osstat.return_value).st_size = PropertyMock(return_value=filesize)

        now_time = dt(2024, 1, 1, 10, 00, 00)
        call_time = [now_time]
        for _ in range(len(reported) * 2):
            call_time.append(now_time + td(seconds=5))
            now_time = now_time + td(seconds=5)
        MockDateTime.now_returns(*call_time)

        mock_onprogress = MockOnProgress()
        callback = AwsUploader.CallbackAdapter("filepath", mock_onprogress)

        assert callback._filesize == filesize

        for value in upbytes:
            callback(value)

        assert len(mock_onprogress.reported) == len(reported)

        for ix, value in enumerate(reported):
            progress = mock_onprogress.reported[ix]
            assert progress.progress == value


class TestAwsUploader:

    class MockSession:

        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def client(self, name):
            self._client_name = name
            return Mock()

    @patch("nimbuscli.core.uploader.Session", MockSession)
    def test_config(self):
        uploader = AwsUploader("key", "secret", "bucket", "class")

        cfg = uploader.config()

        kwargs = uploader._session._kwargs
        client_name = uploader._session._client_name
        assert kwargs == {"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        assert client_name == "s3"
        assert cfg == {"S3 Bucket": "bucket", "S3 Storage": "class"}

    @patch("os.stat")
    @patch("nimbuscli.core.uploader.Session", Mock)
    @patch("nimbuscli.core.uploader.datetime", MockDateTime)
    def test_upload(self, mock_osstat):
        started_dt = dt(2024, 5, 10, 12, 30, 50)
        completed_dt = dt(2024, 5, 10, 12, 35, 55)
        MockDateTime.now_returns(
            started_dt,  # started
            started_dt,  # CallbackAdapter.__init__
            completed_dt,  # completed
            completed_dt,  # assert CallbackAdapter.__init__
        )

        type(mock_osstat.return_value).st_size = PropertyMock(return_value=100)

        mock_onprogress = MockOnProgress()

        uploader = AwsUploader("key", "secret", "bucket", "class")
        status = uploader.upload(
            "filepath",
            "key",
            mock_onprogress,
        )

        assert status.size == 100
        assert status.started == started_dt
        assert status.completed == completed_dt
        assert status.status == UploadStatus.SUCCESS
        assert status.success
        uploader._s3.upload_file.assert_called_with(
            "filepath",
            "bucket",
            "key",
            ExtraArgs={"StorageClass": "class"},
            Callback=AwsUploader.CallbackAdapter("filepath", mock_onprogress),
        )

    @patch("os.stat")
    @patch("nimbuscli.core.uploader.Session", Mock)
    @patch("nimbuscli.core.uploader.datetime", MockDateTime)
    def test_upload_exception(self, mock_osstat):
        started_dt = dt(2024, 5, 10, 12, 30, 50)
        completed_dt = dt(2024, 5, 10, 12, 35, 55)
        MockDateTime.now_returns(
            started_dt,  # started
            started_dt,  # CallbackAdapter.__init__
            completed_dt,  # completed
            completed_dt,  # assert CallbackAdapter.__init__
        )

        type(mock_osstat.return_value).st_size = PropertyMock(return_value=100)

        mock_onprogress = MockOnProgress()

        uploader = AwsUploader("key", "secret", "bucket", "class")

        exc = Exception("upload error")
        uploader._s3.upload_file.side_effect = exc

        status = uploader.upload(
            "filepath",
            "key",
            mock_onprogress,
        )

        assert status.size == 100
        assert status.started == started_dt
        assert status.completed == completed_dt
        assert status.exception == exc
        assert status.status == UploadStatus.FAILED
        assert not status.success
        uploader._s3.upload_file.assert_called_with(
            "filepath",
            "bucket",
            "key",
            ExtraArgs={"StorageClass": "class"},
            Callback=AwsUploader.CallbackAdapter("filepath", mock_onprogress),
        )


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
