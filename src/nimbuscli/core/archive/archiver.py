from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import ContextManager

from logdecorator import log_on_end, log_on_start


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


class FSArchiver(Archiver):
    """
    Abstract base class for all archivers that traverse a file system
    starting from a specified root directory and process each file one-by-one.
    """

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        status = ArchivalStatus(directory, archive)
        status.started = datetime.now()

        try:
            with self.init_archiver(archive) as arc:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_name = os.path.relpath(file_path, directory)
                        self.add_file(arc, file_path, file_name)
        except Exception as e:  # pylint: disable=broad-exception-caught
            status.exception = e

        status.completed = datetime.now()
        return status

    @abstractmethod
    def init_archiver(self, archive: str) -> ContextManager:
        """
        Create and initialize an instance of an archiver that
        acts as a context manager.

        :param archive: A file path where the archive should be created.
        :return: An archiver that implements the context manager.
        """

    @abstractmethod
    def add_file(self, arc: ContextManager, file_path: str, file_name: str) -> None:
        """
        Add a file to the archive using a previously created archiver.

        :param arc: An instance of the archiver, created with `init_archiver` method.
        :param file_path: The absolute path to the file.
        :param file_name: An alternative name for the file in the archive.
        """


class ArchivalStatus:

    def __init__(self, directory: str, archive: str):
        self.directory: str = directory
        self.archive: str = archive
        self.started: datetime = None
        self.completed: datetime = None
        self.exception: Exception = None

    @property
    def success(self) -> bool:
        return all(
            [
                self.exception is None,
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
    def elapsed(self) -> timedelta | None:
        if self.started is not None and self.completed is not None:
            return self.completed - self.started
        return None
