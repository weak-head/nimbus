from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from nas.cmd.abstract import Action, ActionResult, Command
from nas.core.archiver import ArchivalStatus, Archiver
from nas.core.uploader import Uploader
from nas.provider.backup import BackupProvider, BackupResource


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(self, destination: str, provider: BackupProvider, archiver: Archiver, uploader: Uploader = None):
        super().__init__("Backup")
        self._destination = destination
        self._provider = provider
        self._archiver = archiver
        self._uploader = uploader

    def _config(self) -> dict[str, Any]:
        return {
            "Destination": self._destination,
            "Upload": bool(self._uploader),
        }

    def _pipeline(self) -> list[Action]:
        upload = [Action(self._upload)] if self._uploader else []
        return [
            Action(self._map_directories),
            Action(self._backup),
            *upload,
        ]

    def _map_directories(self, arguments: list[str]) -> DirectoryMappingActionResult:
        return DirectoryMappingActionResult(
            self._provider.resolve(arguments),
        )

    def _backup(self, mapping: DirectoryMappingActionResult) -> BackupActionResult:
        result = BackupActionResult([])

        for group in mapping.entries:
            for directory in group.directories:
                backup = BackupEntry(group.name, directory)

                archive_path = self._compose_path(
                    self._destination,
                    backup.group,
                    backup.folder,
                    datetime.now(),
                )

                backup.archive = self._archiver.archive(
                    backup.folder,
                    archive_path,
                )

                result.entries.append(backup)

        return result

    def _upload(self, backups: BackupActionResult) -> UploadActionResult:
        result = UploadActionResult()

        # implement me

        return result

    def _compose_path(self, destination: str, group: str, folder: str, today: datetime) -> str:
        suffix = 0
        today_path = today.strftime("%Y-%m-%d_%H%M")
        archive_name = Path(folder).name
        base_path = os.path.join(destination, group, archive_name, f"{archive_name}_{today_path}")

        # Don't overwrite the existing backups under the same path.
        # Find the next available name that matches the pattern.
        while True:
            archive_path = base_path + (f"_{suffix:02d}.rar" if suffix > 0 else ".rar")
            if os.path.exists(archive_path):
                suffix += 1
            else:
                return archive_path


class BackupEntry:

    def __init__(self, group: str, folder: str):
        self.group: str = group
        self.folder: str = folder
        self.archive: ArchivalStatus = None

    @property
    def success(self) -> bool:
        return self.archive and self.archive.success


class UploadEntry:

    def __init__(self):
        self.backup: BackupEntry = None


class DirectoryMappingActionResult(ActionResult[list[BackupResource]]):
    pass


class BackupActionResult(ActionResult[list[BackupEntry]]):

    @property
    def success(self) -> bool:
        return any(b.success for b in self.entries)


class UploadActionResult(ActionResult[list[UploadEntry]]):
    pass
