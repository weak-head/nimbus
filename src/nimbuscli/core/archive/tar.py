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

    def __init__(self, compressor: str = None):
        """
        Creates a new instance of the TarArchiver.

        :param compressor: Data compressor. One of [ bz2 | gz | xz ].
        """

        if compressor is not None:
            if compressor not in ("bz2", "gz", "xz"):
                raise ValueError("Compressor should be one of: 'bz2', 'gz' or 'xz'.")

        self._compressor = compressor

    def __repr__(self) -> str:
        params = [f"cmp='{self._compressor}'"]
        return "TarArchiver(" + ", ".join(params) + ")"

    @property
    def extension(self) -> str:
        return "tar" if self._compressor is None else f"tar.{self._compressor}"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        started = datetime.now()
        mode = "w" if self._compressor is None else f"w:{self._compressor}"
        with tarfile.open(archive, mode) as tar:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_name = os.path.relpath(file_path, directory)
                    tar.add(file_path, arcname=file_name)
        return ArchivalStatus(directory, archive, started, datetime.now())
