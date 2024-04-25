import logging
import os.path
import sys

from logdecorator import log_on_error, log_on_start

from nimbus.cli.parser import parse_args
from nimbus.cli.runner import CommandRunner
from nimbus.config import SEARCH_PATHS, Config, resolve_config, safe_load
from nimbus.factory.command import CfgCommandFactory, CommandFactory
from nimbus.factory.component import CfgComponentFactory
from nimbus.factory.notification import CfgNotifierFactory, NotifierFactory
from nimbus.factory.report import CfgReporterFactory, ReporterFactory
from nimbus.log import setup_logger


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
    runner = CommandRunner()
    args = sys.argv[1:]
    return execute(runner, args)


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
            print(f"- {os.path.expanduser(path)}", file=sys.stderr)
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

    if cfg := setup_logger(config):
        if cfg is None:
            print(
                "The application encountered an issue while attempting to configure logger.\n"
                "Please follow these steps to resolve the problem:\n"
                "  1. Ensure that the configuration file adheres to the expected format.\n"
                "  2. Confirm that the application has write access to the log directory.\n"
                "If the issue persists, consult the documentation.\n"
                "The execution will continue, but the logging capabilities would be disabled.\n"
            )
        elif logging.root.level <= logging.DEBUG:
            print(
                "-------------  Security Alert: Debug Mode Active  -----------------------\n",
                "  Caution: The application is currently running in debug mode.\n",
                "  This setting may result in the logging of sensitive information,\n",
                "  including passwords, cloud keys, certificates, and access tokens.\n",
                "  Please ensure that this mode is enabled only in secure environments\n",
                "  and review the logs to prevent any data exposure.\n",
                "-------------------------------------------------------------------------",
            )

    try:
        runner.configure(
            build_command_factory(config),
            build_reporter_factory(config),
            build_notifier_factory(config),
        )
    except Exception:  # pylint: disable=broad-exception-caught
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

    runner.run_default(ns)
    return ExitCode.SUCCESS


@log_on_start(logging.DEBUG, "Building command factory")
@log_on_error(logging.ERROR, "Failed to create command factory: {e!r}", on_exceptions=Exception)
def build_command_factory(config: Config) -> CommandFactory:
    return CfgCommandFactory(
        config,
        CfgComponentFactory(config),
    )


@log_on_start(logging.DEBUG, "Building reporter factory")
@log_on_error(logging.ERROR, "Failed to create reporter factory: {e!r}", on_exceptions=Exception)
def build_reporter_factory(config: Config) -> ReporterFactory:
    return CfgReporterFactory(config)


@log_on_start(logging.DEBUG, "Building notifier factory")
@log_on_error(logging.ERROR, "Failed to create notifier factory: {e!r}", on_exceptions=Exception)
def build_notifier_factory(config: Config) -> NotifierFactory:
    return CfgNotifierFactory(config)
