import logging
import os.path
import sys

from strictyaml import YAMLError

from nimbuscli.cli import RunnerFactory, parse_args
from nimbuscli.cmd import CfgCommandFactory
from nimbuscli.config import load_config, resolve_config
from nimbuscli.log import setup_logger
from nimbuscli.notify import CfgNotifierFactory
from nimbuscli.report import CfgReporterFactory


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
    return execute(sys.argv[1:])


def execute(args: list[str]) -> int:
    ns = parse_args(args)
    if not ns:
        return ExitCode.INCORRECT_USAGE

    config_path, search_paths = resolve_config(ns.config_path)
    if not config_path:
        print(
            "The application could not locate the configuration file.\n"
            "Please ensure that the configuration file exists in the specified location.\n"
            "Locations that were checked:",
            file=sys.stderr,
        )
        for path in search_paths:
            print(f"- {os.path.expanduser(path)}", file=sys.stderr)
        return ExitCode.CMD_NOT_FOUND

    config = None
    try:
        config = load_config(config_path)
    except YAMLError:
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

    if setup_logger(config) is None:
        print(
            "-----------------  Configuration Alert: Logging Disabled  ---------------------\n"
            "  The application encountered an issue while attempting to configure logger.\n"
            "  Please follow these steps to resolve the problem:\n"
            "    1. Ensure that the configuration file adheres to the expected format.\n"
            "    2. Confirm that the application has write access to the log directory.\n"
            "  If the issue persists, consult the documentation.\n"
            "  The execution will continue, but the logging capabilities would be disabled.\n"
            "-------------------------------------------------------------------------------"
        )
    elif logging.root.level <= logging.DEBUG:
        print(
            "---------------  Security Alert: Debug Mode Active  ---------------------\n"
            "  Caution: The application is currently running in debug mode.\n"
            "  This setting may result in the logging of sensitive information,\n"
            "  including passwords, cloud keys, certificates, and access tokens.\n"
            "  Please ensure that this mode is enabled only in secure environments\n"
            "  and review the logs to prevent any data exposure.\n"
            "-------------------------------------------------------------------------"
        )

    try:
        factory = RunnerFactory(
            CfgCommandFactory(config),
            CfgReporterFactory(config),
            CfgNotifierFactory(config),
        )
        runner = factory.create_runner(ns)
        runner.execute()

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

    return ExitCode.SUCCESS
