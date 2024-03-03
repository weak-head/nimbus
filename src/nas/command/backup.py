from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from nas.command.abstract import Command, CommandInfo
from nas.core.archiver import ArchivalResult, Archiver
from nas.core.provider import Provider, Resources
from nas.core.uploader import Uploader
from nas.report.writer import Writer


class Backup(Command):
    """
    Create and upload backups.
    """

    def __init__(self, path: str, writer: Writer, provider: Provider, archiver: Archiver, uploader: Uploader = None):
        super().__init__(writer, provider)
        self._destination = path
        self._archiver = archiver
        self._uploader = uploader

    def info(self) -> CommandInfo:
        return CommandInfo(
            name="Backup",
            params={
                "Destination": self._destination,
                "Upload": bool(self._uploader),
            },
        )

    def _execute(self, resources: Resources) -> None:
        backups = self._backup(self._destination, resources)
        self._writer.section("Backup").entry(backups)

        if not self._uploader:
            return

        uploads = self._upload(backups)
        self._writer.section("Upload").entry(uploads)

    def _backup(self, destination: str, resources: Resources) -> BackupInfo:
        info = BackupInfo()
        info.started = datetime.now()

        for resource in resources.items:
            for artifact in resource.artifacts:
                entry = BackupEntry(resource.name, artifact)

                archive_path = self._compose_path(
                    destination,
                    entry.group,
                    entry.folder,
                    info.started,
                )

                entry.archive = self._archiver.archive(entry.folder, archive_path)
                info.entries.append(entry)

        info.completed = datetime.now()
        return info

    def _upload(self, backups: BackupInfo) -> UploadInfo:
        info = UploadInfo()
        info.started = datetime.now()

        # TODO: implement me

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
        self.archive: ArchivalResult = None

    @property
    def successful(self) -> bool:
        return self.archive and self.archive.successful


class UploadEntry:

    def __init__(self):
        self.backup: BackupEntry = None


class ActionInfo:

    def __init__(self):
        self.entries: list = []
        self.started: datetime = None
        self.completed: datetime = None

    @property
    def elapsed(self) -> timedelta:
        return self.completed - self.started


class BackupInfo(ActionInfo):
    pass


class UploadInfo(ActionInfo):
    pass
