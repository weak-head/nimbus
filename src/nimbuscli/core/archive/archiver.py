from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class Archiver(ABC):
    """
    Defines an abstract archiver.
    All archivers should follow the APIs defined by this class.
    """

    @abstractmethod
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        """
        Archive a directory.

        :param directory: Full path to the directory that should be archived.
        :param archive: A file path where the archive should be created.
        :return: Status of the directory archival.
        """

    @property
    @abstractmethod
    def extension(self) -> str:
        """
        The recommended file extension for the archive.
        """


class ArchivalStatus:

    def __init__(self, directory: str, archive: str, started: datetime, completed: datetime):
        self.directory = directory
        self.archive = archive
        self.started = started
        self.completed = completed

    @property
    def success(self) -> bool:
        return all(
            [
                self.started,
                self.completed,
                self.directory,
                self.archive,
                os.path.exists(self.archive),
            ]
        )

    @property
    def size(self) -> int:
        return os.stat(self.archive).st_size if self.success else None

    @property
    def speed(self) -> int:
        return int(self.size // self.elapsed.total_seconds()) if self.success else 0

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started
