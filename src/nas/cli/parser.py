"""
CLI API parser with support of the following commands:
  - up [services...]
  - down [services...]
  - backup [groups...]
  - snapshot
"""

from argparse import ArgumentParser

from nas.cli.adapters import BackupAdapter, DownAdapter, SnapshotAdapter, UpAdapter
from nas.utils.config import Config


def create_parser(config: Config) -> ArgumentParser:
    """
    Create the root-level argument parser that delegates a
    parsing logic to a particular subparser.

    :param config: Application configuration.
    :return: Fully initialized argument parser.
    """
    parser = ArgumentParser("nas")
    subparsers = parser.add_subparsers()

    # -- Init subparsers
    up_parser(subparsers.add_parser("up"), config)
    down_parser(subparsers.add_parser("down"), config)
    backup_parser(subparsers.add_parser("backup"), config)
    snapshot_parser(subparsers.add_parser("snapshot"), config)

    return parser


def up_parser(parser: ArgumentParser, config: Config):
    """
    Initialize 'up' command parser.

    :param parser: The parser, that would be initialized as 'up' command.
    :param config: Application configuration.
    :return: None
    """

    # -- nargs:
    # --   n => exact count 'n'
    # --   ? => 0 or 1
    # --   + => 1+
    # --   * => 0+
    parser.add_argument(
        "services",
        nargs="*",
        default="",
        help="Services that should be started",
    )

    parser.set_defaults(func=UpAdapter.execute)


def down_parser(parser: ArgumentParser, config: Config):
    """
    Initialize 'down' command parser.

    :param parser: The parser, that would be initialized as 'down' command.
    :param config: Application configuration.
    :return: None
    """

    # -- nargs:
    # --   n => exact count 'n'
    # --   ? => 0 or 1
    # --   + => 1+
    # --   * => 0+
    parser.add_argument(
        "services",
        nargs="*",
        default="",
        help="Services that should be stopped",
    )

    parser.set_defaults(func=DownAdapter.execute)


def backup_parser(parser: ArgumentParser, config: Config):
    """
    Initialize 'backup' command parser.

    :param parser: The parser, that would be initialized as 'backup' command.
    :param config: Application configuration.
    :return: None
    """

    # -- nargs:
    # --   n => exact count 'n'
    # --   ? => 0 or 1
    # --   + => 1+
    # --   * => 0+
    parser.add_argument(
        "groups",
        nargs="*",
        default="",
        help="One or several groups to backup",
    )

    parser.set_defaults(func=BackupAdapter.execute)


def snapshot_parser(parser: ArgumentParser, config: Config):
    """
    Initialize 'snapshot' command parser.

    :param parser: The parser, that would be initialized as 'up' command.
    :param config: Application configuration.
    :return: None
    """

    parser.set_defaults(func=SnapshotAdapter.execute)
