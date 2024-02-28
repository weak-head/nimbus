from __future__ import annotations

import os
from abc import ABC, abstractmethod

from nas.core.runner import CompletedProcess, Runner


class Archiver(ABC):
    """Compress and archive data."""

    @abstractmethod
    def archive(self, folder: str, archive_path: str) -> ArchivalResult:
        """
        Create compressed archive from the specified folder.

        :param folder: Input folder to archive, recursive.
        :param archive_path: Path of the output archive.
        :return: Archival result.
        """


class RarArchiver(Archiver):
    """
    Compress and archive data using 'WinRar'.

    - https://www.win-rar.com/download.html
    - https://www.win-rar.com/rar-linux-mac.html
    """

    def __init__(self, runner: Runner, password: str) -> None:
        """
        Creates a new instance of `RarArchiver` that used the provided `Runner`
        to start WinRar archival process.

        :param runner: Command runner to use.
        :param password: Password to protect the archive with.
        """
        self._runner = runner
        self._password = password

    def archive(self, folder: str, archive_path: str) -> ArchivalResult:
        """
        Create compressed archive from the specified folder.

        :param folder: Input folder to archive, recursive.
        :param archive_path: Path of the output archive.
        :return: Archival result.
        """

        # Ensure destination folder exists
        directory_path = os.path.dirname(archive_path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

        # Execute the folder archival using WinRar.
        # It is expected that the 'rar' executable is available in
        # the system PATH and could be access by the user,
        # that executes the archival process.
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
                archive_path,
                folder,
            ]
        )

        return ArchivalResult(proc, folder=folder, archive_path=archive_path)


class ArchivalResult:
    """Result of compressing and archiving a single folder."""

    def __init__(self, proc: CompletedProcess, folder: str, archive_path: str):
        """
        Creates a new instance of the `ArchivalResult`.

        :param proc: Completed process.
        :param folder: Input folder.
        :param archive_path: Full path to the created archive.
        """

        self.proc = proc
        """Completed archival process."""

        self.folder = folder
        """Input folder."""

        self.archive_path = archive_path
        """Full path to the created archive."""

    @property
    def archive_size(self) -> int:
        """Archive size, in bytes."""
        return os.stat(self.archive_path).st_size if self.successful else None

    @property
    def successful(self) -> bool:
        """True, if the archive is successfully created."""
        return self.proc.successful and self.folder and self.archive_path and os.path.exists(self.archive_path)

    @property
    def archival_speed(self) -> int:
        """Archival speed, in bytes per second."""
        return int(self.archive_size // self.proc.elapsed.total_seconds()) if self.successful else 0
