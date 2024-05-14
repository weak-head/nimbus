from argparse import ArgumentParser, Namespace
from importlib import metadata


def parse_args(args: list[str]) -> Namespace | None:
    parser = create_parser()
    if not args:
        parser.print_help()
        return None
    try:
        return parser.parse_args(args)
    except AttributeError:
        parser.print_help()
    return None


def create_parser() -> ArgumentParser:
    parser = ArgumentParser("ni")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {metadata.version('nimbuscli')}",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="overwrite config location",
    )
    commands = parser.add_subparsers(dest="command")

    # -- Up
    up = commands.add_parser("up")
    up.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="glob patterns to filter services",
    )

    # -- Down
    down = commands.add_parser("down")
    down.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="glob patterns to filter services",
    )

    # -- Backup
    backup = commands.add_parser("backup")
    backup.add_argument(
        "selectors",
        nargs="*",
        default="",
        help="glob patterns to filter directory groups",
    )

    return parser
