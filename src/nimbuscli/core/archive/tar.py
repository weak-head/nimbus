import logging

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver


class TarArchiver(Archiver):
    """
    Creates tar archives, including those using gzip, bz2 and lzma compression.
    """

    def __init__(self, compressor: str = None):
        """
        Creates a new instance of the TarArchiver.
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
        return "tar"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        pass
