from __future__ import annotations

from abc import ABC, abstractmethod

from nimbus.cmd import Backup, Down, Up
from nimbus.cmd.abstract import Command
from nimbus.config import Config
from nimbus.factory.component import ComponentFactory
from nimbus.provider.backup import BackupProvider


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
        cfg = self._config.backup
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
