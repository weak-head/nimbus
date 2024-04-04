from __future__ import annotations

from abc import ABC, abstractmethod

from nimbus.config import Config
from nimbus.core.archiver import Archiver, RarArchiver
from nimbus.core.runner import Runner, SubprocessRunner
from nimbus.core.uploader import AwsUploader, Uploader
from nimbus.factory.service import ServiceFactory
from nimbus.provider.secrets import Secrets, SecretsProvider
from nimbus.provider.service import ServiceProvider


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
    def create_service_provider(self) -> ServiceProvider:
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
        cfg = self._config.archivers[profile]

        if not cfg:
            return None

        if cfg.provider == "rar":
            return RarArchiver(
                self.create_runner(),
                cfg.password,
            )

        return None

    def create_uploader(self, profile: str) -> Uploader:
        cfg = self._config.uploaders[profile]

        if not cfg:
            return None

        if cfg.provider == "aws":
            return AwsUploader(
                cfg.access_key,
                cfg.secret_key,
                cfg.bucket,
                cfg.storage_class,
            )

        return None

    def create_secrets(self) -> Secrets:
        return Secrets(SecretsProvider(self._config.secrets))

    def create_service_provider(self) -> ServiceProvider:
        return ServiceProvider(self._config.services.directories)

    def create_service_factory(self) -> ServiceFactory:
        return ServiceFactory(
            self.create_runner(),
            self.create_secrets(),
        )
