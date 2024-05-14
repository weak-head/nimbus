import logging
import os
import tarfile
from datetime import datetime

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver


class TarArchiver(Archiver):
    """
    Creates tar archives, including those using gzip, bz2 and lzma compression.
    """

    def __init__(self, compression: str = None):
        """
        Creates a new instance of the TarArchiver.

        :param compressor: Data compression method.
            You can specify the following values:
                - gz - Creates Tarfile with gzip compression.
                - xz - Creates Tarfile with lzma compression.
                - bz2 - Creates Tarfile with bzip2 compression.
        """

        if compression is not None:
            if compression not in ("bz2", "gz", "xz"):
                raise ValueError("Compression should be None or one of: 'bz2', 'gz' or 'xz'.")

        self._compression = compression

    def __repr__(self) -> str:
        params = [f"cmp='{self._compression}'"]
        return "TarArchiver(" + ", ".join(params) + ")"

    @property
    def extension(self) -> str:
        return "tar" if self._compression is None else f"tar.{self._compression}"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        started = datetime.now()
        mode = "w" if self._compression is None else f"w:{self._compression}"
        with tarfile.open(archive, mode) as tar:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_name = os.path.relpath(file_path, directory)
                    tar.add(file_path, arcname=file_name)
        return ArchivalStatus(directory, archive, started, datetime.now())
