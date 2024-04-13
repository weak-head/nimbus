from __future__ import annotations

import logging
import os
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable

from boto3 import Session
from logdecorator import log_on_end, log_on_error, log_on_start


class UploadProgress:
    """
    Defines a file upload progress.
    """

    def __init__(self, progress: int, elapsed: timedelta, speed: int):
        self.progress = progress
        self.elapsed = elapsed
        self.speed = speed
        self.timestamp = datetime.now()

    def __repr__(self):
        params = [
            f"timestamp='{self.timestamp}'",
            f"progress='{self.progress}'",
            f"speed='{self.speed}'",
            f"elapsed='{self.elapsed}'",
        ]
        return "UploadProgress(" + ", ".join(params) + ")"


class Uploader(ABC):
    """
    Defines an abstract file uploader.
    All uploaders should follow the APIs defined by this class.
    """

    @abstractmethod
    def config(self) -> dict[str, str]:
        """
        Returns a configuration used by this uploader.
        """

    @abstractmethod
    def upload(
        self,
        filepath: str,
        key: str,
        on_progress: Callable[[UploadProgress], None] = None,
    ) -> UploadStatus:
        """
        Upload a file to the pre-configured destination.

        :param filepath: Full path to the file that should be uploaded.
        :param key: The name of the key to upload to.
        :param on_progress: An optional callback that is invoked on progress update.
        :return: Status of the file upload.
        """


class AwsUploader(Uploader):
    """
    Upload files to AWS S3 bucket.
    """

    class CallbackAdapter:
        """
        Converts boto3 callback to common callback.
        """

        def __init__(self, filepath: str, on_progress: Callable[[UploadProgress], None]):
            self._filepath = filepath
            self._filesize = os.stat(filepath).st_size
            self._on_progress = on_progress
            self._uploaded = 0
            self._reported = 0
            self._started = datetime.now()
            self._lock = threading.Lock()

        def __eq__(self, other):
            return (self._filepath, self._on_progress) == (other._filepath, other._on_progress)

        @log_on_end(logging.DEBUG, "Uploaded {self._filepath!s} [{self._uploaded!s}/{self._filesize!s}]")
        def __call__(self, bytes_amount: int):
            with self._lock:

                # Accumulate the uploaded bytes,
                # and calculate the upload progress.
                self._uploaded += bytes_amount
                progress = min(int((self._uploaded / self._filesize) * 100), 100)

                # Throttle the reported progress.
                # Report when uploaded (at least) another 10% of the file.
                if progress >= self._reported + 10 or (progress == 100 and self._reported != 100):
                    self._reported = progress

                    elapsed = max(timedelta(seconds=1), datetime.now() - self._started)
                    speed = int(self._uploaded // elapsed.total_seconds())

                    self._on_progress(UploadProgress(progress, elapsed, speed))

    def __init__(self, access_key: str, secret_key: str, bucket: str, storage_class: str):
        self._session = Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._access_key = access_key
        self._secret_key = secret_key
        self._s3 = self._session.client("s3")
        self._bucket = bucket

        # See:
        #  - https://aws.amazon.com/s3/storage-classes/
        #  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
        self._storage_class = storage_class

    def __repr__(self) -> str:
        params = [
            f"access='{self._access_key}'",
            f"secret='{self._secret_key}'",
            f"bucket='{self._bucket}'",
            f"storage='{self._storage_class}'",
        ]
        return "AwsUploader(" + ", ".join(params) + ")"

    def config(self) -> dict[str, str]:
        return {
            "S3 Bucket": self._bucket,
            "S3 Storage": self._storage_class,
        }

    def upload(
        self,
        filepath: str,
        key: str,
        on_progress: Callable[[UploadProgress], None] = None,
    ) -> UploadStatus:
        status = UploadStatus(filepath, key)
        status.started = datetime.now()
        status.size = os.stat(filepath).st_size

        try:

            self._upload(
                filepath,
                self._bucket,
                key,
                self._storage_class,
                AwsUploader.CallbackAdapter(filepath, on_progress) if on_progress else None,
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            status.exception = e

        status.completed = datetime.now()
        return status

    @log_on_start(logging.INFO, "Uploading to s3 {bucket!s}/{key!s} [{storage_class!s}]")
    @log_on_end(logging.INFO, "Uploaded {bucket!s}/{key!s}")
    @log_on_error(logging.ERROR, "Failed to upload {filepath!s}: {e!r}", on_exceptions=Exception)
    def _upload(
        self,
        filepath: str,
        bucket: str,
        key: str,
        storage_class: str,
        on_progress: AwsUploader.CallbackAdapter,
    ):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
        self._s3.upload_file(
            filepath,
            bucket,
            key,
            ExtraArgs={"StorageClass": storage_class},
            Callback=on_progress,
        )


class UploadStatus:

    SUCCESS = "success"
    FAILED = "failed"

    def __init__(self, filepath: str, key: str):
        self.filepath: str = filepath
        self.key: str = key
        self.size: int = None
        self.started: datetime = None
        self.completed: datetime = None
        self.exception: Exception = None

    @property
    def status(self) -> str:
        return UploadStatus.FAILED if self.exception else UploadStatus.SUCCESS

    @property
    def success(self) -> bool:
        return all(
            [
                self.status == UploadStatus.SUCCESS,
                self.filepath,
                self.key,
                self.size,
                self.started,
                self.completed,
            ]
        )

    @property
    def elapsed(self) -> timedelta:
        return max(timedelta(seconds=1), self.completed - self.started)

    @property
    def speed(self) -> int:
        return int(self.size // self.elapsed.total_seconds()) if self.success else 0
