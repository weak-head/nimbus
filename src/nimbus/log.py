from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

from logdecorator import log_on_end

from nimbus.config import Config


class LogConfig:

    def __init__(self, level: str | int, location: str, stdout: bool) -> None:
        self.level = level
        self.location = location
        self.stdout = stdout

    def __repr__(self):
        r = [
            f"[ {self.level} ",
            f"| {self.location} ",
            "| STDOUT ]" if self.stdout else "]",
        ]
        return "".join(r)


@log_on_end(logging.DEBUG, "Logger has been configured: {result!r}")
def setup_logger(config: Config) -> LogConfig | None:
    try:
        cfg = parse_config(config)

        log_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)-5.5s] - %(message)s",
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(cfg.level)

        today = datetime.now().strftime("%Y-%m-%d")
        log_dir = os.path.abspath(os.path.expanduser(cfg.location))
        log_file = os.path.join(log_dir, f"{today}.log")
        os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        if cfg.stdout:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)

        for name in ["botocore", "boto3", "boto", "s3transfer"]:
            logging.getLogger(name).setLevel(logging.CRITICAL)

        return cfg

    except Exception:  # pylint: disable=broad-exception-caught
        logging.getLogger().setLevel(logging.CRITICAL)
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)

    return None


def parse_config(config: Config) -> LogConfig:
    cfg = LogConfig(logging.INFO, "~/.nimbus/logs", False)

    if not config.logs:
        return cfg

    if config.logs.level:
        cfg.level = config.logs.level
    if config.logs.location:
        cfg.location = config.logs.location
    if config.logs.stdout:
        cfg.stdout = config.logs.stdout

    return cfg
