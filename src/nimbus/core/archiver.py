from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_start

from nimbus.core.runner import CompletedProcess, Runner


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


class RarArchiver(Archiver):
    """
    Create a password protected archive using 'WinRar'.
    """

    def __init__(self, runner: Runner, password: str):
        self._runner = runner
        self._password = password

    @log_on_start(logging.INFO, "Archiving {folder!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, folder: str, archive: str) -> ArchivalStatus:

        # Ensure destination folder exists
        directory_path = os.path.dirname(archive)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

        # It is expected that 'rar' executable
        # is available in a system PATH.
        proc = self._runner.execute(
            [
                "rar",  # https://www.win-rar.com/download.html
                "a",  # archive
                "-r",  # recursive
                "-rr5",  # 5% recovery data
                "-htb",  # use BLAKE2 hash
                "-m3",  # compression level [0-5]
                "-md128m",  # 128 MB dictionary size
                "-qo+",  # add quick open information
                "-idq",  # silent mode
                "-ep1",  # exclude prefix from file names
                "-k",  # lock archive
                "-y",  # yes to all questions
                f"-hp{self._password}",  # protect with password
                archive,
                folder,
            ]
        )

        return ArchivalStatus(proc, folder, archive)


class ArchivalStatus:

    def __init__(self, proc: CompletedProcess, folder: str, archive: str):
        self.proc = proc
        self.folder = folder
        self.archive = archive

    @property
    def success(self) -> bool:
        return self.proc.success and self.folder and self.archive and os.path.exists(self.archive)

    @property
    def size(self) -> int:
        return os.stat(self.archive).st_size if self.success else None

    @property
    def speed(self) -> int:
        return int(self.size // self.proc.elapsed.total_seconds()) if self.success else 0
