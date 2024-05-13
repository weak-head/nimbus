import logging

from logdecorator import log_on_end, log_on_start

from nimbuscli.core.archive.archiver import ArchivalStatus, Archiver


class TarArchiver(Archiver):

    def __init__(self):
        """
        Creates a new instance of the TarArchiver.
        """

    def __repr__(self) -> str:
        params = []
        return "TarArchiver(" + ", ".join(params) + ")"

    @property
    def extension(self) -> str:
        return "tar"

    @log_on_start(logging.INFO, "Archiving {directory!s} -> {archive!s}")
    @log_on_end(logging.INFO, "Archived [{result.success!s}]: {archive!s}")
    def archive(self, directory: str, archive: str) -> ArchivalStatus:
        pass
