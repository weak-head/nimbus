from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from logdecorator import log_on_end, log_on_error, log_on_start

from nimbuscli.cmd.backup import Backup
from nimbuscli.cmd.command import Command
from nimbuscli.cmd.deploy import Down, Up
from nimbuscli.config import Config
from nimbuscli.core.archive import Archiver, RarArchiver, TarArchiver, ZipArchiver
from nimbuscli.core.execute import SubprocessRunner
from nimbuscli.core.upload import AwsUploader, Uploader
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
        self._profiles = {
            "rar": Config({"provider": "rar", "password": None, "compress": 3, "recovery": 3}),
            "tar": Config({"provider": "tar", "compress": "xz"}),
            "zip": Config({"provider": "zip", "compress": "xz"}),
        }

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
        # Load the archive profile from the app config
        p = self._cfg.first("profiles.archive", lambda x: x.name == profile)

        # Try to load a default profile
        if p is None:
            p = self._profiles.get(profile, None)

        if p is not None:
            match p.provider:
                case "rar":
                    return RarArchiver(SubprocessRunner(), p.password, p.compress, p.recovery)
                case "tar":
                    return TarArchiver(p.compress)
                case "zip":
                    return ZipArchiver(p.compress)

        return None

    @log_on_start(logging.DEBUG, "Creating Uploader: [{profile!s}]")
    @log_on_end(logging.DEBUG, "Created Uploader: {result!r}")
    @log_on_error(logging.ERROR, "Failed to create Uploader: {e!r}", on_exceptions=Exception)
    def create_uploader(self, profile: str) -> Uploader:
        if cfg := self._cfg.first("profiles.upload", lambda x: x.name == profile):
            if cfg.provider == "aws":
                return AwsUploader(
                    cfg.access_key,
                    cfg.secret_key,
                    cfg.bucket,
                    cfg.storage,
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
