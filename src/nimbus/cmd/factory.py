from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_error, log_on_start

from nimbus.cmd.backup import Backup
from nimbus.cmd.command import Command
from nimbus.cmd.deploy import Down, Up
from nimbus.config import Config
from nimbus.factory.component import ComponentFactory
from nimbus.provider.backup import BackupProvider


class CommandFactory(ABC):
    """
    Abstract command factory.
    """

    @abstractmethod
    def create_backup(self, selectors: list[str]) -> Command:
        pass

    @abstractmethod
    def create_up(self, selectors: list[str]) -> Command:
        pass

    @abstractmethod
    def create_down(self, selectors: list[str]) -> Command:
        pass


class CfgCommandFactory(CommandFactory):

    def __init__(self, config: Config, components: ComponentFactory) -> None:
        self._config = config
        self._components = components

    @log_on_start(logging.DEBUG, "Creating Backup command")
    @log_on_error(logging.ERROR, "Failed to create Backup command: {e!r}", on_exceptions=Exception)
    def create_backup(self, selectors: list[str]) -> Command:
        cfg = self._config.commands.backup
        return Backup(
            selectors,
            cfg.destination,
            BackupProvider(cfg.directories),
            self._components.create_archiver(cfg.archive),
            self._components.create_uploader(cfg.upload),
        )

    @log_on_start(logging.DEBUG, "Creating Up command")
    @log_on_error(logging.ERROR, "Failed to create Up command: {e!r}", on_exceptions=Exception)
    def create_up(self, selectors: list[str]) -> Command:
        return Up(
            selectors,
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )

    @log_on_start(logging.DEBUG, "Creating Down command")
    @log_on_error(logging.ERROR, "Failed to create Down command: {e!r}", on_exceptions=Exception)
    def create_down(self, selectors: list[str]) -> Command:
        return Down(
            selectors,
            self._components.create_service_provider(),
            self._components.create_service_factory(),
        )
