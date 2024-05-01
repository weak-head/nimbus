from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbuscli.cmd.backup import Backup
from nimbuscli.cmd.command import Command
from nimbuscli.cmd.deploy import Down, Up
from nimbuscli.config import Config
from nimbuscli.core import Archiver, AwsUploader, RarArchiver, SubprocessRunner, Uploader
from nimbuscli.provider import (
    DirectoryProvider,
    Secrets,
    SecretsProvider,
    ServiceFactory,
    ServiceProvider,
)


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

    def __init__(self, config: Config) -> None:
        self._cfg = config

    @log_on_start(logging.DEBUG, "Creating Backup command")
    @log_on_error(logging.ERROR, "Failed to create Backup command: {e!r}", on_exceptions=Exception)
    def create_backup(self, selectors: list[str]) -> Command:
        cfg = self._cfg.commands.backup
        return Backup(
            selectors,
            cfg.destination,
            DirectoryProvider(cfg.directories),
            self.create_archiver(cfg.archive),
            self.create_uploader(cfg.upload),
        )

    @log_on_start(logging.DEBUG, "Creating Up command")
    @log_on_error(logging.ERROR, "Failed to create Up command: {e!r}", on_exceptions=Exception)
    def create_up(self, selectors: list[str]) -> Command:
        return Up(
            selectors,
            self.create_service_provider(),
            self.create_service_factory(),
        )

    @log_on_start(logging.DEBUG, "Creating Down command")
    @log_on_error(logging.ERROR, "Failed to create Down command: {e!r}", on_exceptions=Exception)
    def create_down(self, selectors: list[str]) -> Command:
        return Down(
            selectors,
            self.create_service_provider(),
            self.create_service_factory(),
        )

    @log_on_start(logging.DEBUG, "Creating Archiver: [{profile!s}]")
    @log_on_end(logging.DEBUG, "Created Archiver: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Archiver: {e!r}", on_exceptions=Exception)
    def create_archiver(self, profile: str) -> Archiver:
        if cfg := CfgCommandFactory._profile(self._cfg.profiles.archive, profile):
            if cfg.provider == "rar":
                return RarArchiver(
                    SubprocessRunner(),
                    cfg.password,
                    cfg.compression,
                    cfg.recovery,
                )

        return None

    @log_on_start(logging.DEBUG, "Creating Uploader: [{profile!s}]")
    @log_on_end(logging.DEBUG, "Created Uploader: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Uploader: {e!r}", on_exceptions=Exception)
    def create_uploader(self, profile: str) -> Uploader:
        if cfg := CfgCommandFactory._profile(self._cfg.profiles.upload, profile):
            if cfg.provider == "aws":
                return AwsUploader(
                    cfg.access_key,
                    cfg.secret_key,
                    cfg.bucket,
                    cfg.storage_class,
                )

        return None

    @log_on_start(logging.DEBUG, "Creating Service Provider")
    @log_on_end(logging.DEBUG, "Created Service Provider: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service Provider: {e!r}", on_exceptions=Exception)
    def create_service_provider(self) -> ServiceProvider:
        return ServiceProvider(self._cfg.commands.deploy.services)

    @log_on_start(logging.DEBUG, "Creating Service Factory")
    @log_on_end(logging.DEBUG, "Created Service Factory: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Service Factory: {e!r}", on_exceptions=Exception)
    def create_service_factory(self) -> ServiceFactory:
        return ServiceFactory(
            SubprocessRunner(),
            Secrets(SecretsProvider(self._cfg.commands.deploy.secrets)),
        )

    @staticmethod
    def _profile(profiles: list[Config], name: str) -> Config | None:
        if cfg := [c for c in profiles if c.name == name]:
            return cfg[0]
        return None
