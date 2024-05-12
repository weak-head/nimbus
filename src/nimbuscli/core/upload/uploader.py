from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable


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
