import os.path
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from nas.config import Config
from nas.report.formatter import Formatter
from nas.report.reporter import Reporter, ReportWriter
from nas.report.writer import TextWriter, Writer


class ReporterFactory(ABC):

    @abstractmethod
    def create_formatter(self) -> Formatter:
        pass

    @abstractmethod
    def create_writer(self) -> Writer:
        pass

    @abstractmethod
    def create_reporter(self) -> Reporter:
        pass


class CfgReporterFactory(ReporterFactory):

    def __init__(self, config: Config) -> None:
        self._config = config

    def report_file(self, extension: str) -> str:
        cfg = self._config.report

        directory = Path(cfg.location).absolute().as_posix()
        os.makedirs(directory, exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return os.path.join(directory, f"{now}.{extension}")

    def create_formatter(self) -> Formatter:
        return Formatter()

    def create_writer(self) -> Writer:
        cfg = self._config.report

        if not cfg:
            return None

        if cfg.format == "txt":
            return TextWriter(
                self.report_file("txt"),
                self.create_formatter(),
            )

        return None

    def create_reporter(self) -> Reporter:
        writer = self.create_writer()

        if not writer:
            return None

        return ReportWriter(writer)
