import os.path
import sys
from argparse import ArgumentParser, Namespace

import yaml

from nas.config import Config
from nas.factory.command import CfgCommandFactory, CommandFactory
from nas.factory.component import CfgComponentFactory


class CLI:

    INCORRECT_USAGE = 2
    """Incorrect command (or argument) usage"""

    UNABLE_TO_EXECUTE = 126
    """Command invoked cannot execute."""

    CMD_NOT_FOUND = 127
    """Command not found, or PATH error"""

    def exec(self, args: list[str]) -> int:
        ns = self._parse_args(args)
        if not ns:
            return CLI.INCORRECT_USAGE

        config_path = self._search_config(ns.config_path)
        if not config_path:
            file = ns.config_path if ns.config_path else "~/.nas/config.yml"
            print(
                f'The configuration file "{file}" is not found.',
                file=sys.stderr,
            )
            return CLI.CMD_NOT_FOUND

        config = self._load_config(config_path)
        if not config:
            print(
                "Configuration load failed: Invalid file format.",
                file=sys.stderr,
            )
            return CLI.UNABLE_TO_EXECUTE

        factory = self._build_factory(config)
        ns.func(ns, factory)

        return 0

    def _up(self, args: Namespace, factory: CommandFactory):
        factory.create_up().execute(args.selectors)

    def _down(self, args: Namespace, factory: CommandFactory):
        factory.create_down().execute(args.selectors)

    def _backup(self, args: Namespace, factory: CommandFactory):
        factory.create_backup().execute(args.selectors)

    def _build_factory(self, config: Config) -> CommandFactory:
        return CfgCommandFactory(
            config,
            CfgComponentFactory(config),
        )

    def _search_config(self, file_path: str) -> str:
        # Default search paths for the configuration location.
        # The order in the list defines the search and load priority.
        search_paths = [
            "~/.nas/config.yml",
            "~/.nas/config.yaml",
        ]

        if file_path:
            search_paths = [file_path]

        for candidate in search_paths:
            resolved_path = os.path.abspath(os.path.expanduser(candidate))
            if os.path.exists(resolved_path):
                return resolved_path

        return None

    def _load_config(self, file_path: str) -> Config:
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                return Config(yaml.safe_load(file))
        except yaml.error.YAMLError:
            return None

    def _parse_args(self, args: list[str]) -> Namespace:
        parser = self._create_parser()

        if not args:
            parser.print_help()
            return None

        try:
            return parser.parse_args(args)
        except AttributeError:
            parser.print_help()
            return None

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser("nas")
        parser.add_argument("--config", dest="config_path", default=None)
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
