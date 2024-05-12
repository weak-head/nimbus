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
    def archive(self, folder: str, archive: str) -> ArchivalStatus:
        """
        Archive a folder.

        :param folder: Full path to the folder that should be archived.
        :param archive: A file path where the archive should be created.
        :return: Status of the folder archival.
        """


class ArchivalStatus:

    def __init__(self, folder: str, archive: str, started: datetime, completed: datetime):
        self.folder = folder
        self.archive = archive
        self.started = started
        self.completed = completed

    @property
    def success(self) -> bool:
        return all(
            [
                self.started,
                self.completed,
                self.folder,
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
