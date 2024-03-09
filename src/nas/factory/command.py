from __future__ import annotations

from abc import ABC, abstractmethod

from nas.cmd import Backup, Down, Up
from nas.cmd.abstract import Command
from nas.config import Config
from nas.factory.component import ComponentFactory
from nas.provider.backup import BackupProvider


class CommandFactory(ABC):
    """
    tbd
    """

    @abstractmethod
    def create_backup(self) -> Command:
        pass

    @abstractmethod
    def create_up(self) -> Command:
        pass

    @abstractmethod
    def create_down(self) -> Command:
        pass


class CfgCommandFactory(CommandFactory):

    def __init__(self, config: Config, components: ComponentFactory) -> None:
        self._config = config
        self._components = components

    def create_backup(self) -> Command:
        cfg = self._config.commands.backup
        return Backup(
            cfg.destination,
            BackupProvider(cfg.directories),
            self._components.create_archiver(cfg.archiver),
            self._components.create_uploader(cfg.uploader),
        )

    def create_up(self) -> Command:
        return Up(
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )

    def create_down(self) -> Command:
        return Down(
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )
