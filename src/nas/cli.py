from argparse import ArgumentParser, Namespace

from nas.factory.command import CommandFactory
from nas.config import Config


class CLI:

    def __init__(self, factory: CommandFactory):
        self._factory = factory

    def exec(self, config: Config, args: list[str]):
        parser = self._create_parser()
        try:
            parsed = parser.parse_args(args)
            parsed.func(parsed, config)
        except AttributeError:
            parser.print_help()

    def _up(self, args: Namespace, config: Config):
        pass

    def _down(self, args: Namespace, config: Config):
        pass

    def _backup(self, args: Namespace, config: Config):
        pass

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser("nas")
        commands = parser.add_subparsers()

        # -- Up
        up = commands.add_parser("up")
        up.add_argument("selectors", nargs="*", default="")
        up.set_defaults(func=self._up)

        # -- Down
        down = commands.add_parser("down")
        down.add_argument("selectors", nargs="*", default="")
        down.set_defaults(func=self._down)

        # -- Backup
        backup = commands.add_parser("backup")
        backup.add_argument("selectors", nargs="*", default="")
        backup.set_defaults(func=self._backup)

        return parser
