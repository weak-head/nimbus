from argparse import ArgumentParser, Namespace

from nimbus.cli.runner import Runner


def parse_args(args: list[str], runner: Runner) -> Namespace | None:

    parser = create_parser(runner)

    if not args:
        parser.print_help()
        return None

    try:
        return parser.parse_args(args)
    except AttributeError:
        parser.print_help()

    return None


def create_parser(runner: Runner) -> ArgumentParser:

    parser = ArgumentParser("ni")
    parser.add_argument("--config", dest="config_path", default=None)
    commands = parser.add_subparsers()

    # -- Up
    up = commands.add_parser("up")
    up.add_argument("selectors", nargs="*", default="")
    up.set_defaults(func=runner.up)

    # -- Down
    down = commands.add_parser("down")
    down.add_argument("selectors", nargs="*", default="")
    down.set_defaults(func=runner.down)

    # -- Backup
    backup = commands.add_parser("backup")
    backup.add_argument("selectors", nargs="*", default="")
    backup.set_defaults(func=runner.backup)

    return parser
