import logging
import os
import sys
from datetime import datetime

from nas.cli import CLI
from nas.report.format import Formatter
from nas.report.writer import LogWriter


def main() -> int:

    configure_log()
    write_startup_header()

    cli = CLI()
    return cli.exec(sys.argv[1:])


def configure_log() -> None:

    # --
    # Log directory
    log_dir = "~/.nas/log"
    log_dir = os.path.abspath(os.path.expanduser(log_dir))
    os.makedirs(log_dir, exist_ok=True)

    # --
    # Log file
    today = datetime.today().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.log")

    # --
    # Log config
    logging.basicConfig(
        filename=log_file,
        encoding="utf-8",
        level=logging.INFO,
        format="%(message)s",
    )

    # --
    # Disable log output for particular loggers
    for name in ["botocore", "boto3", "boto", "s3transfer"]:
        logging.getLogger(name).setLevel(logging.CRITICAL)


def write_startup_header() -> None:
    command_line = (" ".join(sys.argv)).strip()
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # -- header --
    log = LogWriter(Formatter())
    log.entry()
    log.entry("=" * 80)
    log.entry(f"== {now}")
    log.entry(f"== {command_line}")
    log.entry()
