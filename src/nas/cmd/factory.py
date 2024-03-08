from __future__ import annotations

from abc import ABC, abstractmethod

from nas.cmd import Backup, Down, Up
from nas.cmd.abstract import Command
from nas.config import Config
from nas.core.archiver import Archiver, RarArchiver
from nas.core.provider import DictionaryProvider, DirectoryProvider, Provider
from nas.core.runner import Runner, SubprocessRunner
from nas.core.secrets import Secrets
from nas.core.service import ServiceFactory
from nas.core.uploader import AwsUploader, Uploader


class ComponentFactory(ABC):
    """
    tbd
    """

    @abstractmethod
    def create_runner(self) -> Runner:
        pass

    @abstractmethod
    def create_archiver(self, profile: str) -> Archiver:
        pass

    @abstractmethod
    def create_uploader(self, profile: str) -> Uploader:
        pass

    @abstractmethod
    def create_secrets(self) -> Secrets:
        pass

    @abstractmethod
    def create_service_provider(self) -> Provider:
        pass

    @abstractmethod
    def create_service_factory(self) -> ServiceFactory:
        pass


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


class CfgComponentFactory(ComponentFactory):

    def __init__(self, config: Config) -> None:
        self._config = config

    def create_runner(self) -> Runner:
        return SubprocessRunner()

    def create_archiver(self, profile: str) -> Archiver:
        rar_password = self._config.integrations.rar.password
        runner = self.create_runner()
        return RarArchiver(runner, rar_password)

    def create_uploader(self, profile: str) -> Uploader:
        upload_enabled = self._config.commands.backup.upload.enabled
        if not upload_enabled:
            return None

        match self._config.commands.backup.upload.provider:
            case "aws":
                aws_access_key = self._config.integrations.aws.access_key
                aws_secret_key = self._config.integrations.aws.secret_key
                aws_bucket = self._config.commands.backup.upload.aws.bucket
                aws_storage = self._config.commands.backup.upload.aws.storage_class

                return AwsUploader(aws_access_key, aws_secret_key, aws_bucket, aws_storage)

    def create_secrets(self) -> Secrets:
        secrets_dict = self._config.commands.deploy.secrets
        secrets_provider = DictionaryProvider(secrets_dict)
        return Secrets(secrets_provider)

    def create_service_provider(self) -> Provider:
        services_root = self._config.commands.deploy.services
        return DirectoryProvider(services_root)

    def create_service_factory(self) -> ServiceFactory:
        runner = self.create_runner()
        secrets = self.create_secrets()
        return ServiceFactory(runner, secrets)


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
