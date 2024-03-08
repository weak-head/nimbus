from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from nas.cmd.abstract import Action, ActionResult, Command, MappingActionResult
from nas.core.archiver import ArchivalStatus, Archiver
from nas.core.uploader import Uploader
from nas.provider.abstract import Provider


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(self, destination: str, provider: Provider, archiver: Archiver, uploader: Uploader = None):
        super().__init__("Backup", provider)
        self._destination = destination
        self._archiver = archiver
        self._uploader = uploader

    def _config(self) -> dict[str, Any]:
        return {
            "Destination": self._destination,
            "Upload": bool(self._uploader),
        }

    def _pipeline(self) -> list[Action]:
        pipeline = [
            Action(self._map_resources),
            Action(self._backup),
        ]
        if self._uploader:
            pipeline.append(Action(self._upload))
        return pipeline

    def _backup(self, mapping: MappingActionResult) -> BackupActionResult:
        info = BackupActionResult()

        for group in mapping.entries:
            for directory in group.artifacts:
                backup = BackupEntry(group.name, directory)

                archive_path = self._compose_path(
                    self._destination,
                    backup.group,
                    backup.folder,
                    info.started,
                )

                backup.archive = self._archiver.archive(backup.folder, archive_path)
                info.entries.append(backup)

        info.completed = datetime.now()
        return info

    def _upload(self, backups: BackupActionResult) -> UploadActionResult:
        info = UploadActionResult()

        # implement me

        info.completed = datetime.now()
        return info

    def _compose_path(self, destination: str, group: str, folder: str, today: datetime) -> str:
        suffix = 0
        today_path = today.strftime("%Y-%m-%d")
        archive_name = Path(folder).name
        base_path = os.path.join(destination, group, today_path, archive_name)

        # Don't overwrite the existing backups under the same path.
        # Find the next available name that matches the pattern.
        while True:
            archive_path = base_path + f"_{suffix:02d}.rar" if suffix > 0 else ".rar"
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
    def successful(self) -> bool:
        return self.archive and self.archive.successful


class UploadEntry:

    def __init__(self):
        self.backup: BackupEntry = None


class BackupActionResult(ActionResult[list[BackupEntry]]):
    pass


class UploadActionResult(ActionResult[list[UploadEntry]]):
    pass
