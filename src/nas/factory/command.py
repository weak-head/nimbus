from __future__ import annotations

from abc import ABC, abstractmethod

from nas.cmd import Backup, Down, Up
from nas.cmd.abstract import Command
from nas.config import Config
from nas.factory.component import ComponentFactory
from nas.provider.abstract import DictionaryProvider


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

    def __init__(self, config: Config, component_factory: ComponentFactory) -> None:
        self._config = config
        self._component_factory = component_factory

    def create_backup(self) -> Command:
        destination = self._config.commands.backup.destination
        known_folders = self._config.commands.backup.groups

        provider = DictionaryProvider(known_folders)
        archiver = self._component_factory.create_archiver()
        uploader = self._component_factory.create_uploader()

        return Backup(destination, provider, archiver, uploader)

    def create_up(self) -> Command:
        service_provider = self._component_factory.create_service_provider()
        factory = self._component_factory.create_service_factory()
        return Up(service_provider, factory)

    def create_down(self) -> Command:
        service_provider = self._component_factory.create_service_provider()
        factory = self._component_factory.create_service_factory()
        return Down(service_provider, factory)
