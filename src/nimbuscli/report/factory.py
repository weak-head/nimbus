import logging
import os.path
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbuscli.config import Config
from nimbuscli.report.reporter import CompositeReporter, Reporter, ReportWriter
from nimbuscli.report.writer import TextWriter, Writer


class ReporterFactory(ABC):
    """
    Abstract reporter factory.
    """

    @abstractmethod
    def create_reporter(self) -> Reporter:
        pass


class CfgReporterFactory(ReporterFactory):
    """
    Reporter factory that uses the provided configuration
    for construction of a Reporter.
    """

    def __init__(self, config: Config) -> None:
        self._cfg = config

    @log_on_start(logging.DEBUG, "Selecting report file path: [{extension!s}]")
    @log_on_end(logging.DEBUG, "Selected report file path: {result!s}")
    @log_on_error(logging.ERROR, "Failed to select report file: {e!r}", on_exceptions=Exception)
    def report_file(self, path: str, extension: str) -> str:
        path = path if path else "~/.nimbus/reports"

        directory = Path(path).expanduser().as_posix()
        os.makedirs(directory, exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(directory, f"{now}.{extension}")

    def text_writer(self, file) -> Writer:
        return TextWriter(
            file,
            indent_char=" ",
            section_indent=4,
            column_width=30,
        )

    @log_on_start(logging.DEBUG, "Creating Writer: [{kind!s}]")
    @log_on_end(logging.DEBUG, "Created Writer: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Writer: {e!r}", on_exceptions=Exception)
    def create_writer(self, kind: str, directory: str = None) -> Writer:
        match kind:
            case "stdout":
                return self.text_writer(sys.stdout)
            case "txt":
                return self.text_writer(self.report_file(directory, "txt"))
            case _:
                return None

    @log_on_start(logging.DEBUG, "Creating Reporter")
    @log_on_end(logging.DEBUG, "Created Reporter: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Reporter: {e!r}", on_exceptions=Exception)
    def create_reporter(self) -> Reporter:
        reporters = []

        # If 'observability' section is omitted,
        # or 'observability.reports' is not specified
        # the reporting to a file would be disabled.
        if cfg := self._cfg.nested("observability.reports"):
            writer = self.create_writer(cfg.format, cfg.directory)
            reporters.append(ReportWriter(writer))

        if writer := self.create_writer("stdout"):
            reporters.append(ReportWriter(writer, details=False))

        return CompositeReporter(reporters)
