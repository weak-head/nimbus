import logging
import os

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver
from nimbuscli.core.runner import Runner


class RarArchiver(Archiver):
    """
    Create a password protected archive using 'WinRar'.
    https://www.win-rar.com/download.html
    """

    def __init__(
        self,
        runner: Runner,
        password: str | None = None,
        compression: int | None = None,
        recovery: int | None = None,
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
            if not 0 <= compression <= 5:
                raise ValueError("Compression should be in range [0-5]")

        if recovery is not None:
            if not 0 <= recovery <= 1000:
                raise ValueError("Recovery should be in range [0-1000]")

        self._runner = runner
        self._password = password
        self._compression = compression
        self._recovery = recovery

    def __repr__(self) -> str:
        params = [
            f"'{self._runner.__class__.__name__}'",
            f"pwd='{self._password}'",
            f"cmp='{self._compression}'",
            f"rec='{self._recovery}'",
        ]
        return "RarArchiver(" + ", ".join(params) + ")"

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
        # fmt: off
        cmd = [
            "rar",
            "a",        # Archive
            "-r",       # Recursive
            "-ol",      # Process symbolic links as the link
            "-htb",     # Use BLAKE2 hash
            "-md128m",  # Dictionary size: 128 MB
            "-qo+",     # Add quick open information
            "-idq",     # Silent mode
            "-ep1",     # Exclude prefix from file names
            "-k",       # Lock archive
            "-y",       # Yes to all questions
        ]
        # fmt: on

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
