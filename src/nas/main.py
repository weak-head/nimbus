import logging
import os
import sys
from datetime import datetime

from nas.cli.parser import parse_args
from nas.cli.runner import backup, down, up
from nas.config import Config, resolve_config, safe_load
from nas.factory.command import CfgCommandFactory, CommandFactory
from nas.factory.component import CfgComponentFactory
from nas.report.format import Formatter
from nas.report.writer import LogWriter


class ExitCode:

    SUCCESS = 0
    """Successfully finished."""

    INCORRECT_USAGE = 2
    """Incorrect command (or argument) usage."""

    UNABLE_TO_EXECUTE = 126
    """Command invoked cannot execute."""

    CMD_NOT_FOUND = 127
    """Command not found, or PATH error."""


def main() -> int:

    configure_log()
    write_startup_header()

    return execute(sys.argv[1:])


def execute(args: list[str]) -> int:
    ns = parse_args(args, up, down, backup)
    if not ns:
        return ExitCode.INCORRECT_USAGE

    config_path = resolve_config(ns.config_path)
    if not config_path:
        file = ns.config_path if ns.config_path else "~/.nas/config.yml"
        print(
            f'The configuration file "{file}" is not found.',
            file=sys.stderr,
        )
        return ExitCode.CMD_NOT_FOUND

    config = safe_load(config_path)
    if not config:
        print(
            "Configuration load failed: Invalid file format.",
            file=sys.stderr,
        )
        return ExitCode.UNABLE_TO_EXECUTE

    factory = build_factory(config)
    ns.func(ns, factory)

    return ExitCode.SUCCESS


def build_factory(config: Config) -> CommandFactory:
    return CfgCommandFactory(config, CfgComponentFactory(config))


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
