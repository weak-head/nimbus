"""
Provides abstract base class `Uploader` for all uploaders and implements:
  - `AwsUploader` - Upload files to a pre-configured AWS S3 bucket.
"""

from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable

from boto3 import Session
from boto3.exceptions import S3UploadFailedError


class Uploader(ABC):
    """Generic file uploader, with the pre-configured upload destination."""

    @abstractmethod
    def upload(self, filepath: str, key: str, on_progress: Callable = None) -> UploadResult:
        """
        Upload a file to the pre-configured destination.

        :param filepath: Path to the file that should be uploaded.
        :param key: The name of the key to upload to.
        :param on_progress: Called when upload progress is changed.
        :return: Result of the file upload.
        """


class AwsUploader(Uploader):
    """Upload files to a pre-configured AWS S3 bucket."""

    def __init__(self, access_key: str, secret_key: str, bucket: str, storage_class: str):
        """
        Create a new instance of `AwsUploader` with the pre-configured destination bucket.

        :param access_key: AWS access key.
        :param secret_key: AWS secret key.
        :param bucket: AWS S3 bucket.
        :param storage_class: Object storage class.
        """

        # AWS session
        self._session = Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        # s3 client
        self._s3 = self._session.client("s3")

        # s3 bucket
        self._bucket = bucket

        # s3 object storage class
        self._storage_class = storage_class

    def upload(self, filepath: str, key: str, on_progress: Callable = None) -> UploadResult:
        """
        Upload a file to the pre-configured destination.

        :param filepath: Full path to the file.
        :param key: The name of the key to upload to.
        :param on_progress: Called when upload progress is changed.
        :return: Result of the file upload.
        """

        result = UploadResult(filepath, key)
        result.started = datetime.now()
        result.size = os.stat(filepath).st_size

        try:

            self._s3.upload_file(
                filepath,
                self._bucket,
                key,
                ExtraArgs={"StorageClass": self._storage_class},
                Callback=_CallbackProxy(filepath, on_progress),
            )

        except S3UploadFailedError as e:
            result.exception = e

        result.completed = datetime.now()
        return result


class UploadResult:
    """Result of uploading a single file."""

    SUCCESS = "success"
    """The file has been successfully uploaded."""

    FAILED = "failed"
    """There has been some failure uploading the file."""

    def __init__(self, filepath: str, key: str):
        """
        Create a new instance of the UploadResult with empty values.

        :param filepath: Path to the file.
        :param key: The name of the key to upload to.
        """

        self.filepath = filepath
        """Path to the file."""

        self.key = key
        """The name of the key to upload to."""

        self.size = None
        """Upload size, in bytes."""

        self.started = None
        """Upload start time, as `datetime`."""

        self.completed = None
        """Upload completion time, as `datetime`."""

        self.exception = None
        """The generated exception, or `None`."""

    @property
    def status(self) -> str:
        """Upload status."""
        return UploadResult.FAILED if self.exception else UploadResult.SUCCESS

    @property
    def successful(self) -> bool:
        """True, if the file has been successfully uploaded."""
        return (
            self.status == UploadResult.SUCCESS
            and self.filepath
            and self.key
            and self.size
            and self.started
            and self.completed
        )

    @property
    def elapsed(self) -> timedelta:
        """Upload elapsed time, as `timedelta`."""
        return max(timedelta(seconds=1), self.completed - self.started)

    @property
    def speed(self) -> int:
        """Average upload speed."""
        return int(self.size // self.elapsed.total_seconds()) if self.successful else 0


class _CallbackProxy:
    """Proxy callback for uploaded percentage reporting."""

    def __init__(self, filepath: str, on_progress: Callable):
        """
        Create and initialize a new instance of the callback.

        :param filepath: Full path to the file.
        :param log: Log writer.
        """
        self._filepath = filepath
        self._filesize = os.stat(filepath).st_size
        self._on_progress = on_progress
        self._uploaded = 0
        self._reported = 0
        self._started = datetime.now()
        self._lock = threading.Lock()

    def __call__(self, bytes_amount: int):
        """
        Invoke the callback, reporting the new amount of uploaded bytes.

        :param bytes_amount: Amount of uploaded bytes since the previous call.
        """
        with self._lock:

            # Adjust the total amount of uploaded bytes,
            # and calculate the current upload progress.
            self._uploaded += bytes_amount
            progress = int((self._uploaded / self._filesize) * 100)

            # Report progress, with incremental increase by at least 10%
            if progress >= self._reported + 10:
                self._reported = progress

                elapsed = max(timedelta(seconds=1), datetime.now() - self._started)
                speed = int(self._uploaded // elapsed.total_seconds())

                # Report the upload progress
                self._on_progress(
                    progress=progress,
                    uploaded=self._uploaded,
                    elapsed=elapsed,
                    speed=speed,
                )
