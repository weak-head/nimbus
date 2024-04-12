from datetime import datetime as dt
from datetime import timedelta as td

from mock import Mock, PropertyMock, patch

from nimbus.core.uploader import AwsUploader, UploadProgress, UploadStatus
from tests.helpers import MockDateTime


class MockOnProgress:
    def __call__(self, progress: UploadProgress):
        pass


class TestAwsUploaderCallbackAdapter:
    pass


class TestAwsUploader:

    class MockSession:

        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def client(self, name):
            self._client_name = name
            return Mock()

    @patch("nimbus.core.uploader.Session", MockSession)
    def test_config(self):
        uploader = AwsUploader("key", "secret", "bucket", "class")

        cfg = uploader.config()

        kwargs = uploader._session._kwargs
        client_name = uploader._session._client_name
        assert kwargs == {"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        assert client_name == "s3"
        assert cfg == {"S3 Bucket": "bucket", "S3 Storage": "class"}

    @patch("os.stat")
    @patch("nimbus.core.uploader.Session", Mock)
    @patch("nimbus.core.uploader.datetime", MockDateTime)
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
    @patch("nimbus.core.uploader.Session", Mock)
    @patch("nimbus.core.uploader.datetime", MockDateTime)
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
