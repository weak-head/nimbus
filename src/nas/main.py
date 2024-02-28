"""
This is the main entry point for automation of all most common
operations for datasets, docker and housekeeping.
"""

import logging
import os
import sys
from datetime import datetime

from nas.cli.parser import create_parser
from nas.report.format import Formatter
from nas.report.writer import LogWriter
from nas.utils.config import load_config


def main() -> int:
    """Main entry point."""

    # --
    # -- Load config
    config = load_config()
    if config is None:
        print(
            "The default config file (~./nas/config.yaml) is not found.",
            file=sys.stderr,
        )
        return 126  # Command invoked cannot execute

    # --
    # -- Configure log writer and write startup header
    configure_log()
    write_startup_header()

    # --
    # -- Create CLI parser, parse CLI input and execute command
    parser = create_parser(config)
    try:
        args = parser.parse_args()
        args.func(args, config)
    except AttributeError:
        parser.print_help()

    return 0


def configure_log() -> None:
    """Initialize logging subsystem."""

    # --
    # Log folder
    log_folder = "~/.nas/log"
    log_folder = os.path.abspath(os.path.expanduser(log_folder))
    os.makedirs(log_folder, exist_ok=True)

    # --
    # Log file
    today = datetime.today().strftime("%Y-%m-%d")
    log_file = f"{today}.log"
    log_path = os.path.join(log_folder, log_file)

    # --
    # Log config
    logging.basicConfig(
        filename=log_path,
        encoding="utf-8",
        level=logging.INFO,
        format="%(message)s",
    )

    # --
    # Disable log output for particular loggers
    disabled_loggers = [
        "botocore",
        "boto3",
        "boto",
        "s3transfer",
    ]
    for name in disabled_loggers:
        logging.getLogger(name).setLevel(logging.CRITICAL)


def write_startup_header() -> None:
    """Writes startup header."""

    # --
    # Information to include
    command_line = (" ".join(sys.argv)).strip()
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # --
    # Log header
    log = LogWriter(Formatter())
    log.out()
    log.out("=" * 80)
    log.out(f"== {now}")
    log.out(f"== {command_line}")
    log.out()
