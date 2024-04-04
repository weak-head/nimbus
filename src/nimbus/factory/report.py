import os.path
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from nimbus.config import Config
from nimbus.report.reporter import CompositeReporter, Reporter, ReportWriter
from nimbus.report.writer import TextWriter, Writer


class ReporterFactory(ABC):

    @abstractmethod
    def create_writer(self, kind: str) -> Writer:
        pass

    @abstractmethod
    def create_reporter(self) -> Reporter:
        pass


class CfgReporterFactory(ReporterFactory):

    def __init__(self, config: Config) -> None:
        self._config = config

    def report_file(self, extension: str) -> str:
        path = self._config.reports.location
        path = path if path else "~/.nas/reports"

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

    def create_writer(self, kind: str) -> Writer:
        match kind:
            case "stdout":
                return self.text_writer(sys.stdout)
            case "txt":
                return self.text_writer(self.report_file("txt"))
            case _:
                return None

    def create_reporter(self) -> Reporter:
        reporters = []

        if writer := self.create_writer("stdout"):
            reporters.append(ReportWriter(writer, details=False))

        if (kind := self._config.reports.format) and (writer := self.create_writer(kind)):
            reporters.append(ReportWriter(writer))

        return CompositeReporter(reporters)
