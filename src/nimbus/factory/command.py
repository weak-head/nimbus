from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_error, log_on_start

from nimbus.cmd import Backup, Down, Up
from nimbus.cmd.abstract import Command
from nimbus.config import Config
from nimbus.factory.component import ComponentFactory
from nimbus.provider.backup import BackupProvider


class CommandFactory(ABC):
    """
    Abstract command factory.
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

    @log_on_start(logging.DEBUG, "Creating Backup command")
    @log_on_error(logging.ERROR, "Failed to create Backup command: {e!r}", on_exceptions=Exception)
    def create_backup(self) -> Command:
        cfg = self._config.commands.backup
        return Backup(
            cfg.destination,
            BackupProvider(cfg.directories),
            self._components.create_archiver(cfg.archive),
            self._components.create_uploader(cfg.upload),
        )

    @log_on_start(logging.DEBUG, "Creating Up command")
    @log_on_error(logging.ERROR, "Failed to create Up command: {e!r}", on_exceptions=Exception)
    def create_up(self) -> Command:
        return Up(
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )

    @log_on_start(logging.DEBUG, "Creating Down command")
    @log_on_error(logging.ERROR, "Failed to create Down command: {e!r}", on_exceptions=Exception)
    def create_down(self) -> Command:
        return Down(
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )
