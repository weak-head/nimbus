import logging
import tarfile
from typing import ContextManager

from logdecorator import log_on_error

from nimbuscli.core.archive.archiver import FSArchiver


class TarArchiver(FSArchiver):
    """
    Creates tar archives, including those using gzip, bz2 and lzma compression.
    """

    def __init__(self, compression: str | None = None):
        """
        Creates a new instance of the TarArchiver.

        :param compressor: Data compression method.
            You can specify the following values:
                - gz - Creates Tarfile with gzip compression.
                - xz - Creates Tarfile with lzma compression.
                - bz2 - Creates Tarfile with bzip2 compression.
        """

        if compression not in (None, "bz2", "gz", "xz"):
            raise ValueError("Compression should be None or one of: 'bz2', 'gz' or 'xz'.")

        self._compression = compression

    def __repr__(self) -> str:
        params = [f"cmp='{self._compression}'"]
        return "TarArchiver(" + ", ".join(params) + ")"

    @property
    def extension(self) -> str:
        return "tar" if self._compression is None else f"tar.{self._compression}"

    @log_on_error(logging.ERROR, "Failed init archiver: {e!r}", on_exceptions=Exception)
    def init_archiver(self, archive: str) -> ContextManager:
        mode = "w" if self._compression is None else f"w:{self._compression}"
        return tarfile.open(archive, mode)

    @log_on_error(logging.ERROR, "Failed to add file: {e!r}", on_exceptions=Exception)
    def add_file(self, arc: tarfile.TarFile, file_path: str, file_name: str) -> None:
        arc.add(file_path, arcname=file_name)
