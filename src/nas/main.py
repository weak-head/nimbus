import logging
import os
import sys
from datetime import datetime

from nas.cli.parser import parse_args
from nas.cli.runner import CommandRunner
from nas.config import Config, resolve_config, safe_load, SEARCH_PATHS
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

    return execute(CommandRunner(), sys.argv[1:])


def execute(runner: CommandRunner, args: list[str]) -> int:
    ns = parse_args(args, runner)
    if not ns:
        return ExitCode.INCORRECT_USAGE

    config_path = resolve_config(ns.config_path)
    if not config_path:
        print(
            "The application could not locate the configuration file.\n"
            "Please ensure that the configuration file exists in the specified location.\n"
            "Locations that were checked:",
            file=sys.stderr,
        )
        for path in [ns.config_path] if ns.config_path else SEARCH_PATHS:
            print(f"- {path}", file=sys.stderr)
        return ExitCode.CMD_NOT_FOUND

    config = safe_load(config_path)
    if not config:
        print(
            "The application encountered an issue while attempting to load the configuration file.\n"
            "The provided file format is invalid. Please follow these steps to resolve the problem:\n"
            "  1. Ensure that the configuration file adheres to the expected format.\n"
            "  2. Inspect the configuration file for any syntax errors, missing brackets, or other inconsistencies.\n"
            "  3. Confirm that the file encoding matches the expected UTF-8 encoding.\n"
            "  4. Ensure that the application has read access to the configuration file.\n"
            "  5. Verify that the file content aligns with the expected structure.\n"
            "If you continue to encounter this issue, consult the documentation.",
            file=sys.stderr,
        )
        return ExitCode.UNABLE_TO_EXECUTE

    factory = build_factory(config)
    if not factory:
        print(
            "The application encountered an issue during startup due to an invalid configuration.\n"
            "Please follow these steps to troubleshoot:\n"
            "  1. Review the configuration file for any syntax errors, missing elements, or incorrect values.\n"
            "  2. Confirm that the configuration file adheres to the expected format.\n"
            "  3. Verify that any external dependencies referenced in the configuration are correctly configured.\n"
            "If the issue persists, consult the documentation.",
            file=sys.stderr,
        )
        return ExitCode.UNABLE_TO_EXECUTE
    runner.set_factory(factory)

    runner.run_default(ns)
    return ExitCode.SUCCESS


def build_factory(config: Config) -> CommandFactory:
    try:
        return CfgCommandFactory(
            config,
            CfgComponentFactory(config),
        )
    except AttributeError:
        return None


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
