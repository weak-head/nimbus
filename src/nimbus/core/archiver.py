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
    https://www.win-rar.com/download.html
    """

    def __init__(
        self,
        runner: Runner,
        password: str = None,
        compression: int = 3,
        recovery: int = 3,
    ):
        """
        Creates a new instance of the RarArchiver.

        :param runner: Process runner.
        :param password: Password to protect the archive with.
        :param compression: Compression level [0-5].
        :param recovery: Recovery record (%) [0-1000].
        """
        if runner is None:
            raise ValueError("The runner cannot be None")

        if password is not None:
            if password == "":
                raise ValueError("If password is specified, it cannot be empty string")

        if compression is not None:
            if not (0 <= compression <= 5):
                raise ValueError("Compression should be in range [0-5]")

        if recovery is not None:
            if not (0 <= recovery <= 1000):
                raise ValueError("Recovery should be in range [0-1000]")

        self._runner = runner
        self._password = password
        self._compression = compression
        self._recovery = recovery

    @log_on_start(logging.INFO, "Archiving {folder!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, folder: str, archive: str) -> ArchivalStatus:
        # Ensure destination folder exists
        directory_path = os.path.dirname(archive)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

        # It is expected that 'rar' executable
        # is available in a system PATH.
        proc = self._runner.execute(self._build_cmd(folder, archive))
        return ArchivalStatus(proc, folder, archive)

    def _build_cmd(self, folder: str, archive: str) -> list[str]:
        cmd = [
            "rar",
            "a",  # archive
            "-r",  # recursive
            "-htb",  # use BLAKE2 hash
            "-md128m",  # 128 MB dictionary size
            "-qo+",  # add quick open information
            "-idq",  # silent mode
            "-ep1",  # exclude prefix from file names
            "-k",  # lock archive
            "-y",  # yes to all questions
        ]

        # Add recovery data [0-1000]
        if self._recovery is not None:
            cmd.append(f"-rr{self._recovery}")

        # Compression level [0-5]
        if self._compression is not None:
            cmd.append(f"-m{self._compression}")

        # Protect with password
        if self._password is not None:
            cmd.append(f"-hp{self._password}")

        cmd.extend([archive, folder])
        return cmd


class ArchivalStatus:

    def __init__(self, proc: CompletedProcess, folder: str, archive: str):
        self.proc = proc
        self.folder = folder
        self.archive = archive

    @property
    def success(self) -> bool:
        return all(
            [
                self.proc.success,
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
        return int(self.size // self.proc.elapsed.total_seconds()) if self.success else 0
