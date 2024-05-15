import logging
import zipfile
from typing import ContextManager

from logdecorator import log_on_error

from nimbuscli.core.archive.archiver import FSArchiver


class ZipArchiver(FSArchiver):
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

    @log_on_error(logging.ERROR, "Failed init archiver: {e!r}", on_exceptions=Exception)
    def init_archiver(self, archive: str) -> ContextManager:
        return zipfile.ZipFile(archive, "w", self._compression)

    @log_on_error(logging.ERROR, "Failed to add file: {e!r}", on_exceptions=Exception)
    def add_file(self, arc: zipfile.ZipFile, file_path: str, file_name: str) -> None:
        arc.write(file_path, arcname=file_name)
