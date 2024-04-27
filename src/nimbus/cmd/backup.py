from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from logdecorator import log_on_end, log_on_start

from nimbus.cmd.command import Action, ActionResult, Command
from nimbus.core import ArchivalStatus, Archiver, Uploader, UploadProgress, UploadStatus
from nimbus.provider import DirectoryProvider, DirectoryResource


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(
        self,
        selectors: list[str],
        destination: str,
        provider: DirectoryProvider,
        archiver: Archiver,
        uploader: Uploader = None,
    ):
        super().__init__("Backup", selectors)
        self._destination = Path(destination).expanduser().as_posix()
        self._provider = provider
        self._archiver = archiver
        self._uploader = uploader

    def _config(self) -> dict[str, Any]:
        cfg = {
            "Destination": self._destination,
            "Upload": bool(self._uploader),
        }

        if self._uploader:
            cfg |= self._uploader.config()

        return cfg

    @log_on_end(logging.DEBUG, "Pipeline: {result!r}")
    def _pipeline(self) -> list[Action]:
        upload = [Action(self._upload)] if self._uploader else []
        return [
            Action(self._map_directories),
            Action(self._backup),
            *upload,
        ]

    @log_on_end(logging.DEBUG, "Mapped {selectors!r} to {result!s}")
    def _map_directories(self, selectors: list[str]) -> DirectoryMappingActionResult:
        return DirectoryMappingActionResult(
            self._provider.resolve(selectors),
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
        result = UploadActionResult([])

        for backup in filter(lambda e: e.success, backups.entries):
            entry = UploadEntry(backup)

            upload_key = self._compose_upload_key(
                backup.group,
                backup.folder,
                backup.archive.archive,
            )

            entry.upload = self._uploader.upload(
                backup.archive.archive,
                upload_key,
                ProgressTracker(entry),
            )

            result.entries.append(entry)

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

    def _compose_upload_key(self, group: str, directory: str, archive: str) -> str:
        directory_name = Path(directory).name
        archive_name = Path(archive).name
        return os.path.join(group, directory_name, archive_name)


class ProgressTracker:

    def __init__(self, upload: UploadEntry):
        self._upload = upload

    @log_on_start(logging.INFO, "Uploaded progress {progress.progress!s}%")
    def __call__(self, progress: UploadProgress):
        self._upload.progress.append(progress)


class BackupEntry:

    def __init__(self, group: str, folder: str):
        self.group: str = group
        self.folder: str = folder
        self.archive: ArchivalStatus = None

    @property
    def success(self) -> bool:
        return self.archive and self.archive.success


class UploadEntry:

    def __init__(self, backup: BackupEntry = None):
        self.backup: BackupEntry = backup
        self.upload: UploadStatus = None
        self.progress: list[UploadProgress] = []

    @property
    def success(self) -> bool:
        return self.backup and self.backup.success and self.upload and self.upload.success


class DirectoryMappingActionResult(ActionResult[list[DirectoryResource]]):
    pass


class BackupActionResult(ActionResult[list[BackupEntry]]):

    @property
    def success(self) -> bool:
        return any(b.success for b in self.entries)

    @property
    def total_size(self) -> int:
        return sum(entry.archive.size for entry in self.entries if entry.success)


class UploadActionResult(ActionResult[list[UploadEntry]]):

    @property
    def success(self) -> bool:
        return any(e.success for e in self.entries)

    @property
    def total_size(self) -> int:
        return sum(entry.upload.size for entry in self.entries if entry.success)
