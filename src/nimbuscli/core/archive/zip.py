import logging
import os
import zipfile
from datetime import datetime

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver


class ZipArchiver(Archiver):
    """
    Creates zip archives, including ZIP64 extensions.
    """

    def __init__(self, compression: str | None = None):
        """
        Creates a new instance of the ZipArchiver.

        :param compression: Data compression method.
            You can specify the following values:
                - gz - Creates zipfile with gzip compression.
                - xz - Creates zipfile with lzma compression.
                - bz2 - Creates zipfile with bzip2 compression.
        """

        if compression not in (None, "bz2", "gz", "xz"):
            raise ValueError("Compression should be None or one of: 'bz2', 'gz' or 'xz'.")

        self._compression: int = {
            None: zipfile.ZIP_STORED,
            "bz2": zipfile.ZIP_BZIP2,
            "gz": zipfile.ZIP_DEFLATED,
            "xz": zipfile.ZIP_LZMA,
        }[compression]

    def __repr__(self) -> str:
        params = [f"cmp='{self._compression}'"]
        return "ZipArchiver(" + ", ".join(params) + ")"

    @property
    def extension(self) -> str:
        return "zip"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        started = datetime.now()
        with zipfile.ZipFile(archive, "w", self._compression) as zipf:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_name = os.path.relpath(file_path, directory)
                    zipf.write(file_path, arcname=file_name)
        return ArchivalStatus(directory, archive, started, datetime.now())
