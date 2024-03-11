import sys
from argparse import ArgumentParser, Namespace

from nas.config import Config
from nas.factory.builder import Builder
from nas.factory.command import CommandFactory


class CLI:

    def __init__(self, builder: Builder):
        self._builder: Builder = builder
        self._config: Config = None
        self._factory: CommandFactory = None

    def exec(self, args: list[str]) -> int:
        parser = self._create_parser()
        try:
            parsed = parser.parse_args(args)

            config = Config.load(parsed.config)
            if config is None:
                file = parsed.config if parsed.config else "~./nas/config.yaml"
                print(f'The configuration file "{file}" is not found.', file=sys.stderr)
                return 126

            # yaml.parser.ParserError

            self._config = config
            self._factory = self._builder.build_factory(config)
            parsed.func(parsed, config)
        except AttributeError:
            parser.print_help()

        return 0

    def _up(self, args: Namespace, config: Config):
        pass

    def _down(self, args: Namespace, config: Config):
        pass

    def _backup(self, args: Namespace, config: Config):
        pass

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser("nas")
        parser.add_argument("--config", dest="config", default=None)
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
