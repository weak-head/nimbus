from __future__ import annotations

from abc import ABC, abstractmethod

from nas.config import Config
from nas.core.archiver import Archiver, RarArchiver
from nas.core.runner import Runner, SubprocessRunner
from nas.core.uploader import AwsUploader, Uploader
from nas.factory.secrets import Secrets
from nas.factory.service import ServiceFactory
from nas.provider.abstract import DictionaryProvider, DirectoryProvider, Provider


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
