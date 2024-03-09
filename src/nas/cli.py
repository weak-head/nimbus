from argparse import ArgumentParser

from nas.config import Config


def create_parser(config: Config) -> ArgumentParser:
    parser = ArgumentParser("nas")
    subparsers = parser.add_subparsers()

    up_parser(subparsers.add_parser("up"), config)
    down_parser(subparsers.add_parser("down"), config)
    backup_parser(subparsers.add_parser("backup"), config)

    return parser


def up_parser(parser: ArgumentParser, config: Config):
    parser.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="Services that should be started",
    )

    parser.set_defaults(func=None)


def down_parser(parser: ArgumentParser, config: Config):
    parser.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="Services that should be stopped",
    )

    parser.set_defaults(func=None)


def backup_parser(parser: ArgumentParser, config: Config):
    parser.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="Multiple patterns to match against the configured backup groups.",
    )

    parser.set_defaults(func=None)
