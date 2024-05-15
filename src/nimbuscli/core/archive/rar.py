import logging

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver
from nimbuscli.core.execute import CompletedProcess, Runner


class RarArchiver(Archiver):
    """
    Creates a password protected archive using 'WinRar'.
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

        if password is not None and password == "":
            raise ValueError("If password is specified, it cannot be empty string.")

        if compression is not None and not 0 <= compression <= 5:
            raise ValueError("Compression should be either None or in [0-5] range.")

        if recovery is not None and not 0 <= recovery <= 1000:
            raise ValueError("Recovery should be either None or in [0-1000] range.")

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

    @property
    def extension(self) -> str:
        return "rar"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        # It is expected that 'rar' executable
        # is available in a system PATH.
        cmd = self._generate_cmd(directory, archive)
        proc = self._runner.execute(cmd)
        return RarArchivalStatus(proc, directory, archive)

    def _generate_cmd(self, directory: str, archive: str) -> list[str]:
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

        cmd.extend([archive, directory])
        return cmd


class RarArchivalStatus(ArchivalStatus):

    def __init__(self, proc: CompletedProcess, directory: str, archive: str):
        super().__init__(directory, archive)
        self.started = proc.started
        self.completed = proc.completed
        self.proc = proc

    @property
    def success(self) -> bool:
        return all([self.proc.success, super().success])
