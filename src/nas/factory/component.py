from __future__ import annotations

from abc import ABC, abstractmethod

from nas.config import Config
from nas.core.archiver import Archiver, RarArchiver
from nas.core.runner import Runner, SubprocessRunner
from nas.core.uploader import AwsUploader, Uploader
from nas.factory.secrets import Secrets
from nas.factory.service import ServiceFactory
from nas.provider.secrets import SecretsProvider
from nas.provider.service import ServiceProvider


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
        profile_cfg = self._config.archivers[profile]

        if not profile_cfg:
            return None

        if profile_cfg.provider == "rar":
            return RarArchiver(
                self.create_runner(),
                profile_cfg.password,
            )

        return None

    def create_uploader(self, profile: str) -> Uploader:
        profile_cfg = self._config.uploaders[profile]

        if not profile_cfg:
            return None

        if profile_cfg.provider == "aws":
            return AwsUploader(
                profile_cfg.access_key,
                profile_cfg.secret_key,
                profile_cfg.bucket,
                profile_cfg.storage_class,
            )

        return None

    def create_secrets(self) -> Secrets:
        return Secrets(SecretsProvider({}))

    def create_service_provider(self) -> ServiceProvider:
        return ServiceProvider(self._config.services.directories)

    def create_service_factory(self) -> ServiceFactory:
        return ServiceFactory(
            self.create_runner(),
            self.create_secrets(),
        )
