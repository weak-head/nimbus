from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable

from boto3 import Session
from boto3.exceptions import S3UploadFailedError


class Uploader(ABC):
    """
    Defines an abstract file uploader.
    All uploaders should follow the APIs defined by this class.
    """

    @abstractmethod
    def upload(self, filepath: str, key: str, on_progress: Callable = None) -> UploadResult:
        """
        Upload a file to the pre-configured destination.

        :param filepath: Full path to the file that should be uploaded.

        :param key: The name of the key to upload to.

        :param on_progress: An optional callback that is invoked on progress update.
            The callback accepts four positional arguments:
                - uploaded bytes (`int`)
                - uploaded percentage (`int`)
                - elapsed time (`timedelta`)
                - average upload speed, bytes per second (`int`)

        :return: Result of the file upload.
        """


class AwsUploader(Uploader):
    """
    AWS S3 file uploader.
    """

    class CallbackAdapter:
        """
        Converts boto3 callback to common callback.
        """

        def __init__(self, filepath: str, on_progress: Callable):
            self._filepath = filepath
            self._filesize = os.stat(filepath).st_size
            self._on_progress = on_progress
            self._uploaded = 0
            self._reported = 0
            self._started = datetime.now()
            self._lock = threading.Lock()

        def __call__(self, bytes_amount: int):
            with self._lock:

                # Accumulate the uploaded bytes,
                # and calculate the upload progress.
                self._uploaded += bytes_amount
                progress = int((self._uploaded / self._filesize) * 100)

                # Throttle the reported progress.
                # Report when uploaded (at least) another 10% of the file.
                if progress >= self._reported + 10:
                    self._reported = progress

                    elapsed = max(timedelta(seconds=1), datetime.now() - self._started)
                    speed = int(self._uploaded // elapsed.total_seconds())

                    self._on_progress(self._uploaded, progress, elapsed, speed)

    def __init__(self, access_key: str, secret_key: str, bucket: str, storage_class: str):
        self._session = Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._s3 = self._session.client("s3")
        self._bucket = bucket

        # See:
        #  - https://aws.amazon.com/s3/storage-classes/
        #  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
        self._storage_class = storage_class

    def upload(self, filepath: str, key: str, on_progress: Callable = None) -> UploadResult:
        result = UploadResult(filepath, key)
        result.started = datetime.now()
        result.size = os.stat(filepath).st_size

        try:

            self._s3.upload_file(
                filepath,
                self._bucket,
                key,
                ExtraArgs={"StorageClass": self._storage_class},
                Callback=AwsUploader.CallbackAdapter(filepath, on_progress) if on_progress else None,
            )

        except S3UploadFailedError as e:
            result.exception = e

        result.completed = datetime.now()
        return result


class UploadResult:

    SUCCESS = "success"
    FAILED = "failed"

    def __init__(self, filepath: str, key: str):
        self.filepath = filepath
        self.key = key
        self.size: int = None
        self.started: datetime = None
        self.completed: datetime = None
        self.exception: Exception = None

    @property
    def status(self) -> str:
        return UploadResult.FAILED if self.exception else UploadResult.SUCCESS

    @property
    def successful(self) -> bool:
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
        return max(timedelta(seconds=1), self.completed - self.started)

    @property
    def speed(self) -> int:
        return int(self.size // self.elapsed.total_seconds()) if self.successful else 0
