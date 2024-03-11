from argparse import ArgumentParser, Namespace
from typing import Callable


def parse_args(
    args: list[str],
    func_up: Callable,
    func_down: Callable,
    func_backup: Callable,
) -> Namespace | None:

    parser = create_parser(
        func_up,
        func_down,
        func_backup,
    )

    if not args:
        parser.print_help()
        return None

    try:
        return parser.parse_args(args)
    except AttributeError:
        parser.print_help()

    return None


def create_parser(
    func_up: Callable,
    func_down: Callable,
    func_backup: Callable,
) -> ArgumentParser:

    parser = ArgumentParser("nas")
    parser.add_argument("--config", dest="config_path", default=None)
    commands = parser.add_subparsers()

    # -- Up
    up = commands.add_parser("up")
    up.add_argument("selectors", nargs="*", default="")
    up.set_defaults(func=func_up)

    # -- Down
    down = commands.add_parser("down")
    down.add_argument("selectors", nargs="*", default="")
    down.set_defaults(func=func_down)

    # -- Backup
    backup = commands.add_parser("backup")
    backup.add_argument("selectors", nargs="*", default="")
    backup.set_defaults(func=func_backup)

    return parser
