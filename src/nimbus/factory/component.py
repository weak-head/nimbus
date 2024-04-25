from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbus.config import Config
from nimbus.core.archiver import Archiver, RarArchiver
from nimbus.core.runner import Runner, SubprocessRunner
from nimbus.core.uploader import AwsUploader, Uploader
from nimbus.factory.service import ServiceFactory
from nimbus.provider.secrets import Secrets, SecretsProvider
from nimbus.provider.service import ServiceProvider


class ComponentFactory(ABC):
    """
    Abstract component factory.
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
    """
    Component factory that uses the provided configuration
    for components build up.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    @log_on_start(logging.DEBUG, "Creating Runner")
    @log_on_end(logging.DEBUG, "Created Runner: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Runner: {e!r}", on_exceptions=Exception)
    def create_runner(self) -> Runner:
        return SubprocessRunner()

    @log_on_start(logging.DEBUG, "Creating Archiver: [{profile!s}]")
    @log_on_end(logging.DEBUG, "Created Archiver: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Archiver: {e!r}", on_exceptions=Exception)
    def create_archiver(self, profile: str) -> Archiver:
        cfg = self._config.profiles.archive[profile]

        if not cfg:
            return None

        if cfg.provider == "rar":
            return RarArchiver(
                self.create_runner(),
                cfg.password,
                cfg.compression,
                cfg.recovery,
            )

        return None

    @log_on_start(logging.DEBUG, "Creating Uploader: [{profile!s}]")
    @log_on_end(logging.DEBUG, "Created Uploader: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Uploader: {e!r}", on_exceptions=Exception)
    def create_uploader(self, profile: str) -> Uploader:
        cfg = self._config.profiles.upload[profile]

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

    @log_on_start(logging.DEBUG, "Creating Secrets")
    @log_on_end(logging.DEBUG, "Created Secrets: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Secrets: {e!r}", on_exceptions=Exception)
    def create_secrets(self) -> Secrets:
        return Secrets(SecretsProvider(self._config.commands.deploy.secrets))

    @log_on_start(logging.DEBUG, "Creating Service Provider")
    @log_on_end(logging.DEBUG, "Created Service Provider: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service Provider: {e!r}", on_exceptions=Exception)
    def create_service_provider(self) -> ServiceProvider:
        return ServiceProvider(self._config.commands.deploy.discovery.directories)

    @log_on_start(logging.DEBUG, "Creating Service Factory")
    @log_on_end(logging.DEBUG, "Created Service Factory: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service Factory: {e!r}", on_exceptions=Exception)
    def create_service_factory(self) -> ServiceFactory:
        return ServiceFactory(
            self.create_runner(),
            self.create_secrets(),
        )
